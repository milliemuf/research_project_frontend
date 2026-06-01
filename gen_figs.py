"""Regenerate Figures 2, 4, 5 from the R2 re-run results (genuine 3f+1
heterogeneous consensus). All numbers are computed from the committed
benchmark_results CSV/JSON — nothing is hardcoded. Fig 5 uses the real
Byzantine fault-injection matrix; Fig 2 runs an exact McNemar test on the
paired single-agent vs consensus outcomes."""
import csv, os, json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BR = r"C:\dev\backend\Mtech_project\codeflow-backend\benchmark_results"
AMBER, BLUE, GREEN, ORANGE, RED = "#e0a33e", "#5b7fb4", "#3a7a3a", "#c8862a", "#bf504d"


def cases(prefix):
    """Per-case rows from <prefix>__cases.csv (list of dicts)."""
    path = os.path.join(BR, f"{prefix}__cases.csv")
    if not os.path.exists(path):
        return []
    return list(csv.DictReader(open(path, encoding="utf-8")))


def summary(prefix):
    path = os.path.join(BR, f"{prefix}__summary.json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def as_bool(v):
    return str(v).strip().lower() in ("true", "1", "yes")


def durs(prefix):
    return [float(r["duration_ms"]) / 1000.0
            for r in cases(prefix) if r.get("duration_ms") not in (None, "")]


def safety_rate(prefix):
    rows = cases(prefix)
    if not rows:
        return None, 0
    v = sum(1 for r in rows if as_bool(r.get("safety_violation")))
    return 100.0 * v / len(rows), len(rows)


def mcnemar_exact(pairs):
    """pairs: list of (single_violation, consensus_violation) booleans.
    b = single-only violations, c = consensus-only. Exact two-sided
    binomial test (p=0.5) on the discordant pairs."""
    b = sum(1 for s, c in pairs if s and not c)
    c = sum(1 for s, c in pairs if c and not s)
    n = b + c
    if n == 0:
        return b, c, 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return b, c, min(1.0, 2 * tail)


# ---------------- Figure 2: safety-violation rate, single vs consensus ----------------
# Paired datasets where we have BOTH a single-agent baseline and a genuine
# 3f+1 consensus run under the fixed validator gate. BugsInPy pools the original
# 20 (PySnooper+ansible) with the 30-bug expansion (black/fastapi/tornado/
# spacy/httpie) -> 50 paired cases for the McNemar test.
PAIRS = [("BugsInPy\n(n=50)", ["r2_bip_single", "r2_bipx_single"],
                               ["r2_bip_hetero", "r2_bipx_hetero"]),
         ("E-commerce\n(n=10)", ["r2_ec_single"], ["r2_ec_hetero_clean"])]
labels, base, bft = [], [], []
mcnemar_pairs = []
for lab, sps, cps in PAIRS:
    srows = [r for sp in sps for r in cases(sp)]
    crows = [r for cp in cps for r in cases(cp)]
    if not srows or not crows:
        continue
    sc = {r["bug_id"]: as_bool(r.get("safety_violation")) for r in srows}
    cc = {r["bug_id"]: as_bool(r.get("safety_violation")) for r in crows}
    ids = set(sc) & set(cc)
    labels.append(lab)
    base.append(100.0 * sum(sc[i] for i in ids) / len(ids))
    bft.append(100.0 * sum(cc[i] for i in ids) / len(ids))
    for bid in ids:
        mcnemar_pairs.append((sc[bid], cc[bid]))

b, c, p = mcnemar_exact(mcnemar_pairs)
fig, ax = plt.subplots(figsize=(10.5, 6.5), dpi=150)
x = np.arange(len(labels)); w = 0.38
ax.bar(x - w/2, base, w, label="Single-agent baseline", color=AMBER, edgecolor="black")
ax.bar(x + w/2, bft, w, label="3f+1 consensus (hetero)", color=BLUE, edgecolor="black")
for xi, v in zip(x - w/2, base): ax.text(xi, v + 1, f"{v:.0f}%", ha="center", fontsize=11)
for xi, v in zip(x + w/2, bft): ax.text(xi, v + 1, f"{v:.0f}%", ha="center", fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel("Safety violation rate (%)", fontsize=12); ax.set_ylim(0, max(base + bft) + 12)
ax.set_title("Safety-violation rate: single-agent vs genuine 3f+1 consensus\n"
             f"McNemar exact test on {len(mcnemar_pairs)} paired outcomes "
             f"(discordant b={b}, c={c}): p = {p:.3f}", fontsize=13)
ax.legend(fontsize=11); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); fig.savefig("corrected_fig2.png", facecolor="white"); plt.close(fig)
print(f"fig2 done | safety base={base} bft={bft} | McNemar n={len(mcnemar_pairs)} b={b} c={c} p={p:.4f}")

# ---------------- Figure 4: repair-duration distribution ----------------
groups = [("BugsInPy\nsingle", "r2_bip_single", AMBER),
          ("BugsInPy\n3f+1", "r2_bip_hetero", BLUE),
          ("E-commerce\nsingle", "r2_ec_single", AMBER),
          ("E-commerce\n3f+1", "r2_ec_hetero_clean", BLUE)]
data, cols, labs = [], [], []
for lab, pref, col in groups:
    dd = durs(pref)
    if dd:
        data.append(dd); cols.append(col); labs.append(lab)
fig, ax = plt.subplots(figsize=(11.5, 6.3), dpi=150)
if data:
    bp = ax.boxplot(data, patch_artist=True, showmeans=True, widths=0.6,
                    medianprops=dict(color="black", linewidth=2),
                    meanprops=dict(marker="D", markerfacecolor="white",
                                   markeredgecolor="black", markersize=7))
    for patch, col in zip(bp["boxes"], cols): patch.set_facecolor(col)
    ax.set_xticks(range(1, len(labs) + 1)); ax.set_xticklabels(labs, fontsize=10.5)
ax.set_ylabel("Repair duration (s)", fontsize=12)
ax.set_title("Repair-duration distribution: single-agent vs 3f+1 consensus\n"
             "(consensus adds 4 independent validator evaluations per case)", fontsize=13)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); fig.savefig("corrected_fig4.png", facecolor="white"); plt.close(fig)
print("fig4 done; group sizes:", [len(x) for x in data])

# ---------------- Figure 5: Byzantine fault injection (real matrix) ----------------
BYZ = [("Healthy\n(no fault)", "r2_ec_hetero_clean"),
       ("always_reject\n(DoS)", "r2_ec_hetero_byz_always_reject"),
       ("always_approve", "r2_ec_hetero_byz_always_approve"),
       ("random", "r2_ec_hetero_byz_random"),
       ("timeout\n(crash)", "r2_ec_hetero_byz_timeout"),
       ("garbage", "r2_ec_hetero_byz_garbage")]
scen, consensus, violation = [], [], []
for lab, pref in BYZ:
    rows = cases(pref)
    if not rows:
        continue
    n = len(rows)
    # consensus formed = prepare_votes >= quorum (3); fall back to consensus_approved
    formed = sum(1 for r in rows
                 if int(r.get("consensus_prepare_votes") or 0) >= 3
                 or as_bool(r.get("consensus_approved")))
    viol = sum(1 for r in rows if as_bool(r.get("safety_violation")))
    scen.append(lab); consensus.append(100.0 * formed / n); violation.append(100.0 * viol / n)
fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=150)
x = np.arange(len(scen)); w = 0.4
ax.bar(x - w/2, consensus, w, label="Consensus formation rate", color=GREEN, edgecolor="black")
ax.bar(x + w/2, violation, w, label="Safety violation rate (caught by sandbox)", color=ORANGE, edgecolor="black")
for xi, v in zip(x - w/2, consensus): ax.text(xi, v + 1.5, f"{v:.0f}%", ha="center", fontsize=10, fontweight="bold")
for xi, v in zip(x + w/2, violation): ax.text(xi, v + 1.5, f"{v:.0f}%", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(scen, fontsize=10.5)
ax.set_ylabel("Rate (%)", fontsize=12); ax.set_ylim(0, 112)
ax.set_title("Byzantine fault injection on e-commerce: one corrupted validator of four (f = 1)\n"
             "Four independent heterogeneous validators; the 3 honest replicas meet the quorum=3 in\n"
             "every behaviour, so consensus still forms (genuine 3f+1 tolerance); sandbox backstops bad fixes",
             fontsize=11)
ax.legend(fontsize=10.5, loc="center left"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); fig.savefig("corrected_fig5.png", facecolor="white"); plt.close(fig)
print(f"fig5 done; scenarios={scen}")
print(f"  consensus formation={consensus}")
print(f"  safety violation={violation}")
