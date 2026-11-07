# Subagent execution protocol (Codex / supported agent harnesses)

## Core distinction
A subagent is a **separate model context**, not a different model, an independently trained expert, a security boundary, or an independent empirical observation. Do not call juror votes statistically independent evidence. Each juror gets a distinct role and narrow brief, but all share model limitations and may share a workspace.

## Coordinator responsibilities
1. Create a neutral case file with explicit source labels: `USER CLAIM`, `VERIFIED EVIDENCE`, `ASSUMPTION`, `UNKNOWN`.
2. Use the host's **actual subagent delegation tool** (not a simulated tool call). In supported Codex/Agents API setups, look for the exposed multi-agent tools, for example `spawn_agent`, `wait_agent` or the host's equivalent. Tool names are harness-dependent; do not invent a tool that is unavailable.
3. Set child context to the minimum necessary if the harness supports that option (e.g. do not fork the full conversation). Disable child-to-child delegation for this task by instruction. Never forward other juror votes to a juror.
4. Give each agent the *contents* of its designated brief and only the record explicitly permitted for that phase, including the case and four argument statements for jurors. Do not ask children to traverse the whole repository or read `.court/jury/`.
5. Group parallel jurors in waves bounded by the host's concurrency limit. Await all jobs in a wave before continuing. Assign exactly one task per juror and preserve identity, phase and result.
6. On completion, the coordinator saves the **verbatim** returned result in that job's output file, then registers the host-provided subagent identifier with `court.py attest --phase PHASE --job JOB --agent-id HOST_ID`. Do not invent or reuse identifiers. The coordinator never writes its own ballot.
7. Retry missing/invalid jobs once using a **new** child context. If still missing, write `NO VOTE`, record why, and render a partial review. Never invent a vote.
8. Execute the deterministic Python `tally` after every juror is done, and only then dispatch the synthesis/judge agent. Never let the judge change votes.
9. Verify the count of distinct child IDs and completion before calling it multi-agent. If unavailable or unverifiable, disclose that actual multi-agent execution was not established.

## Parallelism vs isolation
A shared filesystem is not a security boundary. Context separation is achieved by sending bounded prompts and not propagating votes; it cannot guarantee agents have no tool access to other files. For stronger isolation, run children in separate working directories/environments or limit their available tools. Child reasoning may also share systematic model biases.

## Roles and phases
- Opening: prosecution challenges the proposal as stated, defense makes strongest evidence-grounded case for proceeding.
- Rebuttal: each addresses specific points from the other side, conceding valid ones.
- Jury: 12 distinct specialists from `jurors.json`, each has a specialty, four mandatory checks and a falsification test; no other jury outputs permitted.
- Judge/synthesizer: after votes are frozen, group the objections, propose tests and stopping conditions. The judge does not vote.

## ChatGPT fallback
When the actual subagent host tool is missing, say so and offer a labeled single-model perspective simulation; never write `--mode agent` just because role prompts exist. A chat without writable files can produce an inline report only.

## Host references
- https://developers.openai.com/api/docs/guides/agents-api/multi-agent
- https://developers.openai.com/api/docs/guides/responses-multi-agent
