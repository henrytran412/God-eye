# God-eye

Undergraduate research for the SJSU Davidson Student Scholars initiative (AY2026–27, mentor
Prof. Kaikai Liu): what fails when a roadside 3D detector, NVIDIA's V2XFusion trained on
DAIR-V2X-I, is deployed unchanged on TUMTraf Intersection, and whether that can be repaired
without target labels. Measurements run on a Jetson Orin Nano. The current findings live in
`results_jetson/repair/ATTRIBUTION.md`.

The repo is public — GitHub Pages serves `docs/`. Documents carrying the DSS cover page
(student ID, GPA, the mentor's signature) live in the gitignored `proposal/private/`; keep
every copy of them there.

`archive/ghostguard/` is an abandoned earlier project on cooperative-perception security. Its
figures come from the synthetic sandbox in `archive/ghostguard/code/ghostguard/sim.py`, with no
real dataset and no trained detector: quote them as design checks, never as benchmark
performance.

Terminology: *baselines* are the prior-art methods compared against. The *oracle* uses target
ground truth, so it marks the achievable ceiling and is never a competitor.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, driven through the `gh` CLI. `gh` is not yet installed;
see the setup steps at the end of `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root and ADRs in `docs/adr/`, both created lazily by
`/domain-modeling` rather than upfront. See `docs/agents/domain.md`.
