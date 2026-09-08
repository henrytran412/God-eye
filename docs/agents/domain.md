# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists: it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions actually get resolved.

## File structure

This repo is **single-context**:

```
/
├── CONTEXT.md          ← created lazily by /domain-modeling
├── docs/
│   ├── adr/            ← created lazily by /domain-modeling
│   └── agents/         ← this configuration
└── code/
    └── ghostguard/     ← the simulation, fusion, and policy code
```

Multi-context layout (a root `CONTEXT-MAP.md` pointing at per-context `CONTEXT.md` files) is not in
use here and should not be introduced unless the repo grows into genuinely separate packages.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

Terms already load-bearing in this project, for reference until `CONTEXT.md` exists: *ego vehicle*,
*remote-only object* (one the ego cannot see itself), *ghost* / *phantom object*, *counterfactual
utility* `U(m|S)`, *safety-weighted risk* `R`, *admission* (the accept / soft-fuse / reject
decision), *baseline* (a prior-art method compared against — never the proposed method), and
*oracle* (the ground-truth upper bound, which cheats by construction).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
