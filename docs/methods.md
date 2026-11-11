# What the program does

1. Download the fixed Dolcetto, GENCODE and ENCODE files. Select one exact gene
   symbol or Ensembl gene ID from GENCODE v32 on chr1–22, X or Y.
2. Download that chromosome's UCSC GRCh38 FASTA file. Search the annotated gene
   span plus the flanks in `config/settings.toml`.
3. Find exact 20-base spacer matches on both strands. Accept only sites with
   an NGG PAM in the spacer's orientation. The minus-strand PAM is upstream
   on the reference, and its displayed sequence is reverse-complemented.
4. If one site matches, measure the 23-base spacer-plus-PAM footprint against
   the union of each peak track. No match and multiple matches are separate
   statuses; neither is silently assigned a location.
5. Find the nearest annotated target-gene transcript start to the spacer's
   midpoint. Report the signed distance in the target gene's orientation.
   Promoter intervals are a stated window around *all* its basic transcript
   starts, not an experimentally established active promoter.
6. Recompute the table, descriptive counts and locus figure inside Quarto.

Internal intervals, GTF conversion and `placements.csv` use **0-based,
half-open** coordinates. Human-facing `guides.csv` spacer starts and ends and
the figure axis use **1-based, inclusive** coordinates. Distances are base-pair
differences; spacer-midpoint distances may end in .5. CTCF gap zero means
overlapping or touching intervals; `CTCF_bp` distinguishes overlap from touching.

The figure preserves increasing genomic coordinates on both strands. The
gene arrow gives transcription direction. Guides are displayed on separate
rows so nearby or overlapping spacers remain visible. Guide numbers follow
input/catalogue order and are not design scores or efficacy ranks.

Only peak *intervals* are drawn. No peak height, motif, knockdown or off-target
measurement is fabricated. All four ENCODE tracks are required inputs; failed
downloads stop the report instead of being treated as absent biological signal.
These are reference K562 experiments, not measurements in the user's cells.

The local exact-match search does not evaluate genome-wide uniqueness,
mismatches, bulges, non-NGG PAMs, individual genetic variants or alternative
contigs. A library gene name can be outdated; the program asks for an exact
GENCODE symbol/ID and does not silently substitute a different gene.

## Reading the code

- `src/guides/__main__.py`: menu, arguments and Quarto invocation.
- `src/guides/data.py`: downloads and plain-text input parsing.
- `src/guides/analysis.py`: exact placement and interval arithmetic.
- `src/guides/plot.py`: one Matplotlib figure.
- `reports/report.qmd`: the executable scientific report.

The few synthetic tests target strand/PAM coordinates, ambiguous placement
and overlapping intervals. They do not validate biological efficacy.
