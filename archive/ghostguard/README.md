# GhostGuard — abandoned

The project's first direction, September 2026: should a connected vehicle admit a shared
detection based on the **measured harm** of admitting it, rather than on proxies for whether
the message is false?

It was dropped because V2X message attacks on deployed vehicles have no documented real-world
instance — `SECURITY_TRACK_ASSESSMENT.md` is the audit that established it, and
`../../notes/PERCEPTION_PIVOT.md` records where the work went next.

**Every number in this folder comes from a hand-parameterised synthetic simulator**
(`code/ghostguard/sim.py`) with no real dataset and no trained detector. They are design checks
on whether the decision rule is well-posed, never benchmark performance.

| | |
|---|---|
| `code/` | The simulator, the gating methods, and the experiment scripts. `python code/run_all.py` regenerates `results/`. |
| `results/` | CSVs and figures from those experiments |
| `REVIEW.md` | Baseline implementation and design audit |
| `ADVISOR_BRIEF.md` | Baseline results and revised direction, for the 6 September advisor meeting |
| `SECURITY_TRACK_ASSESSMENT.md` | Why the security framing could not meet his evidence bar |

Paths inside these documents, such as `code/run_all.py` and `results/`, are relative to this
folder, which was the repository root when they were written. The proposal drafts they cite,
`PROPOSAL_v2.md` among them, are in `../../proposal/archive/`.
