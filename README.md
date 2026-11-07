# ⚖️ Court — Multi-Agent Decision Review for Codex & ChatGPT

**Turn an idea into a falsifiable decision, not a flattering answer.** A reusable, Persian/English Agent Skill that stages adversarial arguments, sends up to **12 distinct specialist reviews to separate host subagents**, counts their responses deterministically, and produces a practical `VERDICT.md`.

Adapted from [Alex Chen's original court-skill](https://github.com/alexyc9381/court-skill) under MIT. This community edition is **not affiliated with or endorsed by OpenAI or the original author**.

## What changed in v2.0

- Twelve specialist roles (market demand, finance, engineering, operations, privacy/security, legal/ethics, customer experience, competition, statistics/evidence, growth, capital allocation, pre-mortem) with mandatory checks and a falsifiable experiment for every vote.
- **Subagent-first orchestration**: use the host's *real* delegation tools; specialist votes must be returned from different subagent contexts, not invented by a single orchestrator.
- **Attestation check**: each completed role job records a distinct, actual host subagent ID; an unverified agent-mode run cannot render as complete.
- Decision memo with critical risks, experiments and stop/go criteria rather than only a court metaphor.
- Labels simulated conversation fallback honestly. Independent **context** does not mean statistically independent expertise or sandbox isolation.

## 12 specialists

| Specialist | Main challenge |
|---|---|
| Demand Researcher | Is the pain real and does behavior demonstrate demand? |
| Financial Analyst | Are unit economics, runway and assumptions credible? |
| Systems Engineer | Will it work reliably outside a demo? |
| Operations Lead | Can this run every day with available people? |
| Security & Privacy Reviewer | How can it be abused or leak sensitive data? |
| Legal & Ethics Reviewer | What compliance, liability or ethical traps exist? |
| First-Time Customer | Will someone understand, trust and return? |
| Competitive Strategist | Why won't existing alternatives win? |
| Statistician & Evidence Auditor | What is evidence vs speculation or sampling bias? |
| Growth & Distribution Lead | Where do initial customers really come from? |
| Capital Allocator | Is this better than the next-best use of resources? |
| Adversarial Failure Analyst | What failure chain is everyone overlooking? |

## How it works

```text
CASE FILE: verified evidence / claims / assumptions / unknowns
       |
       v
2 separate openings: prosecution + defense
       |
       v
2 separate rebuttals
       |
       v
12 separate specialist subagents (bounded parallel waves)
       |       (no access to peer ballots via the prompt)
       v
Deterministic Python tally (not model arithmetic)
       |
       v
1 synthesis/judge subagent -> VERDICT.md + experiments
```

**Total full run: 17 delegated jobs; quick 6-specialist run: 11 jobs.** Models can share the same underlying biases; votes are qualitative perspectives, **not probability estimates**.

## Install: Codex

Clone your published repository or unpack this project, then place the **entire directory** in the user's skills folder (not just the `SKILL.md`):

```bash
git clone https://github.com/Sirhalimi/court-openai.git
mkdir -p ~/.agents/skills/court
cp -R court-openai/. ~/.agents/skills/court/
```

Confirm `~/.agents/skills/court/SKILL.md` exists. Restart/refresh Codex if necessary. Then ask:

```text
Use $court --jury 12 to stress-test this business idea. Use real separate subagents for each specialist and report the attestation count: ...
```

Codex must provide multi-agent delegation tools to this session. If those tools are unavailable or disabled, the skill **does not secretly make API calls** and it must say it is falling back to simulation.

For an Agents API session, the creator can enable multi-agent delegation through the documented session's `agent.multi_agent.enabled` setting. For other Codex hosts, follow the current host's subagent configuration. See [OpenAI Agents API multi-agent documentation](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) and [Responses multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent).

## ChatGPT compatibility

In ChatGPT environments that support installing or importing custom Agent Skills, use the full skill folder. **A normal ChatGPT chat without real delegation tools does not create 12 separate agents.** It can still run a visibly labeled single-model perspective simulation, but no independent-agent claim is made. Python/file output additionally requires a file-capable runtime.

## CLI: deterministic bookkeeping only

```bash
mkdir -p .court
cp examples/example-case.md .court/case.md
python3 scripts/court.py plan --quick
python3 scripts/court.py init --case-file .court/case.md --quick --seed 7 --mode agent
python3 scripts/court.py next
python3 scripts/court.py prompts opening
```

For each announced job, the **host orchestrator** launches a separate subagent using its real tool and passes that job brief and allowed inputs. After the host returns the answer, the coordinator writes it **verbatim** to the job output path and records the real subagent ID:

```bash
python3 scripts/court.py attest --phase opening --job prosecution --agent-id ACTUAL_HOST_AGENT_ID
```

Repeat for every required job. The ordered phases are `opening`, `rebuttal`, `jury`, `judge`. After jury jobs and **before** judge, run `python3 scripts/court.py tally`; after every job and attestation exists, run `python3 scripts/court.py render`. `render --allow-incomplete` intentionally prints **unverified/partial** if needed.

The Python script manages files and deterministic counting. **It does not implement subagent spawning**: only a supported Codex/agent runtime can do that. A text string that looks like an agent ID does not prove isolation; the coordinator must record an identifier received from a real host tool.

## Output

`.court/<run-id>/` contains a neutral case, isolated role briefs, opening and rebuttal statements, separate specialist responses, agent attestations in `state.json`, `tally.json` and `VERDICT.md`. All generated case data remains under `.court/`, which is gitignored.

| Vote | Meaning |
|---|---|
| GUILTY | Do **not** proceed with the current proposal unchanged |
| NOT GUILTY | Reasonable to proceed under stated evidence and safeguards |
| HUNG JURY | No voting majority |
| NO VOTE | Missing/invalid response; never silently count it |

## Test and publication

```bash
python3 -m unittest discover -s tests -v
```

CI tests run on pushes and pull requests. Do **not** commit any `.court/` data containing private proposals or secrets.

## Limits and safety

- Subagents have **separate contexts**, not independent training, guaranteed impartiality or security isolation. Shared workspace access may expose other files despite prompt instructions; for strong access isolation use separate environments or tool restrictions.
- Reproducing the same `--seed` reproduces **role selection**, not the model's judgments.
- Legal, medical, financial or safety-critical decisions require qualified review where appropriate.
- No token/API keys or third-party dependencies are required by the Python bookkeeping tool; actually running host subagents consumes your environment's model usage.

## License

MIT. Original: © 2026 Alex Chen, [court-skill](https://github.com/alexyc9381/court-skill). Credit and license preserved in `LICENSE` and `CITATION.cff`.
