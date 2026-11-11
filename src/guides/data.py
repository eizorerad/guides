"""Download reference files and read genes, guides, peaks and cCRE intervals."""

import gzip
import hashlib
import json
import re
import time
import tomllib
from pathlib import Path

import pandas as pd
import pyBigWig
import requests

ROOT = Path(__file__).resolve().parents[2]
SOURCES = json.loads((ROOT / "metadata/sources.json").read_text())
SETTINGS = tomllib.loads((ROOT / "config/settings.toml").read_text())
PRIMARY = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY"}


def checksum(path, algorithm="md5"):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, algorithm).hexdigest()


def download(source):
    path = ROOT / "data/raw" / source["filename"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        print(f"Downloading {path.name} …", flush=True)
        partial = path.with_suffix(path.suffix + ".part")
        for attempt in range(3):
            try:
                with requests.get(source["url"], stream=True, timeout=90,
                                  headers={"User-Agent": "guides/0.1 (academic research)"}) as response:
                    response.raise_for_status()
                    with partial.open("wb") as handle:
                        for chunk in response.iter_content(1024 * 1024):
                            handle.write(chunk)
                if checksum(partial) != source["md5"]:
                    raise ValueError(f"Checksum mismatch: {path.name}")
                partial.rename(path)
                path.chmod(0o444)
                break
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(2)
    if checksum(path) != source["md5"]:
        raise ValueError(f"Changed raw file: {path}. Remove it and download again.")
    return path


def annotation(path):
    rows = []
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            chrom, _, kind, start, end, _, strand, _, attributes = line.rstrip().split("\t")
            if chrom not in PRIMARY or kind not in {"gene", "transcript"}:
                continue
            attrs = dict(re.findall(r'(\w+) "([^"]+)"', attributes))
            rows.append((attrs["gene_name"], attrs["gene_id"], chrom,
                         int(start) - 1, int(end), strand, kind))
    return pd.DataFrame(rows, columns=["gene", "gene_id", "chrom", "start", "end", "strand", "kind"])


def select_gene(annotations, name):
    genes = annotations[annotations.kind == "gene"]
    chosen = genes[(genes.gene.str.upper() == name.upper()) |
                   (genes.gene_id.str.split(".").str[0] == name.upper())]
    if len(chosen) != 1:
        raise ValueError(f"Expected one gene in GENCODE v32, found {len(chosen)} for {name!r}. "
                         "Use its exact symbol or Ensembl gene ID.")
    return chosen.iloc[0].to_dict()


def library_guides(path, gene):
    table = pd.read_csv(path, sep="\t")
    sequences = table.loc[table["Annotated Gene Symbol"] == gene, "Barcode Sequence"]
    sequences = sequences.drop_duplicates().tolist()
    if not sequences:
        raise ValueError(f"No Dolcetto Set A guides for {gene}. Use the custom-guide mode.")
    return sequences


def validate_guides(sequences):
    sequences = [s.strip().upper() for s in sequences if s.strip()]
    if not sequences or any(not re.fullmatch("[ACGT]{20}", s) for s in sequences):
        raise ValueError("Enter one 20-letter DNA spacer per line (A, C, G, T), without PAM or adapters.")
    return sequences


def read_sequence(path, start, end):
    # Read only the requested part; the downloaded chromosome remains unchanged.
    pieces, position = [], 0
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if line.startswith(">"):
                continue
            line = line.strip()
            next_position = position + len(line)
            if next_position > start and position < end:
                pieces.append(line[max(0, start - position):end - position])
            position = next_position
            if position >= end:
                break
    return "".join(pieces).upper()


def prepare(name):
    inputs = {key: download(value) for key, value in SOURCES["files"].items()}
    annotations = annotation(inputs["annotation"])
    gene = select_gene(annotations, name)
    inputs["reference"] = download(SOURCES["chromosomes"][gene["chrom"]])
    return inputs, annotations, gene


def read_peaks(path, chrom):
    peaks = pd.read_csv(path, sep="\t", header=None, usecols=[0, 1, 2],
                        names=["chrom", "start", "end"])
    return peaks.loc[peaks.chrom == chrom, ["start", "end"]].sort_values("start")


def read_ccres(path, chrom, start, end):
    with pyBigWig.open(str(path)) as source:
        length = source.chroms().get(chrom, 0)
        entries = (source.entries(chrom, start, min(end, length)) or []) if start < length else []
    rows = []
    for left, right, rest in entries:
        fields = rest.split("\t")  # Fixed UCSC bigBed 9+5 schema: name and cCRE_class.
        rows.append((chrom, left, right, fields[0], fields[6]))
    return pd.DataFrame(rows, columns=["chrom", "start", "end", "accession", "cCRE_class"])
