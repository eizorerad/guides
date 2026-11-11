# Local validation

Validation date: 2026-11-11. Platform: Ubuntu Linux x86-64, Pixi v0.83.0.

The six synthetic coordinate tests passed. The terminal menu was exercised
from outside the repository: Dolcetto COTL1 produced three placed guides;
custom mode with one COTL1 spacer and one synthetic nonmatching sequence
produced one placed and one not-found status. Both HTML reports were inspected
in a browser, including their tables and figure. `CITATION.cff` passed
`cffconvert --validate` against schema 1.2.0.

## Baseline: v0.1.0 clean-clone reproduction

Implementation commit: `48805ee`. A separate local Git clone was created with
`git clone --no-hardlinks`, starting without `data/`, `results/` or `.pixi/`.
`pixi install --locked` succeeded. The global package cache was reused, but all
seven raw input files were downloaded afresh from their original providers.
No raw data or generated results were copied from the working repository.

| Check | Observed result |
| --- | --- |
| `pixi run reproduce` in the fresh clone | Exit 0, 88.59 seconds including raw downloads |
| Same command with local raw files already present | Exit 0, 18.88 seconds |
| Largest process RSS reported by `/usr/bin/time -v` for the fresh run | About 348 MiB; this is not the sum of concurrent processes |
| `guides.csv`, `placements.csv`, `locus.png`, `provenance.json`, `software.json` | Byte-identical between the working repository and fresh clone |
| `git status --porcelain` in the clone after reproduction | Empty |
| Custom report after the final table-formatting change | Rendered successfully; integer coordinates and the not-found row retained |

Demo `guides.csv` SHA-256:
`540f2c9dcf38e44e204fb3833ad503a8b9c16f676fea352c5d80fca682f229c0`.
Demo `locus.png` SHA-256:
`6bcc5a15df73a0068c9f58f52a8d5e0e09a3e7b6725032ab88763522c4fb8e11`.
HTML and SVG files contain render-generated identifiers or timestamps, so
byte equality is not a requirement for those formats.

## Course checker

The official [check_capstone.py](https://github.com/khan-lab/cbio7501-f26/blob/main/assessment/check_capstone.py)
downloaded on the validation date reported **19 of 20 automatic checks pass**
on the fresh clone. The only `NO` was the release DOI, explicitly optional for
a capstone. All other automatic items passed, including committed lock and
report source, task/workflow presence, ignored raw data, README coverage,
license and citation metadata. This checker lists evidence; it does not assign
a course grade or prove that hosted CI has run.

Only documentation was updated between that implementation verification and
the baseline tag. The annotated local tag `v0.1.0` marks that version on
`feature/terminal-reports`. `main` is retained as the starting point so the
implementation can later be submitted through a real pull request.

## v0.1.1: English interface and compact locus maps

The menu, prompts and error messages are now English. The figure uses the
coursework's compact track-and-guide layout, with a TSS-relative axis and
500 bp plot flanks. `plot.py` grew from 63 to 77 lines; no dependencies or
analysis algorithms were added.

`pixi install --locked` passed. The menu was exercised with an invalid option
and invalid custom spacer to check the English prompts and error path. The
demo and saved custom request both rendered successfully, and both PNGs were
visually inspected. A source-text scan found no remaining Cyrillic in the
application, README, documentation, settings or report source.

For the minus-strand COTL1 example, the displayed TSS is zero, a position
100 bp downstream is +100, and a position 100 bp upstream is -100. Tick labels
were checked for a correctly displayed zero. The `guides.csv` SHA-256 still
matches the baseline above: the figure update did not change measurements.
The earlier clean-clone run documents v0.1.0; these are the incremental checks
for the v0.1.1 update.

## v0.1.2: help and unattended commands

`guides help`, `guides --help` and `guides -h` returned identical help with
exit code 0. The installed launcher was exercised from outside the repository.
With standard input at EOF, both a Dolcetto report and an inline custom-guide
report completed successfully using `--json`. Their stdout parsed as one JSON
object containing existing absolute report/results paths; progress was on
stderr. Both reports recorded software version 0.1.2.

Missing arguments in an unattended run, custom guides without a gene,
conflicting input options and incompatible download options returned exit 2
without prompting. An invalid spacer returned exit 1 with empty stdout.
The interactive menu was separately opened in a terminal and exited with 0.
`pixi install --locked` passed; the demo measurements retained the baseline
`guides.csv` SHA-256 above. No analysis or plotting code changed in this update.

## v0.1.3: TSS-window and enhancer audit

The raw GENCODE v32 GTF contains two basic COTL1 transcripts, both on the
minus strand, with 1-based TSSs at chr16:84,618,059 and chr16:84,618,078.
These agree with the program's parsed starts. Independently enumerating bases
confirmed that the two configured windows are chr16:84,617,859–84,619,059 and
chr16:84,617,878–84,619,078 (1-based inclusive). Each contains exactly the
gene-oriented offsets -1000 through +200, including the TSS base: 1201 bases.
Independent set intersections confirmed 23 bp of window overlap for each of
the three demo guide footprints.

No enhancer or ENCODE cCRE annotation is present among the loaded sources.
The coursework's orange cCRE colour meant proximal enhancer-like elements;
reusing orange for these configured windows could mislead a reader. The
strip is now neutral grey and directly labelled "Configured TSS windows".
The report, README, methods and citation abstract distinguish these windows
from experimentally annotated promoters and enhancers. The existing
`promoter_bp` column retains its name for script compatibility, with an
explicit definition in the report and README.

`pixi install --locked` passed. Both saved example reports were rebuilt with
the corrected descriptions; the new figure was visually inspected and the
demo measurements retained the baseline `guides.csv` SHA-256. This update
clarifies the existing data; it does not add a promoter/enhancer classifier.

## v0.2.0: ENCODE4 K562 cCREs

The K562 Core Collection BigBed was downloaded from UCSC (93,066,846 bytes,
MD5 `18769a678376a2a04b73e851f6ee6d53`). The locked environment adds
pyBigWig 0.3.29 to read local intervals. The demo's eight raw inputs total
152,249,617 bytes (145.2 MiB). The Python implementation grew by 38 lines net;
source metadata, report explanations and documentation account for the rest.

The four COTL1 elements were independently compared with the
[UCSC track API](https://api.genome.ucsc.edu/getData/track?genome=hg38;track=ENCFF414OGC_ENCFF806YEZ_ENCFF849TDM_ENCFF736UDR;chrom=chr16;start=84617483;end=84618539).
IDs, source classes and full 0-based half-open boundaries agree exactly:

| Element | Start | End | Source class |
| --- | ---: | ---: | --- |
| EH38E4150991 | 84617355 | 84617556 | Proximal enhancer |
| EH38E3195315 | 84617621 | 84617846 | Proximal enhancer |
| EH38E3195316 | 84618006 | 84618355 | Promoter |
| EH38E1833371 | 84618434 | 84618662 | Proximal enhancer |

Independent base-set intersections give promoter-like overlaps of 0, 23 and
9 bp for g1–g3, and zero enhancer-like overlap. g1 touches the promoter
boundary but shares no bases. All pre-existing `guides.csv` columns match
the v0.1.3 baseline. Empty-region, boundary-touching, absent-chromosome and
beyond-chromosome BigBed queries returned empty tables. The six existing
coordinate tests passed.

The demo and the workspace's saved two-guide custom request rendered
successfully. The installed launcher ran from `/tmp` with `--json` and stdin
at EOF; stdout was pure JSON with existing absolute output paths and progress
was on stderr. The custom request was preserved. Both HTML reports contain
the cCRE tables with correctly converted 1-based coordinates, source links,
an embedded figure and software version 0.2.0. The new demo PNG was visually
inspected: the separate cCRE track and its legend do not overlap other panels.

A local verification does not substitute for the hosted Reproduce Action or
an independent partner report required by the capstone.
