"""Figure 6: f=2 Byzantine tight-bound. Prepare-vote count per scenario with the
quorum=5 threshold; shows consensus forming for <=f faults and collapsing at f+1.
All values read from the r2_f2_* result summaries (nothing hardcoded)."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BR = r"C:\dev\backend\Mtech_project\codeflow-backend\benchmark_results"
GREEN, RED, GREY = "#3a7a3a", "#bf504d", "#888888"


def load(p):
    f = os.path.join(BR, f"{p}__summary.json")
    return json.load(open(f)) if os.path.exists(f) else None


# Reject-side is the deterministic liveness demonstration.
SCEN = [("Healthy\n(0 faults)", "r2_f2_clean"),
        ("2 reject\n(= f)", "r2_f2_reject2"),
        ("3 reject\n(= f+1)", "r2_f2_reject3")]
labels, votes, formed = [], [], []
for lab, pref in SCEN:
    d = load(pref)
    if not d:
        continue
    pv = [int(c["consensus_prepare_votes"]) for c in d["per_case"]]
    n = len(pv)
    labels.append(lab)
    votes.append(np.mean(pv))
    formed.append(100.0 * sum(1 for v in pv if v >= 5) / n)

fig, ax = plt.subplots(figsize=(9.5, 6.3), dpi=150)
x = np.arange(len(labels))
colors = [GREEN if f > 0 else RED for f in formed]
bars = ax.bar(x, votes, 0.55, color=colors, edgecolor="black")
ax.axhline(5, color="black", linestyle="--", linewidth=1.8)
ax.text(len(labels) - 0.5, 5.12, "quorum = 2f+1 = 5", ha="right", fontsize=11, fontweight="bold")
ax.axhline(7, color=GREY, linestyle=":", linewidth=1.2)
ax.text(0.0, 7.08, "n = 3f+1 = 7 validators", ha="left", fontsize=9.5, color=GREY)
for xi, v, fm in zip(x, votes, formed):
    ax.text(xi, v + 0.12, f"{v:.0f} votes\n{fm:.0f}% form", ha="center", fontsize=10.5, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel("Prepare votes received (mean of 5 cases)", fontsize=12)
ax.set_ylim(0, 8)
ax.set_title("f = 2 Byzantine tolerance is tight: consensus survives f faults, collapses at f+1\n"
             "Honest validators that meet the quorum (5) form consensus; 3 (= f+1) rejecters leave\n"
             "only 4 honest votes < 5, so consensus provably cannot form (genuine 3f+1 bound)",
             fontsize=11)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); fig.savefig("corrected_fig6.png", facecolor="white"); plt.close(fig)
print(f"fig6 done | labels={labels} mean_votes={[round(v,1) for v in votes]} form%={formed}")
