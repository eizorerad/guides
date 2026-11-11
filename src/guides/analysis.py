"""Exact local placement and interval measurements; no efficacy prediction."""

import json

import pandas as pd

from .data import (ROOT, SETTINGS, SOURCES, checksum, library_guides,
                   prepare, read_peaks, read_sequence, validate_guides)


def reverse_complement(sequence):
    return sequence.translate(str.maketrans("ACGTN", "TGCAN"))[::-1]


def find_matches(sequence, spacer, offset=0):
    matches = []
    for strand, query in [("+", spacer), ("-", reverse_complement(spacer))]:
        position = sequence.find(query)
        while position != -1:
            pam = (sequence[position + 20:position + 23] if strand == "+" else
                   reverse_complement(sequence[max(0, position - 3):position]))
            if len(pam) == 3 and pam.endswith("GG") and set(pam) <= set("ACGT"):
                matches.append(dict(start=position + offset, end=position + offset + 20,
                                    strand=strand, pam=pam))
            position = sequence.find(query, position + 1)
    return matches


def overlap_bp(intervals, start, end):
    # Merge clipped overlaps so overlapping peaks never count a base twice.
    total, previous_end = 0, start
    for left, right in sorted(intervals):
        left, right = max(left, start), min(right, end)
        total += max(0, right - max(left, previous_end))
        previous_end = max(previous_end, right)
    return total


def interval_distance(intervals, start, end):
    return min((max(left - end, start - right, 0) for left, right in intervals), default=None)


def analyse(request):
    inputs, annotations, gene = prepare(request["gene"])
    sequences = request["sequences"]
    if sequences is None:
        sequences = library_guides(inputs["library"], gene["gene"])
    sequences = validate_guides(sequences)
    search_start = max(0, gene["start"] - SETTINGS["search_flank"])
    search_end = gene["end"] + SETTINGS["search_flank"]
    sequence = read_sequence(inputs["reference"], search_start, search_end)
    search_end = search_start + len(sequence)
    transcripts = annotations[(annotations.gene_id == gene["gene_id"]) &
                              (annotations.kind == "transcript")]
    tss = sorted(set(transcripts.start if gene["strand"] == "+" else transcripts.end - 1))
    upstream, downstream = SETTINGS["promoter_upstream"], SETTINGS["promoter_downstream"]
    promoters = [(t - upstream, t + downstream + 1) if gene["strand"] == "+" else
                 (t - downstream, t + upstream + 1) for t in tss]
    tracks = {key: read_peaks(inputs[key], gene["chrom"]) for key in SOURCES["tracks"]}
    rows, alternatives = [], []
    for index, spacer in enumerate(sequences, 1):
        label = f"g{index}"
        matches = find_matches(sequence, spacer, search_start)
        status = "placed" if len(matches) == 1 else "not found" if not matches else "ambiguous"
        row = dict(guide=label, sequence=spacer, status=status, matches=len(matches))
        alternatives.extend(dict(guide=label, **match) for match in matches)
        if len(matches) == 1:
            match = matches[0]
            start, end = match["start"], match["end"]
            midpoint = (start + end - 1) / 2
            nearest_tss = min(tss, key=lambda t: abs(t - midpoint))
            footprint = (start, end + 3) if match["strand"] == "+" else (start - 3, end)
            row.update(chrom=gene["chrom"], start=start + 1, end=end,
                       strand=match["strand"], pam=match["pam"],
                       tss=nearest_tss + 1,
                       tss_distance_bp=(midpoint - nearest_tss) * (1 if gene["strand"] == "+" else -1),
                       promoter_bp=overlap_bp(promoters, *footprint))
            for key, peaks in tracks.items():
                intervals = list(peaks.itertuples(index=False, name=None))
                row[f"{key}_bp"] = overlap_bp(intervals, *footprint)
                if key == "CTCF":
                    row["nearest_CTCF_bp"] = interval_distance(intervals, *footprint)
        rows.append(row)
    columns = ["guide", "sequence", "status", "matches", "chrom", "start", "end", "strand", "pam",
               "tss", "tss_distance_bp", "promoter_bp", *[f"{k}_bp" for k in tracks], "nearest_CTCF_bp"]
    table = pd.DataFrame(rows).reindex(columns=columns)
    placed = table[table.status == "placed"]
    centre = gene["start"] if gene["strand"] == "+" else gene["end"] - 1
    left = int(placed.start.min()) - 1 if len(placed) else centre
    right = int(placed.end.max()) if len(placed) else centre + 1
    view = (max(0, left - SETTINGS["plot_flank"]), right + SETTINGS["plot_flank"])
    output = ROOT / "results" / request["name"]
    output.mkdir(parents=True, exist_ok=True)
    table.to_csv(output / "guides.csv", index=False)
    pd.DataFrame(alternatives, columns=["guide", "start", "end", "strand", "pam"]).to_csv(
        output / "placements.csv", index=False)
    used_sources = []
    for key, path in inputs.items():
        source = SOURCES["chromosomes"][gene["chrom"]] if key == "reference" else SOURCES["files"][key]
        used_sources.append(dict(source, key=key, sha256=checksum(path, "sha256")))
    manifest = dict(request=request, settings=SETTINGS, gene=gene,
                    search_interval=[search_start, search_end], plot_interval=list(view), sources=used_sources,
                    environment_sha256=checksum(ROOT / "pixi.lock", "sha256"))
    (output / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return dict(table=table, gene=gene, annotations=annotations, tss=tss, promoters=promoters,
                tracks=tracks, view=view, output=output, manifest=manifest)
