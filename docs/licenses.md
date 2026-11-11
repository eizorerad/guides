# Licenses and attribution

## This project

Original Python code, tests and configuration: **MIT**, copyright 2026 Leonid
Klarov; see [LICENSE](../LICENSE). Original README, documentation, report prose
and figure design: **CC BY 4.0**, copyright 2026 Leonid Klarov
([license](https://creativecommons.org/licenses/by/4.0/)). Source-derived
sequences and annotations retain the terms of their providers below.

The [README banner](assets/guides-banner.png) was supplied by the project
maintainer and is included under the documentation license. It is decorative
artwork; scientific locus plots are computed separately when the report renders.
Badge images are served by Shields.io, with release and workflow status from
GitHub.

The scientific idea develops the locus-annotation component of the author's
CBIO7102 **One gene, four guides** coursework. The Python implementation was
written for this standalone project; no unlicensed upstream Python module was
copied from the cluster. Source-specific citations are also printed in reports.

## Data

The raw files are downloaded from their providers. They are not redistributed
in Git and are not covered by this project's MIT license. Fixed URLs and
checksums are in [sources.json](../metadata/sources.json).

| Data | Attribution and applicable terms |
| --- | --- |
| Dolcetto Set A spacer table | David Root / John Doench, Broad GPP; Sanson et al. (2018), [doi:10.1038/s41467-018-07901-8](https://doi.org/10.1038/s41467-018-07901-8). Downloaded from the [Addgene library page](https://www.addgene.org/pooled-library/broadgpp-human-crispri-dolcetto/). Addgene's [Terms of Use](https://www.addgene.org/terms-of-use/) govern site content, including restrictions on commercial use. No separate open-data license is asserted for this table. This capstone uses it for noncommercial academic research and downloads the original file rather than bundling it. The article's CC BY 4.0 license is not assumed to relicense Addgene's table. |
| GENCODE v32 basic annotation | GENCODE Consortium; Frankish et al. (2019), [doi:10.1093/nar/gky955](https://doi.org/10.1093/nar/gky955). [GENCODE data access](https://www.gencodegenes.org/pages/data_access.html) states that its data are open access; [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/) request attribution and preserve applicable third-party rights. No additional CC license is assigned here. |
| GRCh38 primary chromosome FASTA files | Genome Reference Consortium, downloaded from UCSC. Assembly GCA_000001405.15; [UCSC assembly README](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/README.txt), [GRC data](https://www.ncbi.nlm.nih.gov/grc/human/data). The reference sequence is used as public genome data; the UCSC software license does not become the license of these sequence files. Provider notices and potential third-party rights remain applicable. |
| K562 DNase and ChIP-seq peaks | ENCODE; exact file accessions and experiments appear in each report. The [ENCODE data-use policy](https://www.encodeproject.org/about/data-use-policy/) allows unrestricted use of released data and requests citation. ENCODE Project Consortium (2012), [doi:10.1038/nature11247](https://doi.org/10.1038/nature11247). We state this policy, rather than inventing a separate CC license. |
| ENCODE4 K562 cCRE Core Collection | ENCODE Consortium; Weng and Moore labs, UMass Chan Medical School; hosted by UCSC. Moore et al. (2026), *An Expanded Registry of Candidate cis-Regulatory Elements for Studying Transcriptional Regulation*, [doi:10.1038/s41586-025-09909-9](https://doi.org/10.1038/s41586-025-09909-9). Released data follow the [ENCODE unrestricted-use policy](https://www.encodeproject.org/about/data-use-policy/) with attribution. The fixed source URL, checksum, registry version and four supporting signal accessions are in `metadata/sources.json`; the BigBed is downloaded, not bundled in Git. |

No physical library, plasmid or biological material is distributed or ordered
by this software. Custom sequences are supplied by the user and retain their
original rights and attribution requirements.

## Reused workflow and dependencies

`.github/workflows/reproduce.yml` is copied from Aziz Khan's CBIO7501 course,
licensed MIT. Its full copyright and permission notice is retained in
[cbio7501-MIT.txt](licenses/cbio7501-MIT.txt). Attribution is not a Git coauthor
trailer.

Dependencies are installed from their original distributions into the ignored
Pixi environment; their notices remain there. The project does not vendor their
source or distribute an environment archive. Python uses the PSF license,
NumPy and pandas use BSD licenses, Matplotlib uses its PSF-based license,
Requests uses Apache-2.0, [pyBigWig](https://github.com/deeptools/pyBigWig) uses MIT,
Jupyter packages use BSD licenses, and Quarto uses
GPL-2.0. Quarto runs as a separate command; its license is not relabeled MIT.
`pixi.lock` records the exact installed packages and their source locations.
