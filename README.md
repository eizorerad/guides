# guides

A small terminal program that places published or user-supplied CRISPRi guides
on a human GRCh38 locus and generates a Quarto report of their K562 regulatory
context. Author: Leonid Klarov <leonid.klarov@gmail.com>.

This CBIO7501 capstone develops the locus-annotation part of my CBIO7102
**One gene, four guides** coursework. The research question is: **how does local
regulatory context differ between guides targeting the same gene?** The report
compares annotated promoter windows and DNase, H3K4me3, H3K27ac and CTCF peaks.

The first version supports human **GRCh38, K562, SpCas9/NGG and CRISPRi**.
It retrieves existing guides from **Dolcetto Set A**; it does not design or
rank new guides. It is a descriptive analysis, not an efficacy or genome-wide
off-target predictor. Only called peak intervals are drawn, not signal heights.

## Start here

On the author's computer, the command is already installed:

```bash
guides
```

The menu and scientific report are in English:

```text
1  Gene → guides from Dolcetto Set A
2  Gene + custom guides
0  Exit
```

Choose **1** and enter `COTL1` for the demonstration. Choose **2** to enter a gene
and then your own spacers, one per line; finish with an empty line. Both modes
need the target gene so the program knows which locus to search.

Use an exact GENCODE v32 gene symbol or an unversioned Ensembl gene ID.
Each custom spacer must contain **20 DNA bases (A/C/G/T), without PAM,
adapters or FASTA headers**, in its own 5′–3′ orientation. Lowercase is accepted.
Any number of spacers is allowed. Dolcetto Set A normally has three guides per
gene; this program does not pad it to four.

## Reproduce from a clean clone

Hardware/platform: Linux x86-64, an ordinary CPU, no GPU or cluster account.
Allow 4 GB RAM and 4 GB free disk space for installation, caches and the demo.
The installed environment occupies about 0.7 GB; the demo raw inputs occupy
about 56 MB. Internet access is needed for the first installation and downloads.
Later runs reuse checksum-verified local files. Selecting another chromosome
downloads its compressed FASTA too. Other operating systems are not in the lock.

Install [Pixi](https://pixi.sh/latest/installation/) from its official source
(tested with v0.83.0), open a fresh clone of this repository, then run:

```bash
pixi install --locked
pixi run reproduce
```

This downloads all demo inputs, computes the analysis during Quarto rendering
and writes `reports/COTL1-dolcetto.html`. Open that self-contained HTML file in
a browser. No manual data placement, absolute cluster paths or credentials
are needed. First-run time depends on download speed; see the measured local
run in [validation.md](docs/validation.md).

To test a local clone before publishing a GitHub repository:

```bash
git clone /absolute/path/to/guides /tmp/guides-check
cd /tmp/guides-check
pixi install --locked
pixi run reproduce
```

The default gene and window sizes are in [settings.toml](config/settings.toml).
The download URLs, releases, checksums and terms are fixed in
[sources.json](metadata/sources.json), with a checksum list in
[checksums.md5](metadata/checksums.md5). All scientific counts, tables and
figures are recomputed by [report.qmd](reports/report.qmd).

## Other commands

Run these from the repository directory:

```bash
pixi run guides                                  # interactive menu
pixi run guides --gene COTL1                      # published guides
pixi run guides --gene COTL1 --guides-file /absolute/path/to/spacers.txt
pixi run download                                # download demo inputs
pixi run test                                    # synthetic coordinate tests
```

Optional: `bash scripts/install_command.sh` installs a `guides` launcher in
`~/.local/bin` (or `XDG_BIN_HOME`). That directory must be on `PATH`, and the
repository must stay at its installed location. It will not overwrite an
existing command. The portable alternative is always `pixi run guides`.

## Expected outputs

For each gene and mode (`dolcetto` or `custom`):

| File | Contents |
| --- | --- |
| `reports/GENE-mode.html` | Self-contained report, figure, tables, methods and citations |
| `results/GENE-mode/locus.png` and `.svg` | Locus figure for viewing or reuse |
| `results/GENE-mode/guides.csv` | Placement status, spacer coordinates and context measurements |
| `results/GENE-mode/placements.csv` | All exact local matches, including ambiguous alternatives |
| `results/GENE-mode/request.json` | Gene and submitted custom sequences, if any |
| `results/GENE-mode/provenance.json` | Settings, resolved gene, source URLs, raw-file hashes and lock hash |
| `results/GENE-mode/software.json` | Software versions used in the report |
| `results/GENE-mode/render.log` | Quarto output for troubleshooting |

A rerun of the same gene and mode replaces that output. Copy a report/results
directory elsewhere before comparing separate custom sets. Run one report at
a time. Generated outputs, raw data and the environment are ignored by Git.

In the COTL1 example, the three Dolcetto spacers should each have one exact local
placement. They overlap the defined promoter windows and selected H3K4me3
peaks, but not the selected DNase, H3K27ac or CTCF peaks. Absence of a called
peak is not evidence that the locus has no activity. Details and coordinate
conventions are in [methods.md](docs/methods.md).

## Data availability and licenses

All inputs used by the demonstration are publicly downloadable from their
providers; no private MBZUAI data are required. Original raw files are kept
read-only in `data/raw/`, verified against committed MD5 checksums and never
committed. A failed download or checksum stops the run. The program does not
upload custom sequences.

| Input | Source |
| --- | --- |
| Published spacers | [Dolcetto Set A, Addgene / Broad GPP](https://www.addgene.org/pooled-library/broadgpp-human-crispri-dolcetto/) |
| Genes and transcript starts | [GENCODE v32 basic annotation](https://www.gencodegenes.org/human/release_32.html) |
| Reference sequence | [UCSC GRCh38 chromosomes](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/) |
| K562 DNase peaks | [ENCFF185XRG](https://www.encodeproject.org/files/ENCFF185XRG/) |
| K562 H3K4me3 peaks | [ENCFF961SPZ](https://www.encodeproject.org/files/ENCFF961SPZ/) |
| K562 H3K27ac peaks | [ENCFF038DDS](https://www.encodeproject.org/files/ENCFF038DDS/) |
| K562 CTCF peaks | [ENCFF769AUF](https://www.encodeproject.org/files/ENCFF769AUF/) |

Original code is under the [MIT license](LICENSE); original documentation and
report prose are [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Third-party data retain their own terms. In particular, no separate open-data
license is asserted for the Addgene table; this is a noncommercial academic
use under its site terms, and the raw table is not redistributed in Git.
See [licenses and attribution](docs/licenses.md), including the retained
MIT notice for the course's Reproduce workflow.

## How to cite

Klarov, Leonid (2026). *guides: reproducible CRISPRi guide context in K562*,
version 0.1.1. Machine-readable metadata: [CITATION.cff](CITATION.cff).
Also cite the original datasets and publications listed in each report:
Sanson et al. (2018), [doi:10.1038/s41467-018-07901-8](https://doi.org/10.1038/s41467-018-07901-8);
Frankish et al. (2019), [doi:10.1093/nar/gky955](https://doi.org/10.1093/nar/gky955);
ENCODE Project Consortium (2012), [doi:10.1038/nature11247](https://doi.org/10.1038/nature11247),
and the specific ENCODE file accessions.

## Code and capstone status

Four small modules handle input/rendering, downloads, interval analysis and
plotting in `src/guides/`. The executable report is in `reports/`; settings and
source metadata have separate folders. There is no server, database, trained
model or workflow engine to manage.

See [capstone.md](docs/capstone.md) for the rubric mapping and
[validation.md](docs/validation.md) for checks actually performed. Development
and the release tag are local. GitHub publication, real pull requests, a hosted
Reproduce run, a GitHub Release and the partner's reproduction report still
need to be completed before submission. A Zenodo DOI is optional for this
capstone and has not been created.
