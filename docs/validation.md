# Local validation

Validation date: 2026-11-11. Platform: Ubuntu Linux x86-64, Pixi v0.83.0.

The six synthetic coordinate tests passed. The terminal menu was exercised
from outside the repository: Dolcetto COTL1 produced three placed guides;
custom mode with one COTL1 spacer and one synthetic nonmatching sequence
produced one placed and one not-found status. Both HTML reports were inspected
in a browser, including their tables and figure. `CITATION.cff` passed
`cffconvert --validate` against schema 1.2.0.

Clean-clone reproduction and the course checker are being verified before the
local release tag is created. Their measured results will be recorded here.

A local verification does not substitute for the hosted Reproduce Action or
an independent partner report required by the capstone.
