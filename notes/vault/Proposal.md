---
title: Proposal
tags:
  - context
  - proposal
---

# Proposal

Davidson Student Scholars, AY2026-27. Mentor Prof. Kaikai Liu. Sources in
`proposal/`; cover-page documents stay in the gitignored `proposal/private/`.

Current title: *Which Component Fails When a Roadside Detector Moves?*

> [!danger] The framing is obsolete
> The synopsis says "detection and position largely survive while heading estimation
> collapses." [[Component Attribution]] contradicts both halves: detection is ~84% of
> the loss and heading contributes ~0.1%.

## What needs rewriting

- Title, synopsis, A.2, A.3, all of B
- C.3's repair list — two of its four are now measured negatives
  ([[Repair Attempts]]: INT8 recalibration hurts Car; the others never cross the threshold)
- C.5, which treats compression as the axis of interest

## What replaces it

A stronger result than the original: a systematic demonstration, each with a control,
that **nine label-free interventions cannot close a roadside cross-domain gap**, plus a
label-free teacher that recovers 4.2x without training ([[Label-Free Teacher]]). That is
the evidence-backed case for the compute the next stage needs, rather than asking on spec.
