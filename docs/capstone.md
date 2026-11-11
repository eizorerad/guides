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
| Version control | Small described commits, topic branches and annotated release tags; author and committer Leonid Klarov. GitHub pull requests record integration into `main`. |
| Documentation and openness | README, MIT code license, CC BY 4.0 prose, third-party data terms, `CITATION.cff`, data availability and provenance records; contribution and conduct files. |

The [lesson 11 capstone instructions](https://khanlab.bio/cbio7501-f26/pages/11-documentation.html)
also request `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`; both are included.
The README explicitly answers its seven questions: purpose, related publication,
repository contents, hardware, reproduction, expected outputs and contact.
Methods distinguish measured overlaps, configured TSS windows and published
candidate regulatory classes, and state the limits of their interpretation.

## GitHub evidence and independent reproduction

The repository is public at [eizorerad/guides](https://github.com/eizorerad/guides).
The [pull request history](https://github.com/eizorerad/guides/pulls?q=is%3Apr),
[releases](https://github.com/eizorerad/guides/releases) and
[Reproduce runs](https://github.com/eizorerad/guides/actions/workflows/reproduce.yml)
provide the GitHub evidence. A local reproduction alone is not a hosted run;
check that the successful Action matches the submitted release tag or commit.

The earlier `v0.2.0` tag records the cCRE implementation before the lesson 11
documentation audit. Version `v0.2.1` includes that documentation and the public
repository metadata; earlier tags are preserved.

Before submission, give the instructor and partner the repository and release
links. The partner must independently reproduce that release from the README
and file the [course reproduce report](https://khanlab.bio/cbio7501-f26/assessment/reproduce-report-template.html).
This project does not fabricate an independent review or reproduction report.
The instructor also reads the repository and asks for explanations of choices.
A Zenodo DOI and a container image are optional for this capstone.
