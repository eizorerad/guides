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

A local verification does not substitute for the hosted Reproduce Action or
an independent partner report required by the capstone.
