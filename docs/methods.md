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
   The configured windows surround *all* its basic transcript starts; they
   are not experimentally established active promoters. The existing column
   `promoter_bp` records overlap with those windows and keeps its name for
   compatibility with scripts.
6. Read ENCODE4 K562 cCREs covering the figure and placed guide footprints
   from the pinned BigBed file, using pyBigWig. Keep source IDs, full boundaries
   and biosample-specific class labels. Measure footprint overlap with the
   union of promoter-like and enhancer-like elements separately.
7. Recompute the tables, descriptive counts and locus figure inside Quarto.

Internal intervals, GTF conversion, `ccres.csv` and `placements.csv` use **0-based,
half-open** coordinates. Human-facing `guides.csv` spacer starts and ends use
**1-based, inclusive** coordinates, as does the report's cCRE table. Distances are base-pair
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
Here, the upper grey bars show called peaks, and the labelled lower grey strip
shows the configured TSS windows. A separate cCRE track uses the provider's
red for promoter-like, orange for proximal enhancer-like and yellow for distal
enhancer-like elements. Other classes, including Low-DNase, are grouped in grey
in the figure; their exact labels remain in the tables. Element boundaries are
clipped only for drawing. These figures do not reproduce the coursework's
bigWig curves, measured knockdown colours or CRISPick design windows.

The cCRE source is the ENCODE Registry v4 Core Collection for K562 / GRCh38.
The fixed bigBed 9+5 schema supplies the element ID and `cCRE_class` fields.
Classes come from the provider's signal datasets and thresholds, independently
of the four peak-call files plotted here. `Promoter` denotes a promoter-like
signature near an annotated TSS. `Proximal enhancer` and `Distal enhancer`
denote enhancer-like signatures within or beyond 2 kb of the provider's
annotated TSSs, which need not be starts of the selected gene. Low-DNase means
low accessibility in K562. Candidate classes and proximity do not establish
functional enhancer-to-gene links.

`ccre_promoter_bp` counts overlap with the source class `Promoter`;
`ccre_enhancer_bp` combines `Proximal enhancer` and `Distal enhancer`.
Overlaps use the 23-base spacer-plus-PAM footprint and count each base only
once per class group. `ccre_ids` and `ccre_classes` retain all overlapping
elements, including other classes. Placed guides without overlaps have zero
bases and `none` for IDs/classes; ambiguous or not-found guides have missing
values. An empty track means no source elements in that interval, not evidence
of absent regulatory activity. H3K4me3 and H3K27ac peaks alone do not identify
a regulatory element's type or its target gene.

The default TSS window includes offsets from -1000 through +200 in the gene's
orientation: 1000 upstream bases, the TSS base itself, and 200 downstream
bases, for 1201 bases total. Minus-strand windows are reflected on the genomic
axis. Overlapping transcript windows are counted as a union, not repeatedly.

Only peak *intervals* are drawn. No peak height, motif, knockdown or off-target
measurement is fabricated. All four ENCODE peak tracks and the cCRE file are required inputs; failed
downloads stop the report instead of being treated as absent biological signal.
These are reference K562 experiments, not measurements in the user's cells.

The local exact-match search does not evaluate genome-wide uniqueness,
mismatches, bulges, non-NGG PAMs, individual genetic variants or alternative
contigs. A library gene name can be outdated; the program asks for an exact
GENCODE symbol/ID and does not silently substitute a different gene.

## Reading the code

- `src/guides/__main__.py`: menu, arguments and Quarto invocation.
- `src/guides/data.py`: downloads, text parsing and local BigBed queries.
- `src/guides/analysis.py`: exact placement and interval arithmetic.
- `src/guides/plot.py`: one Matplotlib figure.
- `reports/report.qmd`: the executable scientific report.

The few synthetic tests target strand/PAM coordinates, ambiguous placement
and overlapping intervals. They do not validate biological efficacy.
