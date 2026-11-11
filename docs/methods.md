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
half-open** coordinates. Human-facing `guides.csv` spacer starts and ends use
**1-based, inclusive** coordinates. Distances are base-pair
differences; spacer-midpoint distances may end in .5. CTCF gap zero means
overlapping or touching intervals; `CTCF_bp` distinguishes overlap from touching.

The figure's origin is the annotated target-gene TSS nearest the midpoint of
the placed-guide span (or the view midpoint when none are placed). Its 1-based
genomic position appears in the title. The axis shows offsets in the target
gene's direction, so downstream is always to the right; a minus-strand gene
has decreasing genomic coordinates from left to right. Figure offsets refer
to this one displayed TSS, whereas the table uses each guide's nearest TSS.
The gene arrows show transcription direction. Guides have separate rows;
their colours and numbers identify inputs, not knockdown or efficacy ranks.

The compact tracks, grey background windows, black PAM tips and lower guide
panel follow the visual layout of the author's coursework notebook 01.6.
Here, grey bars show called peak intervals and orange bars show the defined
promoter windows. They do not reproduce that notebook's bigWig signal curves,
measured knockdown colours, cCRE strip or CRISPick design windows.

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
