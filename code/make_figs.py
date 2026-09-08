"""Figures for the design review.

Two questions get a picture, because both are comparisons of curves that a
table cannot show at a glance:

  fig1  benefit vs harm, one curve per gating family, per attack condition.
        This is the fair comparison: every family swept across its own
        operating range, so no method is judged at someone else's threshold.
  fig2  conformal risk control: realised risk against the target alpha, per
        condition, and what the target costs in admitted evidence.

Identity is carried by a figure-level legend rather than end-of-curve labels:
the curves converge at their high ends (which is itself a finding), so labels
placed there collide.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e6e5e1"
S1, S2, S3, S4, S5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": GRID, "axes.linewidth": 1.0,
    "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.titlesize": 9.5, "axes.titleweight": "bold",
    "grid.color": GRID, "grid.linewidth": 0.8,
    "legend.frameon": False, "legend.fontsize": 8.4,
})


def style(ax):
    ax.set_axisbelow(True)
    ax.grid(True, alpha=0.9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def handle(color, marker="o", ms=6):
    return Line2D([], [], color=color, marker=marker, lw=2.0, ms=ms,
                  mec=SURFACE, mew=1.4)


# ------------------------------------------------------------------ fig 1

def fig_tradeoff():
    df = pd.read_csv(os.path.join(RES, "tradeoff.csv"))
    conds = ["none", "spoof", "collusion"]
    titles = {"none": "Benign traffic",
              "spoof": "Single-source fabrication",
              "collusion": "Two colluding senders"}
    fams = [("confidence", S1, "confidence threshold"),
            ("gate_umarg", S2, "gate trained on $E_S[U(m|S)]$"),
            ("gate_usolo", S3, "gate trained on $U(m\\,|\\,\\varnothing)$")]
    refs = [("naive_lf", "s", "accept every message"),
            ("cad_like", "^", "occupancy-consistency check"),
            ("oracle_greedy", "*", "counterfactual oracle")]

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.0), sharey=True)
    for ax, cond in zip(axes, conds):
        style(ax)
        sub = df[df.condition == cond]
        for fam, col, _ in fams:
            f = sub[sub.family == fam].sort_values("harm_rate")
            if f.empty:
                continue
            ax.plot(f.harm_rate, f.benefit_rate, "-o", color=col, lw=2.0,
                    ms=5.0, mec=SURFACE, mew=1.4, zorder=3, clip_on=False)
        for nm, mk, _ in refs:
            p = sub[sub.family == nm]
            if p.empty:
                continue
            ax.plot(p.harm_rate, p.benefit_rate, mk, color=MUTED,
                    ms=13 if mk == "*" else 8, mec=SURFACE, mew=1.4,
                    zorder=4, clip_on=False)
        ax.set_title(titles[cond], color=INK, loc="left")
        ax.set_xlabel("harm rate\nshare of admitted messages that assert a\nnon-existent object")
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(-0.03, 1.05)
    axes[0].set_ylabel("benefit rate\nshare of remote-only objects admitted")

    fig.suptitle("Up and to the left is better: benefit kept per unit of harm admitted",
                 x=0.006, y=0.985, ha="left", fontsize=11.5, weight="bold", color=INK)
    fig.legend([handle(c) for _, c, _ in fams] +
               [handle(MUTED, mk, 12 if mk == "*" else 7) for _, mk, _ in refs],
               [l for _, _, l in fams] + [l for _, _, l in refs],
               loc="upper left", bbox_to_anchor=(0.005, 0.955), ncol=3,
               columnspacing=1.6, handletextpad=0.5, labelcolor=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.855))
    out = os.path.join(RES, "fig1_benefit_vs_harm.png")
    fig.savefig(out, dpi=170)
    print("wrote", out)


# ------------------------------------------------------------------ fig 2

def fig_crc():
    df = pd.read_csv(os.path.join(RES, "crc_alpha_sweep.csv"))
    conds = [("none", S1, "benign (calibration domain)"),
             ("degraded", S2, "sensor degraded"),
             ("removal", S3, "message withholding"),
             ("spoof", S4, "fabrication"),
             ("collusion", S5, "collusion")]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6))
    a = df.alpha.values
    dead = df.lam_hat.values <= 0
    a_dead = a[dead].max() if dead.any() else None

    ax = axes[0]
    style(ax)
    if a_dead is not None:
        ax.axvspan(a.min() - 0.02, a_dead + 0.005, color="#f0efeb", zorder=0)
        ax.annotate("no feasible threshold:\nCRC rejects every message,\n"
                    "so realised risk is 0 and\nso is every benefit",
                    (0.062, 0.60), fontsize=7.8, color=INK2, va="top")
    ax.plot([0.02, 0.56], [0.02, 0.56], "--", color=MUTED, lw=1.4, zorder=2)
    ax.annotate("target: risk $=\\alpha$", (0.50, 0.505), rotation=30,
                fontsize=7.6, color=INK2, ha="center", va="bottom",
                rotation_mode="anchor")
    for c, col, _ in conds:
        ax.plot(a, df[f"risk_{c}"].values, "-o", color=col, lw=2.0, ms=5.0,
                mec=SURFACE, mew=1.4, zorder=3, clip_on=False)
    ax.set_xlabel("target risk level  $\\alpha$")
    ax.set_ylabel("realised risk on test traffic")
    ax.set_title("Calibrated on benign traffic, tested everywhere",
                 color=INK, loc="left")
    ax.set_xlim(0.03, 0.57)
    ax.set_ylim(-0.02, 0.82)

    ax = axes[1]
    style(ax)
    if a_dead is not None:
        ax.axvspan(a.min() - 0.02, a_dead + 0.005, color="#f0efeb", zorder=0)
    for col, key, lab in [(S1, "benefit_rate", "remote-only objects kept"),
                          (S3, "accept_rate", "messages admitted")]:
        ax.plot(a, df[key].values, "-o", color=col, lw=2.0, ms=5.0,
                mec=SURFACE, mew=1.4, clip_on=False, zorder=3, label=lab)
    ax.legend(loc="upper left", labelcolor=INK2)
    ax.set_xlabel("target risk level  $\\alpha$")
    ax.set_ylabel("rate")
    ax.set_xlim(0.03, 0.57)
    ax.set_ylim(-0.03, 1.05)
    ax.set_title("What the target costs in discarded evidence",
                 color=INK, loc="left")

    fig.legend([handle(c) for _, c, _ in conds], [l for _, _, l in conds],
               loc="lower left", bbox_to_anchor=(0.045, 0.0), ncol=3,
               columnspacing=1.6, handletextpad=0.5, labelcolor=INK2)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    out = os.path.join(RES, "fig2_crc.png")
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    fig_tradeoff()
    fig_crc()
