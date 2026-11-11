"""A small genomic-track figure built with Matplotlib."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def locus_figure(result):
    table, gene = result["table"], result["gene"]
    left, right = result["view"]
    placed = table[table.status == "placed"]
    colours = {"DNase": "#188977", "H3K4me3": "#dc8b26", "H3K27ac": "#9856a6", "CTCF": "#3979aa"}
    height = max(1.3, 0.35 * len(placed))
    fig, axes = plt.subplots(7, 1, sharex=True, figsize=(11, 6.8 + height),
                             gridspec_kw={"height_ratios": [1, 0.7, height, 0.7, 0.7, 0.7, 0.7]},
                             layout="constrained")
    genes = result["annotations"]
    genes = genes[(genes.kind == "gene") & (genes.chrom == gene["chrom"]) &
                  (genes.start < right) & (genes.end > left)]
    for index, row in enumerate(genes.itertuples()):
        y = index % 3
        start, end = max(left, row.start), min(right, row.end)
        colour = "#172b3a" if row.gene == gene["gene"] else "#969da5"
        a, b = (start, end) if row.strand == "+" else (end, start)
        axes[0].annotate("", xy=(b, y), xytext=(a, y), arrowprops=dict(arrowstyle="->", color=colour))
        axes[0].text((start + end) / 2, y + 0.16, row.gene, ha="center", fontsize=8, color=colour)
    axes[0].set(ylim=(-0.4, 3), ylabel="Genes")
    promoters = [(max(left, a), min(right, b) - max(left, a)) for a, b in result["promoters"]
                 if a < right and b > left]
    axes[1].broken_barh(promoters, (0.2, 0.6), facecolors="#efbd78", alpha=0.55)
    for tss in result["tss"]:
        if left <= tss < right:
            axes[1].axvline(tss, color="#a8631b", linewidth=1)
    axes[1].set(ylabel="Target\npromoters", ylim=(0, 1))
    for index, row in enumerate(placed.itertuples()):
        index = len(placed) - index - 1
        start = row.start - 1
        axes[2].broken_barh([(start, 20)], (index - 0.25, 0.5), facecolors="#b74442")
        pam_start = row.end if row.strand == "+" else start - 3
        axes[2].broken_barh([(pam_start, 3)], (index - 0.25, 0.5), facecolors="#172b3a")
        axes[2].text(start + 10, index + 0.31, f"{row.guide} ({row.strand})", fontsize=8, ha="center")
    if placed.empty:
        axes[2].text(0.5, 0.5, "No unambiguous local placement", transform=axes[2].transAxes, ha="center")
    axes[2].set(ylabel="Guides\n+ PAM", ylim=(-0.6, max(1, len(placed)) - 0.2))
    for ax, (key, peaks) in zip(axes[3:], result["tracks"].items()):
        visible = peaks[(peaks.start < right) & (peaks.end > left)]
        intervals = [(max(left, a), min(right, b) - max(left, a)) for a, b in visible.itertuples(index=False, name=None)]
        ax.broken_barh(intervals, (0.2, 0.6), facecolors=colours[key])
        if not intervals:
            ax.text(0.5, 0.5, "No called peaks in this view", transform=ax.transAxes, ha="center", color="#777777", fontsize=8)
        ax.set(ylabel=key, ylim=(0, 1))
    for ax in axes:
        ax.set_yticks([])
        ax.set_xlim(left, right)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.grid(axis="x", color="#edf0f2", linewidth=0.6)
    axes[-1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x) + 1:,}"))
    axes[-1].set_xlabel(f"{gene['chrom']} · GRCh38 · genomic position (1-based; increasing left to right)")
    fig.suptitle(f"{gene['gene']} · CRISPRi guides and K562 peak annotations", fontsize=15, fontweight="bold")
    for extension in ["png", "svg"]:
        fig.savefig(result["output"] / f"locus.{extension}", dpi=160)
    return fig
