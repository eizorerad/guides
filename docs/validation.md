# Local validation

Validation date: 2026-11-11. Platform: Ubuntu Linux x86-64, Pixi v0.83.0.

The six synthetic coordinate tests passed. The terminal menu was exercised
from outside the repository: Dolcetto COTL1 produced three placed guides;
custom mode with one COTL1 spacer and one synthetic nonmatching sequence
produced one placed and one not-found status. Both HTML reports were inspected
in a browser, including their tables and figure. `CITATION.cff` passed
`cffconvert --validate` against schema 1.2.0.

## Clean-clone reproduction

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

Only documentation was updated after this implementation verification.
The annotated local tag `v0.1.0` marks the documented version on
`feature/terminal-reports`. `main` is retained as the starting point so the
implementation can later be submitted through a real pull request.

A local verification does not substitute for the hosted Reproduce Action or
an independent partner report required by the capstone.
