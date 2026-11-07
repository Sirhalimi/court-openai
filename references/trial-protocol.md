# Decision review protocol

1. The coordinator prepares a neutral case file with source status: verified evidence, user statements, assumptions, unknowns and alternatives.
2. Dedicated prosecution and defense subagents write evidence-aware arguments as stated, never a strawman or invented market fact.
3. Rebuttal subagents answer opposing arguments and concede valid objections.
4. Specialist subagents from `jurors.json` read the same case and four arguments, with unique mandatory questions and falsification tests. They do not receive other specialists' votes.
5. The coordinator saves subagent replies verbatim, records real host IDs, and uses Python to count votes. IDs are traceability labels, not cryptographic guarantees of context isolation.
6. After the tally, a separate synthesis agent explains risks, defensible positives, one-week experiments and stop/go conditions without changing any vote.
7. Produce `VERDICT.md` with the explicit mode, unverified/missing flags, qualitative risks and votes. An unsupported/unknown condition must not be disguised as evidence.

## Terminology

- `GUILTY`: do not proceed unchanged.
- `NOT GUILTY`: proceed as stated subject to explicit safeguards.
- `HUNG JURY`: tie/no majority.
- `NO VOTE`: no valid ballot; not counted.
- Votes are **not** probabilities of success and distinct agents are not scientifically independent samples.

## Artifacts

`.court/<run>/case.md`, `state.json`, `briefs/*.md`, `opening/*.md`, `rebuttal/*.md`, `jury/*.md`, `tally.json`, `judge/judge.md`, `VERDICT.md`.

## Retrial

Preserve past runs and create a **new** case using actually obtained evidence. Contrast old/new assumptions, stop/go thresholds and specialist objections; never claim improvement from a rewrite of the prompt alone.
