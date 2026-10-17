---
title: Index
tags:
  - moc
---

# God-eye — research vault

What fails when a roadside 3D detector is deployed at an intersection it was never
trained on, and can it be repaired without labels there.

> [!abstract] The one-line result
> Detection does not degrade gracefully: Car accuracy falls **69.70 -> 1.83**. No
> single component explains it, nine training-free repairs recovered nothing, and a
> label-free teacher built from a frozen 2D model plus raw LiDAR gets Car to
> **27.21** centre-distance AP without training or target labels.

## Start here

- [[Research Question]] — what is actually being asked
- [[Domain Shift]] — the collapse, measured
- [[Component Attribution]] — which part breaks, and why "orientation" was wrong
- [[Metrics]] — ==read this before quoting any number==
- [[Repair Attempts]] — nine things that did not work
- [[Label-Free Teacher]] — the thing that did
- [[Corrections]] — claims this project made and then withdrew
- [[Open Questions]] — what comes next

## Context

- [[Datasets]] · [[Jetson]] · [[Proposal]]

## Map

![[Research Map.canvas]]
