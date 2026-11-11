# Contributing

Use [GitHub issues](https://github.com/eizorerad/guides/issues) to discuss a
change, or contact Leonid Klarov at <leonid.klarov@gmail.com>.

For a problem report, include the command, software version, platform, expected
result and actual result. Attach a small reproducible example and relevant
`render.log` output when you may share them. Do not disclose restricted
sequences, credentials or personal information.

Keep changes small and readable. Use a topic branch and explain the problem,
the change and relevant validation in the pull request. Keep scientific
settings in `config/` and source URLs, checksums and terms in `metadata/`.
Do not commit raw data, generated reports, results or environments.

Before proposing a code change, run these commands from the repository:

```bash
pixi install --locked
pixi run test
pixi run reproduce
```

Add a focused test when a change affects scientific calculations. For changes
to dependencies or downloads, also reproduce from a fresh clone. Update the
methods and source attribution when their meaning changes.

Original code uses MIT; original documentation uses CC BY 4.0. Contributions
must respect those terms and retain applicable third-party attribution.
Participation follows [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
