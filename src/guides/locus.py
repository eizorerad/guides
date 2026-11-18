"""Read GENCODE v32 and GRCh38 for one locus, in zero-based, half-open coordinates."""

import re
from urllib.parse import urlencode

import pandas as pd

from .cache import query_path
from .data import SETTINGS, SOURCES

REGIONS = SOURCES["regions"]
PRIMARY = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY"}


def ucsc(inputs, key, endpoint, field, limit, *, cached_interval=None, **params):
    base = f"{SOURCES['ucsc_api']}/{endpoint}?"
    query = dict(genome="hg38", **params)
    if cached_interval:
        broad = dict(query, start=cached_interval[0], end=cached_interval[1])
        cached = (p for p in (query, broad) if query_path(base + urlencode(p)).is_file())
        query = next(cached, query)
    return inputs.json(key, REGIONS[key], base + urlencode(query), field, limit, query)


def only(items, description):
    if len(items) != 1:
        raise ValueError(f"Expected one {description}; found {len(items)}.")
    return next(iter(items))


def gene_anchor(groups, stable_id):
    # UCSC search positions are 1-based. One transcript base locates the original gene record.
    anchors = {}
    for group in groups:
        for hit in group["matches"]:
            gid = hit["posName"]
            chrom, span = hit["position"].split(":")
            if gid.split(".")[0] == stable_id and chrom in PRIMARY:
                start = int(span.split("-")[0].replace(",", "")) - 1
                anchors[gid, chrom] = (gid, chrom, start)
    return only(anchors.values(), f"GENCODE v32 locus for {stable_id}")


def annotation(inputs, chrom, left, right):
    source = REGIONS["annotation"]
    params = dict(chrom=chrom, start=left, end=right)
    def read(file, field=None):
        return inputs.json("annotation", source, source["url"].format(chrom=chrom) + file, field, 5_000_000, params)

    index = read("trackData.jsonz", "intervals")
    def fields(row):
        return dict(zip(index["classes"][row[0]]["attributes"], row[1:]))

    def overlapping(rows):
        for row in rows:
            item = fields(row)
            if item["Start"] >= right or item["End"] <= left:
                continue
            if row[0] == index["lazyClass"]:
                yield from overlapping(read(index["urlTemplate"].format_map(item)))
            elif item.get("Type") == "gene":
                yield item
            # The index can nest independent genes in a Sublist.
            if isinstance(row[-1], dict):
                yield from overlapping(row[-1].get("Sublist", []))

    genes = []
    for item in overlapping(index["nclist"]):
        plus = item["Strand"] == 1
        tss = set()
        for tx in map(fields, item.get("Subfeatures", [])):
            tags = tx.get("Tag")
            basic = "basic" in tags if isinstance(tags, list) else tags == "basic"
            if tx.get("Type") == "transcript" and basic:
                tss.add(tx["Start"] if plus else tx["End"] - 1)
        if tss:
            gene = dict(gene=item["Gene_name"], gene_id=item["Gene_id"], chrom=chrom,
                        start=item["Start"], end=item["End"], strand="+" if plus else "-", kind="gene")
            genes.append((gene, sorted(tss)))
    return genes


def find_gene(name, inputs):
    name = name.strip().upper()
    stable_id = name
    if not re.fullmatch(r"ENSG\d{11}", name):
        source = REGIONS["lookup"]
        body = dict(organism="hsapiens", target="ENSG", query=[name])
        rows = inputs.json("lookup", source, source["url"], "result", 32_000, body, body)
        ids = {r["converted"] for r in rows if (r["name"] or "").upper() == name and r["converted"].startswith("ENSG")}
        stable_id = only(ids, f"Ensembl 98 ID for {name!r} (try its Ensembl gene ID)")
    groups = ucsc(inputs, "position", "search", "positionMatches", 600_000,
                  search=stable_id, categories=",".join(REGIONS["position"]["tracks"]))
    gid, chrom, pos = gene_anchor(groups, stable_id)
    matches = [(g, tss) for g, tss in annotation(inputs, chrom, pos, pos + 1)
               if g["gene_id"] == gid and (name == stable_id or g["gene"].upper() == name)]
    return only(matches, f"matching GENCODE v32 basic gene for {name!r}")


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
    # --download may already have cached the full locus for custom guides.
    rows = ucsc(inputs, "ccre", "getData/track", track, 4_000_000,
                track=track, chrom=chrom, start=left, end=right, cached_interval=whole)
    ccres = pd.DataFrame(rows, columns=["chrom", "chromStart", "chromEnd", "name", "cCRE_class"])
    ccres.columns = ["chrom", "start", "end", "accession", "cCRE_class"]
    return neighbors, ccres[(ccres.start < right) & (ccres.end > left)]
