"""Conformal risk control for the nested accept / soft-fuse / quarantine / reject
action set.

Angelopoulos et al., "Conformal Risk Control" (ICLR 2024): if the per-instance
loss L_i(lambda) is monotone in lambda, right-continuous and bounded by B, then

    lambda_hat = inf { lambda : R_hat_n(lambda) <= alpha - (B - alpha)/n }

gives E[L_{n+1}(lambda_hat)] <= alpha.

Two things the proposal has to get right and which this module makes explicit:

1. MONOTONICITY. The theorem needs a per-instance monotone loss. "Excess risk
   over ego-only" is NOT monotone in the permissiveness of the gate -- admitting
   more messages usually lowers risk -- so it cannot be the CRC loss even though
   it is the quantity we care about. What IS monotone is the count of admitted
   ghost-inducing messages, and that is what we control. `check_monotone`
   verifies this empirically rather than assuming it.

2. EXCHANGEABILITY. The guarantee holds only if calibration and test data are
   exchangeable. An adversary chooses the test distribution, so the guarantee
   provably does not extend to attacked traffic. That is not a fixable detail;
   it bounds what the contribution can claim.
"""
import numpy as np


def crc_threshold(losses, alpha, B=1.0):
    """losses: (n_cal, n_lambda), non-decreasing along axis 1 (more permissive).

    Returns the index of the most permissive lambda whose empirical risk still
    satisfies the CRC bound, or -1 if none does (fall back to full rejection).
    """
    n = losses.shape[0]
    Rhat = losses.mean(axis=0)
    bound = alpha - (B - alpha) / n
    ok = np.nonzero(Rhat <= bound)[0]
    return (int(ok[-1]) if ok.size else -1), Rhat, bound


def check_monotone(losses, tol=1e-9):
    """Fraction of calibration instances whose loss curve is non-decreasing."""
    d = np.diff(losses, axis=1)
    per_instance_ok = (d >= -tol).all(axis=1)
    return float(per_instance_ok.mean()), float((d < -tol).mean())


def nested_actions(p_harm, sigma, lam_reject, lam_quar, lam_soft,
                   sigma_gate=None, soft_weight=0.4):
    """Map gate outputs to a fusion weight per message.

    Nested by construction: the reject region contains the quarantine region
    contains the soft-fuse region, so the action set is monotone in lambda and
    a single scalar lambda can index it.

    weight 1.0 = accept, `soft_weight` = soft-fuse, 0.0 = reject.
    Quarantine returns weight 0 for this frame but is reported separately,
    because its cost is a delay, not a rejection.
    """
    w = np.ones(len(p_harm))
    quarantined = np.zeros(len(p_harm), dtype=bool)
    w[p_harm >= lam_soft] = soft_weight
    q = (p_harm >= lam_quar) & (p_harm < lam_reject)
    quarantined |= q
    w[q] = 0.0
    w[p_harm >= lam_reject] = 0.0
    if sigma_gate is not None:
        # high predictive uncertainty -> quarantine rather than commit
        unres = (sigma >= sigma_gate) & (w > 0)
        quarantined |= unres
        w[unres] = 0.0
    return w, quarantined
