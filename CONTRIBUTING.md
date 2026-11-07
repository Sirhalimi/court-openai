# Contributing

Issues and pull requests are welcome. Keep contributions focused on verifiable improvements to portability, safety, evaluation quality and test coverage.

1. Do not remove original attribution or the MIT license.
2. Don't represent role simulation as independently generated model votes.
3. Add regression tests for command-line or parser changes.
4. Preserve compatibility with Python 3.9+ standard library where possible.
5. Avoid introducing network calls, credentials, or dependencies without documenting their necessity.
6. Do not commit `.court/` runs: they may contain sensitive user decisions.

Run `python3 -m unittest discover -s tests -v` before submitting a PR.
