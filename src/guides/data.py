"""Pinned peak files, the guide library and analysis settings."""

import json
import re
import tomllib

import pandas as pd

from .cache import ROOT

SOURCES = json.loads((ROOT / "metadata/sources.json").read_text())
SETTINGS = tomllib.loads((ROOT / "config/settings.toml").read_text())


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


def read_peaks(path, chrom):
    peaks = pd.read_csv(path, sep="\t", header=None, usecols=[0, 1, 2],
                        names=["chrom", "start", "end"])
    return peaks.loc[peaks.chrom == chrom, ["start", "end"]].sort_values("start")
