"""Read GENCODE v32 and GRCh38 for one locus, in zero-based, half-open coordinates."""

import re
from urllib.parse import urlencode

import pandas as pd

from .cache import query_path
from .data import SETTINGS, SOURCES

REGIONS = SOURCES["regions"]
PRIMARY = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY"}


def ucsc_url(endpoint, params):
    return f"{SOURCES['ucsc_api']}/{endpoint}?" + urlencode(dict(genome="hg38", **params))


def ucsc(inputs, key, endpoint, field, limit, **params):
    return inputs.json(key, REGIONS[key], ucsc_url(endpoint, params), field, limit, dict(genome="hg38", **params))


def gene_anchor(groups, stable_id):
    # UCSC search positions are 1-based. One transcript base locates the original gene record.
    anchors = {}
    for group in groups:
        for hit in group["matches"]:
            gid = hit["posName"]
            chrom, span = hit["position"].split(":")
            if gid.split(".")[0] == stable_id and chrom in PRIMARY:
                anchors[gid, chrom] = int(span.split("-")[0].replace(",", "")) - 1
    if len(anchors) != 1:
        raise ValueError(f"Expected one GENCODE v32 locus for {stable_id}; found {len(anchors)}.")
    (gid, chrom), pos = anchors.popitem()
    return gid, chrom, pos


def annotation(inputs, chrom, left, right):
    source = REGIONS["annotation"]
    root = source["url"].format(chrom=chrom)
    params = dict(chrom=chrom, start=left, end=right)
    def read(file, field=None):
        return inputs.json("annotation", source, root + file, field, 5_000_000, params)

    index = read("trackData.jsonz", "intervals")
    def fields(row):
        return dict(zip(index["classes"][row[0]]["attributes"], row[1:]))

    def genes(rows):
        for row in rows:
            item = fields(row)
            if item["Start"] >= right or item["End"] <= left:
                continue
            if row[0] == index["lazyClass"]:
                chunk = index["urlTemplate"].replace("{Chunk}", str(item["Chunk"]))
                yield from genes(read(chunk))
            elif item.get("Type") == "gene":
                gene = dict(gene=item["Gene_name"], gene_id=item["Gene_id"], chrom=chrom,
                            start=item["Start"], end=item["End"], strand="+" if item["Strand"] == 1 else "-", kind="gene")
                transcripts = map(fields, item.get("Subfeatures", []))
                tss = set()
                for tx in transcripts:
                    tags = tx.get("Tag", [])
                    if tx.get("Type") == "transcript" and (tags == "basic" or isinstance(tags, list) and "basic" in tags):
                        tss.add(tx["Start"] if gene["strand"] == "+" else tx["End"] - 1)
                if tss:
                    yield gene, sorted(tss)
            # Overlapping genes can be nested independently of biological parentage.
            if isinstance(row[-1], dict):
                yield from genes(row[-1].get("Sublist", []))
    return list(genes(index["nclist"]))


def find_gene(name, inputs):
    name = name.strip().upper()
    stable_id = name
    if not re.fullmatch(r"ENSG\d{11}", name):
        source = REGIONS["lookup"]
        body = dict(organism="hsapiens", target="ENSG", query=[name])
        rows = inputs.json("lookup", source, source["url"], "result", 32_000, body, body)
        ids = {r["converted"] for r in rows if (r["name"] or "").upper() == name and r["converted"].startswith("ENSG")}
        if len(ids) != 1:
            raise ValueError(f"Expected one Ensembl 98 ID for {name!r}; found {len(ids)}. Use its Ensembl gene ID.")
        stable_id = ids.pop()
    source = REGIONS["position"]
    groups = ucsc(inputs, "position", "search", "positionMatches", 600_000,
                  search=stable_id, categories=",".join(source["tracks"]))
    gid, chrom, pos = gene_anchor(groups, stable_id)
    matches = [(g, tss) for g, tss in annotation(inputs, chrom, pos, pos + 1)
               if g["gene_id"] == gid and (name == stable_id or g["gene"].upper() == name)]
    if len(matches) != 1:
        raise ValueError(f"Expected one matching GENCODE v32 basic gene for {name!r}; found {len(matches)}.")
    return matches[0]


def read_dna(gene, inputs):
    sizes = ucsc(inputs, "reference", "list/chromosomes", "chromosomes", 32_000)
    chrom = gene["chrom"]
    left = max(0, gene["start"] - SETTINGS["search_flank"])
    right = min(sizes[chrom], gene["end"] + SETTINGS["search_flank"])
    if right - left > 3_000_000:
        raise ValueError(f"{chrom}:{left}-{right} exceeds the 3 Mb search limit.")
    dna = ucsc(inputs, "reference", "getData/sequence", "dna", right - left + 1024, chrom=chrom, start=left, end=right)
    flank = max(3, SETTINGS["plot_flank"])
    return dna.upper(), left, (max(0, left - flank), min(sizes[chrom], right + flank))


def read_context(chrom, interval, whole, inputs):
    left, right = max(whole[0], interval[0]), min(whole[1], interval[1])
    genes = [g for g, _ in annotation(inputs, chrom, left, right)]
    neighbors = pd.DataFrame(genes, columns=["gene", "strand", "start", "end"]).sort_values("start", kind="stable")
    track = REGIONS["ccre"]["track"]
    params = dict(track=track, chrom=chrom, start=left, end=right)
    broad = dict(params, start=whole[0], end=whole[1])
    # An explicit --download can also supply cCREs for any custom guide set.
    if not query_path(ucsc_url("getData/track", params)).exists() and query_path(ucsc_url("getData/track", broad)).exists():
        params = broad
    rows = ucsc(inputs, "ccre", "getData/track", track, 4_000_000, **params)
    ccres = pd.DataFrame(rows, columns=["chrom", "chromStart", "chromEnd", "name", "cCRE_class"])
    ccres.columns = ["chrom", "start", "end", "accession", "cCRE_class"]
    return neighbors, ccres[(ccres.start < right) & (ccres.end > left)]
