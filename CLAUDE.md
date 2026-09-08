# GhostGuard

An undergraduate research project on cooperative perception for connected vehicles, submitted to the
SJSU College of Engineering Davidson Student Scholars initiative (AY2026–27). The research question
is whether a vehicle should admit a shared detection based on the **measured harm** admitting it
causes, rather than on proxies for whether the message is false.

**One thing to keep straight before quoting any number from `results/`:** every figure produced so
far comes from the synthetic sandbox in `code/ghostguard/sim.py`, not from OPV2V or any real
dataset, and no LiDAR detector has been trained. Treat those results as design checks on whether the
decision rule is well-posed, never as benchmark performance. The distinction matters because this
material goes to a faculty mentor and a review committee.

Terminology: *baselines* are the prior-art methods compared against; GhostGuard is the *proposed
method*, never "our baseline". The *oracle* reads ground-truth harm and therefore cheats — it marks
the achievable ceiling and is not a competitor.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, driven through the `gh` CLI. Note that `gh` is not yet
installed and no remote exists; see the setup steps at the end of `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root and ADRs in `docs/adr/`, both created lazily by
`/domain-modeling` rather than upfront. See `docs/agents/domain.md`.
