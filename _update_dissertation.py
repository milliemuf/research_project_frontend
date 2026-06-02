"""
Update the MTech dissertation to the genuine-3f+1 / honest-numbers design, matching
the revised manuscript. Operates on a copy so the original is preserved.

  1. Flip old-narrative passages (2 validators -> 4 independent hetero validators;
     Wilcoxon p=0.0016 -> McNemar p=0.125 directional; 0% vs 11.1% -> 75% to 50%).
  2. Add Section 4.4.8: genuine BFT under an equivocating primary (the bft_sim proof).
  3. Append new source-code listings to Appendix G (bft_sim.py, bft_demo.py,
     test_bft_sim.py).
  4. Add new references (Dietterich 2000, Wang 2023, Maturi 2025, CISQ 2022).
"""
import copy, os, shutil
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

SRC = "PROJECT MTECH Software Engineering - ORIGINAL.docx"  # original preserved
DST = "PROJECT MTECH Software Engineering - UPDATED.docx"
BACKEND = r"C:\dev\backend\Mtech_project\codeflow-backend"

shutil.copyfile(SRC, DST)
d = docx.Document(DST)


def find_para(prefix):
    for p in d.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    raise KeyError(prefix)


def set_text(p, text):
    for child in list(p._p):
        if child.tag in (qn("w:r"), qn("w:hyperlink")):
            p._p.remove(child)
    p.add_run(text)


from docx.oxml import OxmlElement


def insert_paras_before(anchor, items):
    """Insert (text, style) paragraphs before `anchor` as CLEAN paragraphs
    (body text -> Normal style; headings -> the named style). Building fresh
    elements avoids inheriting the anchor's heading formatting."""
    for text, style in items:
        new_p = OxmlElement("w:p")
        anchor._p.addprevious(new_p)
        np = Paragraph(new_p, anchor._parent)
        np.style = d.styles[style] if style else d.styles["Normal"]
        np.add_run(text)


def insert_table_before(anchor, header, rows):
    """Insert a real Word table (Table Grid) immediately before `anchor`."""
    t = d.add_table(rows=1, cols=len(header)); t.style = "TableGrid"
    for j, h in enumerate(header):
        c = t.rows[0].cells[j]; c.text = ""; c.paragraphs[0].add_run(h).bold = True
    for row in rows:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = str(v)
    anchor._p.addprevious(t._tbl)
    return t


def _code_lines(path, max_lines=None):
    lines = open(path, encoding="utf-8").read().replace("\t", "    ").split("\n")
    if max_lines and len(lines) > max_lines:
        total = len(lines)
        lines = lines[:max_lines] + [
            "", f"    # ... [{total - max_lines} further lines omitted for brevity; "
                f"full {total}-line source in the released code repository]"]
    return lines


def _write_code(lines):
    from docx.shared import Pt as _Pt
    p = d.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = _Pt(0); pf.space_after = _Pt(0); pf.line_spacing = 1.0
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        r = p.add_run(line if line else " ")
        r.font.name = "Consolas"; r.font.size = _Pt(7.5)
    return p


def add_code_listing(title, path, max_lines=None):
    """Append a code-listing subsection (Heading 3 + monospace body) at doc end."""
    h = d.add_paragraph(); h.style = d.styles["Heading 31"]; h.add_run(title)
    _write_code(_code_lines(path, max_lines))


# ---------------------------------------------------------------- 1. fossil flips
set_text(find_para("Three agent types take part"),
    ("Three roles take part, each on a different LLM provider so the population is genuinely "
     "mixed. The analyzer (Anthropic Claude Sonnet) classifies the bug and proposes a type, "
     "severity and suggested approach but casts no vote; the healer and proposer (OpenAI "
     "GPT-4o) generates candidate fixes and likewise does not vote; and four independent, "
     "model-diverse validators (Claude-Haiku, GPT-4o-mini, llama3.1:8b and mistral:7b) each "
     "cast an independent accept or reject verdict. Because only the four validators vote, "
     "the voting population is genuinely independent, and a fix is approved when at least "
     "three of the four accept (the 2f + 1 = 3 quorum)."))

set_text(find_para("The consensus engine runs PBFT at a fault tolerance of f = 1"),
    ("The consensus engine runs PBFT at a fault tolerance of f = 1, which the n = 3f + 1 "
     "bound turns into four independent validator replicas and a commit quorum of three "
     "(2f + 1 = 3). The three phases, pre-prepare, prepare and commit, are each signed, the "
     "healer's single proposal is bound by a byte digest, and each validator votes "
     "independently. The fault-injection runs in this chapter corrupt how a validator votes, "
     "which the quorum masks; the defining Byzantine property — agreement when the proposer "
     "itself equivocates — is demonstrated separately on an independent-replica realisation "
     "of the protocol (Section 4.4.8)."))

set_text(find_para("Two complementary tests were run on the paired safety-violation outcomes"),
    ("McNemar's exact test is the primary test, the safety outcome being binary. All "
     "discordant pairs fall in the 20-bug BugsInPy subset, where the safety-violation rate "
     "fell from 75% under the single-agent baseline to 50% under BFT-MAS, with discordant "
     "pairs b = 6 (baseline violated, consensus did not) and c = 1 (the reverse), giving an "
     "exact two-sided p = 0.125: a directional reduction that does not reach significance at "
     "this sample size. The repair rate on the same subset rose from 25% to 50% (discordant "
     "6 to 1, p = 0.125), also directional. Across all 90 paired bugs the violation rate is "
     "16.7% for the baseline against 11.1% for consensus. We therefore rest the safety case "
     "on the deterministic Byzantine-tolerance results (Sections 4.4.5 and 4.4.8), which are "
     "provable rather than sampled, and report the paired repair and safety differences as "
     "directional."))

set_text(find_para("Mean pairwise validator agreement sat at about 0.97"),
    ("Mean pairwise validator agreement was near 1.00 on the easy synthetic bugs but fell to "
     "0.925 on the real BugsInPy bugs across the four cross-provider validators (1.00 means "
     "lockstep, 0.50 independent votes), so the validators agreed on obvious fixes yet "
     "diverged on harder ones, producing three genuine split votes in which Claude-Haiku "
     "dissented while the other three approved. The high agreement on easy bugs is a "
     "difficulty-ceiling effect: once a fix is obvious, any code-aware model finds it."))

set_text(find_para("To test the property the system is named for, one of the four agents was wrapped"),
    ("To test fault masking, one of the four independent validators was wrapped in the "
     "ByzantineWrapper and set to each of the five misbehaviours, leaving three honest "
     "validators. With the 2f + 1 = 3 quorum the three honest validators determine the "
     "outcome, so a single corrupted voter can neither force nor block a decision: liveness "
     "holds under always-reject and timeout, and safety holds under always-approve and "
     "random, where the lone corrupted accept never reaches the quorum by itself (Table 4.3). "
     "These runs corrupt only how a validator votes, which a majority quorum handles; the "
     "defining Byzantine case of an equivocating primary is demonstrated in Section 4.4.8."))

set_text(find_para("To take the optimal-count question head-on, the e-commerce dataset was rerun"),
    ("To take the optimal-count question head-on, the e-commerce dataset was rerun with seven "
     "independent validators instead of four, meeting the n = 3f + 1 = 7 constraint at f = 2 "
     "and so tolerating two simultaneous Byzantine validators; an f + 1 = 3 tight-bound check "
     "confirms that a third breaks consensus. Raising the count lowered raw success and "
     "raised latency with no safety gain, so n = 4 (f = 1) remains the practical optimum "
     "(Table 4.5)."))

set_text(find_para("This chapter has reported the study's empirical results"),
    ("This chapter has reported the study's empirical results. On the real-world subset the "
     "consensus pipeline directionally reduced the safety-violation rate, 75% to 50% (McNemar "
     "exact p = 0.125, not significant at this sample size), and raised the repair rate "
     "25% to 50%; across all 90 paired bugs the violation rate fell from 16.7% to 11.1%. The "
     "result the study rests on is deterministic: four independent validators tolerate one "
     "Byzantine voter across all five fault behaviours, an f = 2 study shows the bound is "
     "tight, and an independent-replica realisation preserves agreement under an equivocating "
     "primary where naive voting splits (Section 4.4.8). Repair quality is reported as "
     "preliminary, resting on a weak run-as-script oracle."))

set_text(find_para("When software breaks in a live e-commerce system"),
    ("When software breaks in a live e-commerce system, the bill arrives quickly, and a "
     "hand-written patch rarely ships fast enough to stop the bleeding. Multi-agent large-"
     "language-model (LLM) systems can now write plausible patches on their own, yet they "
     "talk their way to a decision and set no limit on how many agents may be confidently "
     "wrong before a bad fix is shipped. This project builds and tests BFT-MAS, a Byzantine "
     "fault-tolerant multi-agent system that adapts the Practical Byzantine Fault Tolerance "
     "(PBFT) protocol to a mixed group of LLM repair agents, backed by an isolated execution "
     "sandbox and e-commerce integrity checks. A Claude analyzer and a GPT-4o healer propose "
     "a fix that four independent, model-diverse validators (Claude-Haiku, GPT-4o-mini, "
     "llama3.1:8b and mistral:7b) then vote on under PBFT (n = 3f + 1 = 4, quorum = 3) before "
     "a sandbox stage, measured against a single-agent baseline on forty synthetic Python "
     "bugs, twenty real bugs from BugsInPy, and a thirty-bug e-commerce suite. The study "
     "demonstrates the core Byzantine property directly: on an independent-replica "
     "realisation, a malicious primary that equivocates makes a naive vote split the honest "
     "replicas onto different fixes, while the PBFT quorum certificates preserve agreement "
     "and reject forged messages; fault injection and an f = 2 study further show the quorum "
     "masks faulty votes up to the 3f + 1 bound. Repair results are reported as preliminary: "
     "on the real-world subset the unsafe-fix rate fell directionally from 75% to 50% and the "
     "repair rate rose from 25% to 50%, but neither reaches significance (McNemar exact "
     "p = 0.125) and the effect rests on a weak run-as-script oracle. The work delivers an "
     "open-source prototype, a repeatable harness, and the first empirical study of genuine "
     "BFT consensus applied to LLM-driven repair in e-commerce."))

set_text(find_para("Because each bug runs through both pipelines, the safety and success outcomes come in pairs"),
    ("Because each bug runs through both pipelines, the safety and success outcomes come in "
     "pairs. The safety outcome is binary, so McNemar's exact test on the discordant pairs is "
     "the primary test; the two-sided p-value and the discordant-pair counts (b, c) are "
     "reported. Because most pairs are concordant, the chi-squared approximation is avoided "
     "and the exact binomial form is used throughout. The significance threshold is 0.05."))

set_text(find_para("On BugsInPy the single-agent baseline fixes half the bugs"),
    ("On BugsInPy the single-agent baseline fixes 5 of the 20 bugs but accepts unsafe fixes "
     "the sandbox rejects on three-quarters of them. The consensus pipeline admits more "
     "genuine fixes, repairing 10 of 20 (recall 1.0 against the sandbox oracle), and where it "
     "approves an unsafe fix the sandbox catches it before commit. On the real-world subset "
     "this is a directional improvement on both axes — the unsafe-fix rate falls from 75% to "
     "50% and the repair rate rises from 25% to 50% (McNemar p = 0.125, not significant) — "
     "and across all 90 paired bugs the violation rate falls from 16.7% to 11.1%. Figure 4.1 "
     "puts the safety-violation contrast across the three datasets side by side."))

set_text(find_para("Next to the multi-agent LLM frameworks, ChatDev, MetaGPT, AutoGen and CAMEL"),
    ("Next to the multi-agent LLM frameworks, ChatDev, MetaGPT, AutoGen and CAMEL, the system "
     "swaps social coordination for a formal agreement protocol and reports the safety metric "
     "those frameworks leave out. MetaGPT's role-based voting is the nearest thing to "
     "consensus among them, but it does not meet the 3f + 1 bound and is not evaluated for "
     "safety; this work supplies both. Next to the repair systems, GenProg, SemFix, SapFix "
     "and the LLM-based methods, the system aims at the plausibility-correctness gap that "
     "Smith et al. (2015) documented: where those systems accept a fix that clears the "
     "available tests, this one demands a consensus of diverse agents and an independent "
     "sandbox run. The single-agent baseline here effectively stands in for those prior "
     "pipelines, and its higher unsafe-fix rate (75% on the real-world subset against the "
     "consensus pipeline's 50%) is the price of their missing safety check."))

set_text(find_para("The comparison is just as clear about where the system does not win"),
    ("The comparison is just as clear about the system's limits. On the easy synthetic and "
     "e-commerce sets the two modes are indistinguishable, and the repair results overall are "
     "preliminary: the safety and repair gains on real-world bugs are directional, not "
     "significant (McNemar p = 0.125), and rest on a weak run-as-script oracle. Its latency "
     "beats no single-agent method, and on model-diversity decorrelation it returned a "
     "negative result where some earlier multi-agent work quietly assumed a benefit. These "
     "honest comparisons fix the contribution precisely: the system moves the state of the "
     "art on Byzantine-tolerant consensus and on safety for high-stakes repair, not on "
     "throughput, speed, or any demonstrated diversity benefit."))

set_text(find_para("The project set out to design, build and empirically validate"),
    ("The project set out to design, build and empirically validate a Byzantine fault-"
     "tolerant multi-agent system for safe automated program repair in e-commerce systems, "
     "and it did. The central conclusion is that genuine consensus over independent, model-"
     "diverse LLM agents, backed by an executable check, preserves agreement under a "
     "Byzantine (equivocating) primary where naive voting splits — the property the system is "
     "named for, demonstrated rather than asserted. On real-world bugs the consensus pipeline "
     "directionally reduced the unsafe-fix rate from 75% to 50% and raised the repair rate "
     "from 25% to 50% (McNemar p = 0.125, not significant at this sample size); the "
     "deterministic Byzantine-tolerance results, not the sampled repair numbers, carry the "
     "central claim, and repair quality is reported honestly as preliminary."))

set_text(find_para("Reading each bug as a paired observation across the two modes"),
    ("Reading each bug as a paired observation across the two modes gives the four-way split "
     "in Table 4.2. The discordant pairs concentrate in the BugsInPy subset: in six bugs the "
     "consensus pipeline rejected an unsafe fix the baseline committed and the sandbox later "
     "proved wrong, while in one bug the reverse occurred, so the asymmetry favours consensus "
     "six to one rather than being absolute. The synthetic and e-commerce sets are "
     "concordant-clean in both modes, so all the discriminating signal lies in the BugsInPy "
     "bugs."))

set_text(find_para("On average the consensus pipeline runs about twice as slow"),
    ("On average the consensus pipeline runs about three times as slow as the baseline, with "
     "mean latencies of 44.5 seconds against 14.6 on the synthetic set, 155.6 against 39.9 on "
     "BugsInPy and 50.7 against 18.4 on the e-commerce set. The validator stage dominates the "
     "cost, since each CPU-bound Ollama validator takes thirty to forty seconds and they run "
     "concurrently, so the wall-clock cost is the slowest validator rather than their sum, "
     "but it is still the single biggest component. The consensus protocol itself adds under "
     "two milliseconds per round. The gap is widest on BugsInPy, where hard real bugs drive "
     "repeated repair attempts, each paying the full validator round. Figure 4.3 shows the "
     "distribution."))

set_text(find_para("To see whether stronger model heterogeneity moves the needle"),
    ("To see whether stronger model heterogeneity moves the needle, the default validator "
     "panel was made cross-provider (Claude-Haiku, GPT-4o-mini, llama3.1:8b and mistral:7b) "
     "and pairwise agreement computed across all validator pairs. Table 4.4 reports it. Mean "
     "pairwise agreement was near 1.00 on the easy synthetic bugs but fell to 0.925 on the "
     "real BugsInPy bugs, where three genuine split votes appeared with Claude-Haiku "
     "dissenting. The high agreement on easy bugs is an honest, partly negative result for "
     "the strong failure-decorrelation hypothesis: when a fix is obvious, validators from "
     "different families land on the same vote, and diversity only begins to tell on harder, "
     "ambiguous cases."))

# table-cell fossils
for _t in d.tables:
    for _r in _t.rows:
        for _c in _r.cells:
            tx = _c.text
            if "90 paired bugs, p=0.0016" in tx or "90 paired bugs, p = 0.0016" in tx:
                _c.text = ("BugsInPy 20 pairs, safety 75% to 50% (McNemar p = 0.125, n.s.); "
                           "BFT proven by the fault matrix and the equivocating-primary test")
            if "two validators" in tx:
                _c.text = tx.replace("two validators", "four independent validators")
            if "five validators" in tx:
                _c.text = tx.replace("five validators", "seven independent validators")
            if "paired Wilcoxon and McNemar tests reported" in tx:
                _c.text = tx.replace("paired Wilcoxon and McNemar tests reported",
                                     "McNemar's exact test reported")
            if tx.strip() == "Wilcoxon signed-rank test":
                _c.text = "McNemar's exact test"
            if "0.0016" in _c.text:
                _c.text = _c.text.replace("0.0016", "0.125")


# ---- result-data tables -> genuine-3f+1 numbers --------------------------------
def hdr(tb):
    return [c.text.strip() for c in tb.rows[0].cells]


def find_table(*tokens):
    for tb in d.tables:
        h = " ".join(hdr(tb))
        if all(tok in h for tok in tokens):
            return tb
    raise KeyError(tokens)

# Table 4.1 per-dataset: update BugsInPy + Overall (synthetic/e-commerce kept).
_pd = {
    ("BugsInPy (20)", "BFT-MAS consensus"):      ("0.500", "0.500", "155,600", "222,719", "0.667"),
    ("BugsInPy (20)", "Single-agent baseline"):  ("0.250", "0.750", "39,900",  "61,071",  "0.571"),
    ("Overall (90)", "BFT-MAS consensus"):       ("0.889", "0.111", "71,300",  "222,700", "0.889"),
    ("Overall (90)", "Single-agent baseline"):   ("0.833", "0.167", "21,500",  "61,100",  "0.833"),
}
t = find_table("Dataset (n)", "Mean lat. (ms)")
for r in t.rows[1:]:
    key = (r.cells[0].text.strip(), r.cells[1].text.strip())
    if key in _pd:
        for j, v in enumerate(_pd[key], start=2):
            r.cells[j].text = v

# Table 4.2 paired outcomes: 9 / 6 / 1 / 74.
t = find_table("Outcome", "Count", "Interpretation")
_po = [("Both pipelines violated", "9", "Hard real bugs where neither mode's fix passed the oracle"),
       ("Only baseline violated", "6", "Consensus caught an unsafe fix the single agent committed"),
       ("Only consensus violated", "1", "Consensus rejected or failed where the single agent passed"),
       ("Neither violated", "74", "Both handled cleanly (synthetic + e-commerce + 13 BugsInPy)")]
for i, (a, b, c) in enumerate(_po, start=1):
    t.rows[i].cells[0].text = a; t.rows[i].cells[1].text = b; t.rows[i].cells[2].text = c

# Table 4.3 Byzantine matrix: real f=1 data; n=10 throughout; add timeout row.
t = find_table("Scenario", "Consensus success", "Mean pairwise")
_bz = [("Healthy (no fault)", "10", "1.000", "0.000", "1.000"),
       ("always_reject (DoS)", "10", "1.000", "0.000", "0.500"),
       ("always_approve", "10", "1.000", "0.100", "1.000"),
       ("random", "10", "1.000", "0.100", "0.700"),
       ("garbage", "10", "1.000", "0.100", "0.500"),
       ("timeout / crash", "10", "0.900", "0.000", "0.500")]
for i, vals in enumerate(_bz, start=1):
    r = t.rows[i] if i < len(t.rows) else t.add_row()
    for j, v in enumerate(vals):
        r.cells[j].text = v

# Table 4.4 validator diversity -> decorrelation by difficulty.
t = find_table("Configuration", "Mean agreement", "Pairs")
_dv = [("Heterogeneous panel, easy synthetic bugs", "—", "—", "—", "1.00", "6"),
       ("Heterogeneous panel, real BugsInPy bugs", "10", "10", "0.500", "0.925", "6")]
for i, vals in enumerate(_dv, start=1):
    if i < len(t.rows):
        for j, v in enumerate(vals):
            t.rows[i].cells[j].text = v

# Table 4.5 validator-count latency: align latency to the n-sweep (53.3 / 71.3 s).
t = find_table("Configuration", "p50 latency", "Mean agreement")
_lat = {"n = 4": "53.3 s", "n = 7": "71.3 s"}
for r in t.rows[1:]:
    for k, v in _lat.items():
        if r.cells[0].text.strip().startswith(k):
            r.cells[4].text = v

# Objectives table O3 cell -> genuine-BFT framing.
for tb in d.tables:
    if hdr(tb)[:1] == ["Objective"]:
        for r in tb.rows[1:]:
            if r.cells[0].text.strip().startswith("O3"):
                r.cells[1].text = (
                    "Ninety paired bugs across three datasets; consensus tolerated one "
                    "Byzantine validator across five fault behaviours, an f = 2 study showed "
                    "the bound is tight, and an independent-replica realisation preserved "
                    "agreement under an equivocating primary where naive voting split "
                    "(Sections 4.4.5 to 4.4.8).")
        break

d.save(DST)
print("stage-1 flips + result tables done")

# ---------------------------------------------------------------- 2. Section 4.4.8
anchor = find_para("4.5 Proposed Model")
insert_paras_before(anchor, [
    ("4.4.8 Genuine Byzantine Fault Tolerance: Safety under an Equivocating Primary", "Heading 31"),
    (("The fault-injection runs above corrupt how a validator votes, which a majority quorum "
      "masks; they do not exercise the failure the Byzantine Generals problem is named for, a "
      "participant that lies inconsistently, telling different things to different peers. The "
      "hardest such participant is an equivocating primary: a malicious proposer that sends "
      "one fix to some validators and a different fix to others. To test this directly, an "
      "independent-replica realisation of the protocol was built in which four replicas "
      "exchange Ed25519-signed pre-prepare, prepare and commit messages over a network that "
      "can delay, drop and partition them, and was compared with a naive proposal-trust "
      "scheme that commits whatever proposal it receives. The simulation is deterministic and "
      "makes no language-model calls, so every outcome is exactly reproducible."), None),
    (("Under an equivocating primary the naive scheme is catastrophic: honest replicas receive "
      "different proposals and commit different fixes, a split-brain safety violation. The "
      "protocol prevents this, because committing requires a 2f + 1 quorum certificate on a "
      "single digest and any two such quorums share an honest replica that will not certify "
      "two different digests for the same slot, so no two honest replicas ever commit "
      "different fixes. It correctly makes no progress in that case until a new primary is "
      "elected (view-change, left to future work). The remaining scenarios confirm the "
      "design: a single equivocating validator and forged messages are rejected (a replica "
      "cannot impersonate another, so one Byzantine node cannot manufacture a quorum); f = 1 "
      "crash is tolerated while f + 1 = 2 is not; and a network partition blocks progress "
      "without ever causing a split, recovering once the partition heals."), None),
    (("Table 4.6 summarises the eight scenarios under both schemes. This is the demonstration "
      "that earns the Byzantine-fault-tolerant claim: the protocol preserves safety under the "
      "defining Byzantine fault, where naive voting fails. The evaluation is an emulated "
      "asynchronous network within a single host; liveness under primary failure (view-"
      "change) and a multi-host deployment are designed but left as future work, and the "
      "quality of the LLM repairs the protocol agrees on is the separate, preliminary "
      "question of Sections 4.4.1 to 4.4.2."), None),
    ("Table 4.6. Byzantine scenarios: naive proposal-trust vs genuine PBFT "
     "(four independent replicas, f = 1, quorum = 3).", None),
])
insert_table_before(anchor,
    ["Scenario", "Naive proposal-trust", "Genuine PBFT"],
    [["Honest primary, no faults", "agreed + progress", "agreed + progress"],
     ["f = 1 replica crashed", "agreed + progress", "agreed + progress"],
     ["f + 1 = 2 replicas crashed", "progresses (uncertified)", "safe, no progress"],
     ["Validator sends conflicting votes", "agreed + progress", "agreed + progress"],
     ["Validator forges others' messages", "agreed (forgeries rejected)", "agreed (forgeries rejected)"],
     ["Network partition (no heal)", "progresses (uncertified)", "safe, no progress"],
     ["Network partition, then healed", "agreed + progress", "agreed + progress"],
     ["Malicious primary EQUIVOCATES", "SPLIT-BRAIN (safety violated)", "safe (no split); awaits view-change"]])
insert_paras_before(anchor, [
    ("4.4.9 Cross-Language Evaluation on Java (Defects4J)", "Heading 31"),
    (("To test that the pipeline is not Python-specific, and to evaluate it against a real "
      "test oracle rather than the run-as-script proxy used on BugsInPy, the four-validator "
      "consensus pipeline was run on the Defects4J benchmark through its own checkout, "
      "compile and test harness in Docker. Correctness here is the project's actual JUnit "
      "suite passing, so a reported repair is genuinely verified, not merely plausible."), None),
    (("On commons-lang the four independent validators reached consensus on 8 of 9 evaluated "
      "bugs, but none passed the full Lang suite — a concrete measure of how hard real-world "
      "Java repair is. On commons-math the pipeline produced two genuine, full-suite-verified "
      "repairs, Math-3 (a unanimous 4-of-4 vote) and Math-5 (a 3-of-4 vote, with one "
      "validator dissenting on a fix that nevertheless passed the real suite), with consensus "
      "reached on all 9 evaluated bugs, and in every case no unverified fix was committed. "
      "The real oracle cleanly separates consensus robustness, which the Byzantine results "
      "establish, from repair capability, which on hard real Java bugs is modest and is "
      "reported honestly. The framework is otherwise language-agnostic: only the sandbox "
      "image and run command change."), None),
])
d.save(DST)
print("section 4.4.8 inserted")

# ---------------------------------------------------------------- 3. code listings
d.add_paragraph()  # spacer at end (after Appendix G.8)
add_code_listing("G.9 Genuine BFT Simulation (app/consensus/bft_sim.py)",
                 os.path.join(BACKEND, "app", "consensus", "bft_sim.py"))
add_code_listing("G.10 Byzantine Proof Experiments (benchmarks/bft_demo.py)",
                 os.path.join(BACKEND, "benchmarks", "bft_demo.py"))
add_code_listing("G.11 BFT Property Tests (tests/test_bft_sim.py)",
                 os.path.join(BACKEND, "tests", "test_bft_sim.py"))
add_code_listing("G.12 Real Defects4J (Java) Runner (benchmarks/defects4j_runner.py)",
                 os.path.join(BACKEND, "benchmarks", "defects4j_runner.py"), max_lines=370)
d.save(DST)
print("code listings G.9-G.11 appended")

# ---------------------------------------------------------------- 4. references
ref_head = find_para("REFERENCES")
existing = "\n".join(p.text for p in d.paragraphs)
new_refs = [
    ("Consortium for Information & Software Quality (CISQ). (2022). The cost of poor software "
     "quality in the US: A 2022 report. https://www.it-cisq.org/", "CISQ"),
    ("Dietterich, T. G. (2000). Ensemble methods in machine learning. In Multiple Classifier "
     "Systems, LNCS 1857 (pp. 1-15). Springer.", "Dietterich"),
    ("Maturi, M. H., De La Cruz, E., Addula, S. R., et al. (2025). Enhancing smart contract "
     "security with explainable AI: A framework for re-entrancy vulnerability detection and "
     "explanation. In 2025 IEEE SIEDS. IEEE.", "Maturi"),
    ("Wang, X., Wei, J., Schuurmans, D., et al. (2023). Self-consistency improves chain-of-"
     "thought reasoning in language models. In ICLR.", "Wang, X."),
]
# insert after the REFERENCES heading (alphabetical-ish: just append at end of section)
anchorA = None
for p in d.paragraphs:  # the REAL heading (Heading 1), not the table-of-contents entry
    if p.text.strip().startswith("APPENDIX A") and p.style.name == "Heading 1":
        anchorA = p; break
if anchorA is None:
    for p in d.paragraphs:
        if p.text.strip().startswith("APPENDIX A"):
            anchorA = p
added = 0
for text, key in new_refs:
    if key not in existing:
        insert_paras_before(anchorA, [(text, None)])
        added += 1
d.save(DST)
print(f"references added: {added}")

# ---------------------------------------------------------------- 5. Appendix F per-case
import csv as _csv


def _outcome(r):
    succ = r["success"] == "True"
    appr = r.get("consensus_approved") == "True"
    sb = r.get("sandbox_passed") == "True"
    if succ:
        return "Approved and sandbox-validated"
    if appr and not sb:
        return "Approved, sandbox rejected"
    if not appr and r.get("consensus_approved") not in (None, ""):
        return "Rejected at consensus"
    return r.get("final_stage", "")


def rebuild_percase(table_index, csv_name):
    rows = list(_csv.DictReader(
        open(os.path.join(BACKEND, "benchmark_results", csv_name), newline="", encoding="utf-8")))
    tb = d.tables[table_index]
    while len(tb.rows) - 1 < len(rows):
        tb.add_row()
    for i, r in enumerate(rows, start=1):
        cells = tb.rows[i].cells
        dur = f"{float(r['duration_ms'])/1000:.1f}" if r.get("duration_ms") else "--"
        vals = [r["bug_id"], "Yes" if r["success"] == "True" else "No",
                "Yes" if r.get("safety_violation") == "True" else "No", dur, _outcome(r)]
        for j, v in enumerate(vals):
            cells[j].text = v


# T26 BugsInPy consensus, T27 BugsInPy baseline, T31-T34 Byzantine scenarios.
rebuild_percase(26, "r2_bip_hetero__cases.csv")
rebuild_percase(27, "r2_bip_single__cases.csv")
rebuild_percase(31, "r2_ec_hetero_byz_always_reject__cases.csv")
rebuild_percase(32, "r2_ec_hetero_byz_always_approve__cases.csv")
rebuild_percase(33, "r2_ec_hetero_byz_random__cases.csv")
rebuild_percase(34, "r2_ec_hetero_byz_garbage__cases.csv")
d.save(DST)
print("Appendix F per-case tables rebuilt (BugsInPy + Byzantine)")

# ---------------------------------------------------------------- 6. refresh G.1-G.8
def refresh_listing(prefix, filepath, max_lines=None):
    hp = None
    for p in d.paragraphs:
        if p.text.strip().startswith(prefix):
            hp = p; break
    if hp is None:
        print("WARN: listing heading not found:", prefix); return
    # delete following paragraphs (old code) until the next heading or a table
    el = hp._p.getnext()
    while el is not None:
        nxt = el.getnext()
        if el.tag == qn("w:p"):
            para = Paragraph(el, hp._parent)
            if para.style.name in ("Heading 31", "Heading 21", "Heading 1") or \
               para.text.strip().startswith("APPENDIX"):
                break
            el.getparent().remove(el)
        elif el.tag == qn("w:tbl"):
            break
        el = nxt
    # build new (tight, optionally truncated) code paragraph after the heading
    p = _write_code(_code_lines(filepath, max_lines))
    hp._p.addnext(p._p)


for _pfx, _fp in [
    ("G.1 PBFT Consensus Engine", "app/consensus/pbft.py"),
    ("G.2 Consensus Cryptography", "app/consensus/crypto.py"),
    ("G.3 Byzantine Fault-Injection Wrapper", "app/agents/byzantine_wrapper.py"),
    ("G.4 Base Agent Abstraction", "app/agents/base_agent.py"),
    ("G.5 Validator Agent", "app/agents/validator_agent.py"),
    ("G.6 Repair Pipeline", "app/repair/repair_pipeline.py"),
    ("G.7 Single-Agent Baseline Pipeline", "app/repair/single_agent_pipeline.py"),
    ("G.8 Isolated Sandbox Executor", "app/sandbox/docker_executor.py"),
]:
    refresh_listing(_pfx, os.path.join(BACKEND, _fp), max_lines=370)
d.save(DST)
print("G.1-G.8 listings refreshed to current code")
print("WROTE", DST)
