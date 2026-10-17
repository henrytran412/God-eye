---
title: Repair Attempts
tags:
  - experiment
  - negative-result
---

# Repair Attempts

Nine training-free interventions, in the order they ran. Each was chosen by what the
previous one ruled out, so the sequence is the argument.

| Attempt | Car 3D@0.5 | Verdict |
|---|---|---|
| Baseline | 1.83 | reference |
| [[INT8 recalibration]] | 0.15 | worse |
| [[Head threshold]] | 1.83 | no effect |
| [[Operating point]] | 2.30 | not adaptation |
| [[Intensity neutralised]] | 0.23 | much worse |
| [[Camera blanked]] | 0.00 | collapse |
| [[Density control]] | — | exonerated |
| [[Calibration audit]] | — | sound |
| [[Ground-plane sweep]] | 2.08 | no peak |
| [[Ground-plane, confirmed]] | 1.32 | did not replicate |

> [!failure] Net domain-specific improvement: zero
> The only positive — lowering the evaluator's operating point, +0.47 — helps the
> **source** domain just as much, so it is threshold tuning rather than adaptation.

## Why none of them worked

[[Component Attribution]] predicts it. The failure is conjunctive: four axes degrade at
once, and no intervention that leaves the weights untouched moves more than one. Nothing
in the input space crosses a threshold that needs three fixed simultaneously.

## A methodological scar worth keeping

A seven-point sweep on a 400-frame slice produced a clean, interpretable maximum at
z = -0.5 that **was not real** — it reversed sign on the full split. Section C.4 of the
[[Proposal]] already warns about selecting on noisy evidence; this is that trap, met on
our own data.

What did eventually work came from changing the source of the boxes, not post-processing
them: [[Label-Free Teacher]].
