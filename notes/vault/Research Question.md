---
title: Research Question
tags:
  - core
---

# Research Question

> [!question] The question
> Does domain fragility in roadside 3D perception concentrate in specific network
> components, and can the fragile component be repaired using only unlabeled
> target data?

A roadside detector is trained at one intersection and deployed at another. Published
accuracy is measured on the training distribution; deployment is not.

What makes the roadside case distinct from the vehicle-mounted literature: the sensor
is **static**, has no ego-motion, and in single-frame deployment has no trajectory cue
— precisely the cue detectors are shown to rely on for heading.

## Why it matters

A missed detection is a failure downstream planners tolerate. A confident *wrong*
heading is not: heading feeds motion prediction. At 15 m/s over a 3 s horizon, the
measured heading spread moves a predicted position by **~8.6 m**, about two and a half
lane widths.

See [[Domain Shift]] for what was measured, and [[Proposal]] for the framing that
needs rewriting.
