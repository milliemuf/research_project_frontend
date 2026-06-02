"""
Figure 7 - genuine Byzantine fault tolerance: naive proposal-trust vs PBFT.

Reads the deterministic BFT simulation results
(backend benchmark_results/bft_demo__results.json) and renders the scenario
matrix. The headline cell is the equivocating primary: naive splits (red),
PBFT preserves safety (amber = correctly refuses to commit without a quorum).

Run with system python (has matplotlib): python gen_fig7.py
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BR = Path(r"C:\dev\backend\Mtech_project\codeflow-backend\benchmark_results")
rows = json.loads((BR / "bft_demo__results.json").read_text())["rows"]
by = {(r["fault"], r["protocol"]): r for r in rows}

ORDER = [
    ("clean", "Honest primary, no faults"),
    ("crash_f", "f = 1 replica crashed"),
    ("crash_f1", "f + 1 = 2 replicas crashed"),
    ("equivocate_validator", "Validator sends conflicting votes"),
    ("forgery", "Validator forges others' messages"),
    ("partition", "Network partition (no heal)"),
    ("partition_heal", "Network partition, then healed"),
    ("equivocate_primary", "MALICIOUS PRIMARY equivocates (X to some, Y to others)"),
]

GREEN, AMBER, RED = "#2E7D32", "#F9A825", "#C62828"

def cell(r):
    if r["safety_violated"]:
        return RED, "SAFETY VIOLATED\n(split-brain)"
    if r["progress"]:
        return GREEN, "agreed + progress"
    return AMBER, "safe, no progress\n(awaits view-change/heal)"

fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
ax.set_xlim(0, 3); ax.set_ylim(0, len(ORDER) + 1)
ax.axis("off")
ax.text(1.5, len(ORDER) + 0.55, "Naive proposal-trust", ha="center", fontweight="bold", fontsize=13)
ax.text(2.5, len(ORDER) + 0.55, "Genuine PBFT (this work)", ha="center", fontweight="bold", fontsize=13)
ax.text(0.02, len(ORDER) + 0.55, "Scenario", ha="left", fontweight="bold", fontsize=13)

for idx, (fault, label) in enumerate(ORDER):
    y = len(ORDER) - idx
    weight = "bold" if fault == "equivocate_primary" else "normal"
    ax.text(0.02, y + 0.5, label, ha="left", va="center", fontsize=10.5, fontweight=weight)
    for col, proto in ((1, "naive"), (2, "pbft")):
        color, text = cell(by[(fault, proto)])
        ax.add_patch(plt.Rectangle((col, y), 1, 1, facecolor=color, alpha=0.85,
                                   edgecolor="white", linewidth=2))
        ax.text(col + 0.5, y + 0.5, text, ha="center", va="center", color="white",
                fontsize=9, fontweight="bold")

ax.set_title("Genuine Byzantine fault tolerance: naive proposal-trust vs PBFT\n"
             "4 independent validators (f = 1, quorum = 3), signed messages, "
             "fault-injecting async network",
             fontsize=13, pad=18)
legend = [Patch(facecolor=GREEN, label="Agreement + progress"),
          Patch(facecolor=AMBER, label="Safety preserved, no progress (correct refusal)"),
          Patch(facecolor=RED, label="Safety violated (honest replicas commit different fixes)")]
ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, -0.13),
          ncol=1, fontsize=10, frameon=False)
plt.tight_layout()
fig.savefig("corrected_fig7.png", facecolor="white", bbox_inches="tight")
print("wrote corrected_fig7.png")
ep = by[("equivocate_primary", "naive")]
print("check: naive equivocate_primary safety_violated =", ep["safety_violated"],
      "values =", ep["committed_values"])
