"""A compact locus map in the style of the coursework's guide-context figures."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator


def locus_figure(result):
    table, gene = result["table"], result["gene"]
    left, right = result["view"]
    placed = table[table.status == "placed"]
    count = max(1, len(placed))
    centre = (placed.start.min() + placed.end.max() - 2) / 2 if len(placed) else (left + right) / 2
    origin = min(result["tss"], key=lambda t: abs(t - centre))
    direction = 1 if gene["strand"] == "+" else -1
    colours = ["tab:blue", "tab:red", "tab:green", "tab:purple"]
    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(9.5, 5.5 + count * 0.35),
                             gridspec_kw={"height_ratios": [1, 1, 1, 1, 1.3 + count * 0.55]},
                             layout="constrained")
    promoters = [(max(left, a), min(right, b) - max(left, a)) for a, b in result["promoters"]
                 if a < right and b > left]
    for ax in axes:
        for start, width in promoters:
            ax.axvspan(start, start + width, color="0.94", zorder=0)
        ax.axvline(origin, color="black", linewidth=0.7, linestyle="--")
        ax.set_yticks([])
        # Keep genomic coordinates internally; reverse only the view on minus-strand genes.
        ax.set_xlim((left, right) if direction == 1 else (right, left))
        ax.tick_params(labelsize=8)
        for spine in ax.spines.values():
            spine.set_linewidth(0.7)
    for ax, (key, peaks) in zip(axes[:4], result["tracks"].items()):
        visible = peaks[(peaks.start < right) & (peaks.end > left)]
        intervals = [(max(left, a), min(right, b) - max(left, a)) for a, b in visible.itertuples(index=False, name=None)]
        ax.broken_barh(intervals, (0.08, 0.65), facecolors="0.45")
        if not intervals:
            ax.text(0.5, 0.45, "No called peaks in this view", transform=ax.transAxes,
                    ha="center", va="center", color="0.45", fontsize=8)
        ax.set(ylabel=f"K562 {key}\ncalled peaks", ylim=(0, 1))
        ax.yaxis.label.set_size(8)
    ax = axes[-1]
    ax.broken_barh(promoters, (count + 1.05, 0.22), facecolors="0.75")
    ax.text(0.01, count + 1.16, "Configured TSS windows", transform=ax.get_yaxis_transform(),
            va="center", fontsize=7, color="0.15")
    genes = result["annotations"]
    genes = genes[(genes.kind == "gene") & (genes.chrom == gene["chrom"]) &
                  (genes.start < right) & (genes.end > left)]
    for index, row in enumerate(genes.itertuples()):
        start, end = max(left, row.start), min(right, row.end)
        y = count + 0.1 + (index % 2) * 0.38
        colour = "tab:blue" if row.gene == gene["gene"] else "0.5"
        a, b = (start, end) if row.strand == "+" else (end, start)
        ax.annotate("", xy=(b, y), xytext=(a, y), arrowprops=dict(arrowstyle="->", color=colour, linewidth=0.8))
        ax.text((start + end) / 2, y + 0.1, row.gene, ha="center", fontsize=7, color=colour)
    for index, row in enumerate(placed.itertuples()):
        y, start = count - index - 1, row.start - 1
        colour = colours[(int(row.guide[1:]) - 1) % len(colours)]
        ax.broken_barh([(start, 20)], (y - 0.27, 0.54), facecolors=colour, edgecolors="black", linewidth=0.5)
        pam_start = row.end if row.strand == "+" else start - 3
        ax.broken_barh([(pam_start, 3)], (y - 0.27, 0.54), facecolors="black", edgecolors="white", linewidth=0.5)
        ax.text(0.01, y, f"{row.guide} ({row.strand})", transform=ax.get_yaxis_transform(),
                va="center", fontsize=9, weight="bold", color=colour)
        offset = direction * ((row.start + row.end - 2) / 2 - origin)
        ax.text(0.99, y, f"offset {offset:+.1f} bp", transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=8)
    if placed.empty:
        ax.text(0.5, 0, "No unambiguous local placement", transform=ax.get_yaxis_transform(), ha="center", fontsize=9)
    ax.set_ylim(-0.65, count + 1.5)
    offsets = MaxNLocator(nbins=6).tick_values(left - origin, right - origin)
    ax.set_xticks([origin + x for x in offsets if left <= origin + x <= right])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{round(direction * (x - origin)):,}"))
    ax.set_xlabel("Offset from the selected GENCODE TSS (bp; downstream +)\n"
                  "Grey strip / shading: configured TSS windows (not promoter/enhancer calls)", fontsize=8)
    fig.suptitle(f"{gene['gene']} · K562 · GRCh38 · {gene['strand']} strand\n"
                 f"TSS {gene['chrom']}:{origin + 1:,} · guide colours identify inputs; black tips mark PAMs", fontsize=10)
    for extension in ["png", "svg"]:
        fig.savefig(result["output"] / f"locus.{extension}", dpi=160)
    return fig
