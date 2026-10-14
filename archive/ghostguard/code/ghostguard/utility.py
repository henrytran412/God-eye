"""Counterfactual message utility.

    U(m | S) = R(F(S), y) - R(F(S u {m}), y)          positive = helpful

The proposal trains on U(m) = E_S[U(m | S)] with S drawn from sampled
coalitions (a Shapley-flavoured average). This module implements that, plus the
three other utilities you need in order to know whether that average is the
right training target at all:

  U_solo   = U(m | {})          value in isolation
  U_loo    = U(m | M \\ {m})     value given every other message was admitted
  U_greedy                      value at the moment a sequential policy decides

If E_S[U] does not agree in sign with the utility in the context where the
decision is actually taken, then a per-message gate trained on E_S[U] is
solving a different problem from the one it is deployed on. That is a
falsifiable claim about the method, and it is what these four quantities test.
"""
import numpy as np

DELTA = 0.05          # |U| below this counts as redundant / no-effect
HELPFUL, REDUNDANT, HARMFUL = 1, 0, -1


def coalition_labels(ctx, n_coalitions=16, p_incl=0.5, rs=None, score_mode="max"):
    """Monte-Carlo estimate of E_S[U(m|S)] and its spread across coalitions."""
    rs = rs or np.random.default_rng(0)
    n = ctx.n_msg
    if n == 0:
        return np.zeros(0), np.zeros(0), np.zeros(0, dtype=int)
    tot = np.zeros(n)
    sq = np.zeros(n)
    cnt = np.zeros(n, dtype=int)
    for _ in range(n_coalitions):
        mask = rs.random(n) < p_incl
        w = mask.astype(float)
        R_S = ctx.risk_of(w, score_mode=score_mode)
        for i in np.nonzero(~mask)[0]:
            w[i] = 1.0
            R_Si = ctx.risk_of(w, score_mode=score_mode)
            w[i] = 0.0
            u = R_S - R_Si
            tot[i] += u
            sq[i] += u * u
            cnt[i] += 1
    have = cnt > 0
    mean = np.zeros(n)
    std = np.zeros(n)
    mean[have] = tot[have] / cnt[have]
    var = np.zeros(n)
    var[have] = np.maximum(sq[have] / cnt[have] - mean[have] ** 2, 0.0)
    std[have] = np.sqrt(var[have])
    return mean, std, cnt


def solo_utility(ctx, score_mode="max"):
    n = ctx.n_msg
    out = np.zeros(n)
    if n == 0:
        return out
    R0 = ctx.risk_of(np.zeros(n), score_mode=score_mode)
    for i in range(n):
        w = np.zeros(n)
        w[i] = 1.0
        out[i] = R0 - ctx.risk_of(w, score_mode=score_mode)
    return out


def loo_utility(ctx, score_mode="max"):
    n = ctx.n_msg
    out = np.zeros(n)
    if n == 0:
        return out
    for i in range(n):
        w = np.ones(n)
        w[i] = 0.0
        R_wo = ctx.risk_of(w, score_mode=score_mode)
        out[i] = R_wo - ctx.risk_of(np.ones(n), score_mode=score_mode)
    return out


def greedy_oracle(ctx, score_mode="max", max_steps=None):
    """Sequential oracle: keep admitting the message with the largest positive
    marginal gain, in the context of what has already been admitted.

    This is the strongest per-message admission policy that exists for this
    risk function, so it upper-bounds what any gate could achieve. It also
    records U_greedy: the utility each message actually had at decision time.
    """
    n = ctx.n_msg
    w = np.zeros(n)
    u_at_decision = np.full(n, np.nan)
    if n == 0:
        return w, u_at_decision
    R_cur = ctx.risk_of(w, score_mode=score_mode)
    steps = max_steps if max_steps is not None else n
    for _ in range(steps):
        best, best_u = -1, 0.0
        for i in np.nonzero(w == 0)[0]:
            w[i] = 1.0
            u = R_cur - ctx.risk_of(w, score_mode=score_mode)
            w[i] = 0.0
            if u > best_u + 1e-12:
                best, best_u = int(i), u
        if best < 0:
            break
        w[best] = 1.0
        u_at_decision[best] = best_u
        R_cur -= best_u
    # messages never admitted: their gain in the final context
    for i in np.nonzero(w == 0)[0]:
        w[i] = 1.0
        u_at_decision[i] = R_cur - ctx.risk_of(w, score_mode=score_mode)
        w[i] = 0.0
    return w, u_at_decision


def classify(u, delta=DELTA):
    c = np.zeros_like(u, dtype=int)
    c[u > delta] = HELPFUL
    c[u < -delta] = HARMFUL
    return c
