"""Regenerate Figure 1 (BFT-MAS pipeline) with the CORRECT model strings."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(11.9, 6.9), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

COL = {
    "blue":   ("#d6e4f2", "#3f6fa5"),
    "orange": ("#fdecca", "#d39a3c"),
    "green":  ("#d9ead3", "#4a7a3a"),
    "pink":   ("#f6cfce", "#bf504d"),
    "purple": ("#e6d6f3", "#7d5ba6"),
}

def box(cx, cy, w, h, color, lines, bold_first=True, fs=9.5):
    fc, ec = COL[color]
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0.4,rounding_size=1.2", linewidth=1.4,
        facecolor=fc, edgecolor=ec, mutation_aspect=0.6))
    # Header (first line) bold near the top; remaining lines stacked below.
    hy = cy + h/2 - 2.3
    ax.text(cx, hy, lines[0], ha="center", va="center",
            fontsize=fs + (1.0 if bold_first else 0),
            fontweight=("bold" if bold_first else "normal"), color="#111")
    if len(lines) > 1:
        ax.text(cx, hy - 2.7, "\n".join(lines[1:]), ha="center", va="top",
                fontsize=fs, color="#1a1a1a", linespacing=1.4)

def arrow(x1, y1, x2, y2, color="#555"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=14, linewidth=1.5,
        color=color, shrinkA=2, shrinkB=2))

# Title
ax.text(50, 97, "BFT-MAS Code-Repair Pipeline", ha="center", va="center",
        fontsize=16, fontweight="bold", color="#111")
ax.text(50, 91.5, "Analyzer + Healer (proposer) → 4 independent heterogeneous "
        "validators → PBFT consensus → Sandbox → Decision", ha="center", va="center",
        fontsize=10, style="italic", color="#666")

# Boxes — genuine 3f+1: four INDEPENDENT cross-provider validators vote; the
# Healer is the proposer (no vote) and the Analyzer feeds context (no vote).
box(9, 74, 15, 13, "blue",  ["Bug report", "(error msg,", "stack trace,", "code context)"], bold_first=False)
box(30, 74, 16, 13, "blue",  ["ANALYZER", "Claude Sonnet 4.5", "(feeds context,", "does not vote)"])
box(52, 74, 15, 13, "blue",  ["HEALER", "GPT-4o", "(proposer,", "does not vote)"])
box(87, 88, 19, 8.4, "orange",["VALIDATOR 1 · Claude Haiku"], bold_first=True, fs=8.3)
box(87, 78.6, 19, 8.4, "orange",["VALIDATOR 2 · GPT-4o-mini"], bold_first=True, fs=8.3)
box(87, 69.2, 19, 8.4, "orange",["VALIDATOR 3 · llama3.1:8b (local)"], bold_first=True, fs=8.3)
box(87, 59.8, 19, 8.4, "orange",["VALIDATOR 4 · mistral:7b (local)"], bold_first=True, fs=8.3)
box(13, 47, 19, 15, "purple",["MEASUREMENT", "throughput · p50 · p99", "success rate",
                              "safety violation rate", "validator agreement"])
box(53, 47, 32, 15, "green", ["PBFT THREE-PHASE CONSENSUS", "pre-prepare → prepare → commit",
                              "f = 1, quorum = 3 of 4 validators", "(2 cloud + 2 local, independent)"])
box(53, 25, 29, 11, "pink",  ["SANDBOX EXECUTION", "Docker (or subprocess fallback)",
                              "→ exit code, stdout/stderr, runtime"])
box(20, 8, 23, 10, "green",  ["APPLY FIX  [PASS]", "(consensus + sandbox both passed)"])
box(82, 8, 23, 10, "pink",   ["REJECT  [FAIL]", "(safety violation, rollback)"])

# Arrows
arrow(16.5, 74, 22, 74)        # bug -> analyzer
arrow(38, 74, 44.5, 74)        # analyzer -> healer
arrow(59.5, 75.5, 77.5, 88)    # healer -> val1
arrow(59.5, 74.5, 77.5, 78.6)  # healer -> val2
arrow(59.5, 73, 77.5, 69.2)    # healer -> val3
arrow(59.5, 72, 77.5, 59.8)    # healer -> val4
arrow(77.5, 88, 69.5, 53)      # val1 -> pbft
arrow(77.5, 78.6, 69, 49)      # val2 -> pbft
arrow(77.5, 69.2, 69, 46)      # val3 -> pbft
arrow(77.5, 59.8, 69.5, 43)    # val4 -> pbft
arrow(30, 67.5, 44, 53)        # analyzer context -> pbft
arrow(22.5, 47, 37, 47, color="#7d5ba6")   # measurement -> pbft
arrow(53, 39.5, 53, 30.5)      # pbft -> sandbox
arrow(45, 20, 28, 13)          # sandbox -> apply
arrow(61, 20, 78, 13)          # sandbox -> reject

plt.tight_layout(pad=0.3)
fig.savefig("corrected_fig1.png", dpi=300, bbox_inches="tight", facecolor="white")
print("wrote corrected_fig1.png")
from PIL import Image
print("size:", Image.open("corrected_fig1.png").size)
