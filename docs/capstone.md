# Capstone evidence

The project follows the [CBIO7501 capstone rubric](https://khanlab.bio/cbio7501-f26/assessment/capstone-rubric.html).
It is a separate repository for a manageable part of existing CBIO7102
research: comparing the regulatory context of guides targeting one gene.

Audit date: 2026-11-11. The rubric lists seven areas totalling 100 points and
says their weights are still to be confirmed. The automatic checker is
supporting evidence, not a grade: a green Reproduce Action on the submitted
release, the partner's reproduce report and the instructor's reading are
also required. Full credit includes being able to explain each choice.

| Rubric area | Evidence in this repository |
| --- | --- |
| Clean-clone reproduction | `pixi install --locked`, then `pixi run reproduce`; the course Reproduce workflow is included. |
| Organization and data | Raw inputs in ignored `data/raw/`, downloaded by Python, MD5-verified and read-only; fixed URLs and checksums in `metadata/`. Generated figures and tables are ignored. |
| Environment | `pixi.toml` and `pixi.lock`; Linux x86-64 is the declared platform. |
| Automation | Pixi tasks for the menu, download, reproduction and coordinate tests. Scientific settings are in `config/settings.toml`. |
| Literate report | `reports/report.qmd` recomputes placements, measurements, tables, figure and prose counts on every render; caption, alt text and software versions included. |
| Version control | Small local commits, topic branches and a local annotated release tag; sole author and committer Leonid Klarov. |
| Documentation and openness | README, MIT code license, CC BY 4.0 prose, third-party data terms, `CITATION.cff`, data availability and provenance records; contribution and conduct files. |

The [lesson 11 capstone instructions](https://khanlab.bio/cbio7501-f26/pages/11-documentation.html)
also request `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`; both are included.
The README explicitly answers its seven questions: purpose, related publication,
repository contents, hardware, reproduction, expected outputs and contact.
Methods distinguish measured overlaps, configured TSS windows and published
candidate regulatory classes, and state the limits of their interpretation.

## Still required outside this local build

The user requested **local commits only**. Consequently a GitHub repository,
actual pull requests, a GitHub Release and a green hosted Reproduce Action
are not claimed. A local branch merge is not a pull request.

Before submitting, publish the repository to GitHub (private is allowed),
open a real pull request from `feature/terminal-reports` into `main`, and review
and merge it there. Share the repository with the instructor and partner as
needed, publish a release containing the final documentation, run the workflow
on that version and have the
partner reproduce from the README.
The existing `v0.2.0` tag records the verified cCRE implementation; the lesson 11
documentation audit was committed afterwards. Do not treat that older tag as
containing the later documentation or silently move it.
The partner should file their own reproduce report; this project does not
fabricate one. Future changes can be reviewed through real pull requests.
A Zenodo DOI and a container image are optional for this capstone.
