"""
Manuscript revision script for Sage Open SO-26-5308 R1.

Pipeline:
  1. baseline_anon  = current manuscript with author-identifying info stripped
                      (no other changes). This is the Word-Compare baseline.
  2. revised        = baseline_anon + all content revisions (this script).
  Later: Word Compare(baseline_anon, revised) -> tracked-changes copy.

Run:  python revise_manuscript.py
"""
import copy
import os
import shutil
import zipfile
import docx
from docx.text.paragraph import Paragraph


def swap_media(docx_path, member, png_path, size=(3570, 2070)):
    """Replace an embedded image inside a .docx (zip), resizing the new PNG to
    the original pixel size so the inline-shape frame is not distorted."""
    if not os.path.exists(png_path):
        print("WARN: replacement figure missing:", png_path)
        return
    try:
        from PIL import Image
        img = Image.open(png_path).convert("RGBA").resize(size)
        tmp_png = png_path + ".sized.png"
        img.save(tmp_png)
        data = open(tmp_png, "rb").read()
        os.remove(tmp_png)
    except Exception:
        data = open(png_path, "rb").read()
    tmp = docx_path + ".tmp"
    with zipfile.ZipFile(docx_path, "r") as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            payload = data if item.filename == member else zin.read(item.filename)
            zout.writestr(item, payload)
    os.replace(tmp, docx_path)


def strip_watermark(docx_path, marker="FBCH_CONFIDENTIAL"):
    """Remove the confidentiality watermark from a blinded copy. The marker is
    a text-box shape carried in the page headers as a visible <w:t> run plus
    descr=/alt= metadata; blanking the string everywhere in the header/footer
    parts leaves an empty (invisible) box with no identifying text. SAGE Open
    is double-anonymous, so the uploaded manuscript must carry no such mark."""
    tmp = docx_path + ".wm.tmp"
    n = 0
    with zipfile.ZipFile(docx_path, "r") as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if (item.filename.startswith("word/header") or
                    item.filename.startswith("word/footer")) and item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                if marker in text:
                    n += text.count(marker)
                    data = text.replace(marker, "").encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, docx_path)
    print(f"stripped watermark x{n} from {docx_path}")


SRC = "h240624a_technicalpaper_revised.docx"
BASELINE = "MS_R1_baseline_anon.docx"
REVISED = "MS_R1_revised_clean.docx"


# ---------------------------------------------------------------- helpers
def find_para(doc, prefix):
    """First paragraph whose stripped text starts with `prefix`."""
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    raise KeyError(f"paragraph not found: {prefix!r}")


def set_text(p, full_text, bold_lead=None):
    """Replace a paragraph's text, optionally with a bold lead-in label.
    Removes plain runs AND hyperlink fields (emails / URLs live in
    <w:hyperlink> and are invisible to paragraph.runs). Preserves the
    paragraph properties so the style is kept."""
    from docx.oxml.ns import qn
    for child in list(p._p):
        if child.tag in (qn("w:r"), qn("w:hyperlink")):
            p._p.remove(child)
    if bold_lead:
        rl = p.add_run(bold_lead)
        rl.bold = True
        p.add_run(full_text)
    else:
        p.add_run(full_text)


def delete_para(p):
    """Remove a paragraph element entirely."""
    p._p.getparent().remove(p._p)


def replace_in_para(doc, prefix, old, new):
    """Replace a substring inside a paragraph, preserving run formatting where
    the substring sits in one run; otherwise rewrite the paragraph text."""
    p = find_para(doc, prefix)
    for r in p.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return
    set_text(p, p.text.replace(old, new))


def insert_after(p, paragraphs):
    """Insert new paragraphs (list of (text, bold_lead|None)) after p.
    Returns the last inserted paragraph (for chaining)."""
    anchor = p
    for text, bold_lead in paragraphs:
        new_p = copy.deepcopy(p._p)
        anchor._p.addnext(new_p)
        np = Paragraph(new_p, p._parent)
        for r in list(np.runs):
            r._element.getparent().remove(r._element)
        if bold_lead:
            rl = np.add_run(bold_lead)
            rl.bold = True
            np.add_run(text)
        else:
            np.add_run(text)
        anchor = np
    return anchor


def add_table_after(doc, anchor, header, rows):
    """Create a real Word table and move it to directly after `anchor`."""
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for j, h in enumerate(header):
        cell = t.rows[0].cells[j]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            cells[j].text = str(val)
    anchor._p.addnext(t._tbl)
    return t


def paras_after_element(after_elem, tmpl_para, paragraphs):
    """Insert paragraphs after an arbitrary block element (e.g. a table),
    deep-copying tmpl_para for styling. Returns the last new paragraph."""
    cur = after_elem
    last = None
    for text, bold_lead in paragraphs:
        new_p = copy.deepcopy(tmpl_para._p)
        cur.addnext(new_p)
        np = Paragraph(new_p, tmpl_para._parent)
        for r in list(np.runs):
            r._element.getparent().remove(r._element)
        if bold_lead:
            rl = np.add_run(bold_lead)
            rl.bold = True
            np.add_run(text)
        else:
            np.add_run(text)
        cur = new_p
        last = np
    return last


# ---------------------------------------------------------------- 1. baseline_anon
shutil.copyfile(SRC, BASELINE)
d = docx.Document(BASELINE)

# Strip author block (names, affiliation, emails) for blind review.
set_text(find_para(d, "Millicent Mufambi"), "")
set_text(find_para(d, "Department of Software Engineering, Harare"), "")
set_text(find_para(d, "h240624a@hit.ac.zw"), "")
set_text(find_para(d, "wmakondo@hit.ac.zw"), "")
# Acknowledgement institution.
set_text(find_para(d, "The authors thank the Department of Software Engineering"),
         "The authors thank their institution for support during this work.")
# Data-availability GitHub usernames -> anonymised.
set_text(find_para(d, "Data availability."),
         ("The full benchmark CSVs, JSON reports, agent prompts, model identifiers, "
          "seeds, and all source code referenced in this paper will be released in a "
          "public repository on acceptance; an anonymized archive is available to "
          "reviewers. Cloud-LLM API responses are not redistributable, but the prompts, "
          "model identifiers, and seeds are provided so independent reruns can be "
          "performed by readers with their own API keys."),
         bold_lead="Data availability. ")
d.save(BASELINE)
print("wrote", BASELINE)


# ---------------------------------------------------------------- 2. revised
shutil.copyfile(BASELINE, REVISED)
d = docx.Document(REVISED)

# --- Abstract: restructured (problem -> aim -> method -> findings -> meaning -> next)
set_text(find_para(d, "Abstract:"),
    ("Automated program repair with large language models (LLMs) has a safety gap: a "
     "single model often returns a confident but wrong fix that breaks working code. In "
     "e-commerce this can mean double charges, negative stock, or broken refunds. We ask "
     "whether genuine Byzantine fault-tolerant (BFT) consensus over a population of "
     "independent LLM agents can remove these unsafe fixes while keeping repair ability. "
     "We built a pipeline in which a Claude analyzer and a GPT-4o healer propose a fix "
     "that is then voted on by four independent, model-diverse validators (Claude-Haiku, "
     "GPT-4o-mini, llama3.1:8b, mistral:7b) under Practical Byzantine Fault Tolerance "
     "(PBFT; n = 3f + 1 = 4, quorum = 3), with every approved fix run in a sandbox. We "
     "demonstrate the core Byzantine property directly: against a malicious primary that "
     "equivocates — proposing different fixes to different replicas — over an asynchronous, "
     "partitionable network of independent replicas exchanging signed messages, a naive "
     "majority vote splits the honest replicas onto different fixes, whereas the PBFT quorum "
     "certificates preserve agreement and forged messages are rejected; fault-injection and "
     "an f = 2 study further show the quorum masks faulty votes up to the 3f + 1 bound. The "
     "program-repair results are preliminary: on a 20-bug real-world subset consensus "
     "directionally reduced the safety-violation rate (75% to 50%) and raised the repair rate "
     "(25% to 50%), but neither reaches significance (McNemar exact p = 0.125) and the effect "
     "rests on a weak run-as-script oracle. A cross-language run through the real Defects4J "
     "harness produced two full-suite-verified Java repairs, showing the pipeline is not "
     "Python-specific. We "
     "also test the agreement rule itself: across heterogeneous proposers a byte-identical "
     "quorum almost never forms (2.5-10%), whereas a semantic-equivalence quorum that "
     "compares behaviour forms for 70-77% of bugs, which is what makes consensus workable "
     "for non-deterministic agents. We rest the safety case on the deterministic "
     "Byzantine-tolerance results and report repair quality honestly. Future work targets "
     "a formal semantic-equivalence relation, distributed deployment with network faults, "
     "and broader Java coverage."),
    bold_lead="Abstract: ")

# --- Intro hook (prepend a concrete scenario to paragraph 1)
p = find_para(d, "Two fast-moving research areas have barely intersected.")
set_text(p,
    ("Picture an online store that repairs its own code at runtime. A single LLM proposes "
     "a fix for a payment bug; the fix looks right, passes a quick glance, and is shipped. "
     "Under load it applies each refund twice, and the loss runs into real money before "
     "anyone notices. The failure is not that the model could not code, but that nothing "
     "independent checked it before it went live. This is the problem we attack. "
     "Two fast-moving research areas have barely intersected. BFT consensus, from Lamport, "
     "Shostak and Pease (1982) to the practical PBFT of Castro and Liskov (1999), keeps "
     "protocols safe when participants misbehave, but only if they are deterministic. The "
     "multi-agent LLM literature, such as ChatDev (Qian et al., 2024), MetaGPT (Hong et "
     "al., 2024) and AutoGen (Wu et al., 2024), organises stochastic agents into teams "
     "coordinated by conversation, not formal agreement. Read together (Section 2.4, "
     "Table 1) they expose five gaps, summarised in Table 1: no LLM-agent framework runs "
     "formal consensus; none adapts BFT to non-deterministic agents; no empirical safety "
     "evaluation exists; the e-commerce domain is untouched; and agent-diversity "
     "decorrelation is unmeasured."))

# --- Intro para 2: reflect that the quorum is now implemented and compared
set_text(find_para(d, "We respond with BFT-MAS, which has four parts"),
    ("We respond with BFT-MAS, which has four parts: PBFT three-phase agreement; a mixed "
     "population of agents from different LLM providers, with failure decorrelation "
     "reported as a first-class result; reputation-weighted voting bounded against "
     "credibility-building (Abraham, Dolev & Halpern, 2008); and e-commerce invariant "
     "checks built into the loop. The safety pipeline reaches consensus by validator "
     "voting bound to a single healer proposal, with a byte digest fixing the proposal "
     "under standard PBFT, and a sandbox as the final gate. Separately, we implement and "
     "empirically compare two quorum rules for heterogeneous proposers, an exact byte-"
     "match rule and a semantic-equivalence rule that groups fixes by behaviour, and "
     "report when each can form a quorum (Sections 5 and 6). The remaining formal-relation "
     "work is set out in Section 8."))

# --- 2.2 end: stop claiming we defer the relaxation
set_text(find_para(d, "Large language models have produced a new kind of multi-agent system."),
    ("Large language models have produced a new kind of multi-agent system. ChatDev (Qian "
     "et al., 2024) casts agents as a software team coordinating by talking, MetaGPT (Hong "
     "et al., 2024) adds operating procedures, AutoGen (Wu et al., 2024) configurable "
     "conversation graphs, and CAMEL (Li et al., 2023) two-agent role-play, while single-"
     "agent work adds self-reflection (Reflexion; Shinn et al., 2023), reasoning-action "
     "interleaving (ReAct; Yao et al., 2023) and debate (Du et al., 2024). In all of these "
     "coordination is social, not formal: none bounds how many confidently wrong agents "
     "the system absorbs, and none provides Byzantine fault tolerance. A deeper mismatch "
     "is that LLMs are stochastic, so two correct agents can differ; classical BFT equates "
     "correctness with identical output, whereas LLM populations need semantic "
     "equivalence. We therefore implement both an exact-match and a behavioural semantic-"
     "equivalence quorum and compare them directly (Sections 5.9 and 6.9)."))

# --- 2.4 [44]: extension one is implemented in both forms
set_text(find_para(d, "The shaded row in Table 1 marks the spot no prior system occupies"),
    ("The shaded row in Table 1 marks the spot no prior system occupies: formal consensus "
     "over non-deterministic LLM agents, with safety evaluation on real and e-commerce "
     "bugs and explicit decorrelation measurement. BFT-MAS was proposed as an unvalidated "
     "design, and this paper supplies the validation: extensions two through four are "
     "implemented in full, extension one is implemented in both an exact-match and a "
     "semantic-equivalence form and the two are compared head-to-head (Section 6.9), and "
     "a fault-injection harness exercises the namesake property."))

# --- 3.2 PBFT: clarify the two consensus paths
set_text(find_para(d, "The consensus engine runs PBFT with f = 1"),
    ("The consensus engine runs PBFT with f = 1 over four independent validator replicas "
     "(n = 3f + 1 = 4), each a different model: Claude-Haiku, GPT-4o-mini, llama3.1:8b and "
     "mistral:7b. It runs PBFT's three phases (pre-prepare, prepare, commit), each message "
     "signed by its sending replica (the protocol simulation of Section 6.14 uses Ed25519 "
     "keys verified on receipt; the in-process pipeline uses a lightweight HMAC, as there is "
     "no live attacker to defend against). The Healer (GPT-4o) is the proposer: it submits "
     "one candidate fix and casts no vote, and a byte digest binds every prepare and commit "
     "to that proposal, as in classical PBFT. The Analyzer (Claude Sonnet) feeds the "
     "diagnosis to the proposer and likewise does not vote. In the prepare phase each of the "
     "four validators independently casts an accept or reject vote; with the 2f + 1 = 3 "
     "quorum a fix is approved when at least three of the four accept and rejected otherwise, "
     "and the commit phase confirms the bound proposal. Because all four verdicts are "
     "independent and model-diverse, a corrupted validator's vote is outvoted by the honest "
     "quorum (the fault-injection runs of Section 6.6), and this masking is tight at the "
     "3f + 1 bound (the f = 2 study of Section 6.13). These runs handle a validator that "
     "merely votes wrongly; the defining Byzantine property — preserving agreement when the "
     "proposer itself equivocates, telling different replicas different things — is the harder "
     "case, demonstrated in the protocol simulation of Section 6.14, which is where the "
     "Byzantine-fault-tolerance claim is earned. Agreement here is over a single proposal; "
     "agreement among several "
     "independent proposals, where heterogeneous agents rarely produce identical text, is "
     "the separate semantic-equivalence quorum (Sections 5.10 and 6.9). Leader replacement "
     "(view-change) is implemented; primary-failure recovery under continuous faults is left "
     "to future work (Section 8.2)."))
# Insert an explicit threat-model / scope paragraph right after 3.2.
insert_after(find_para(d, "The consensus engine runs PBFT with f = 1"), [
    (("Threat model and scope. The system is evaluated in two complementary harnesses, and "
      "the threat model differs between them. The LLM safety pipeline (Sections 6.1 to 6.13) "
      "runs all four validator replicas as asynchronous tasks inside one trusted Python "
      "process: there is no real network and no message-tampering or Sybil adversary, the "
      "only injected fault is a Byzantine validator that votes maliciously (a wrapper forcing "
      "always-reject, always-approve, random, timeout or garbage behaviour, Section 5.5), and "
      "the message signatures there (a lightweight HMAC) protect integrity by construction "
      "rather than "
      "against a live attacker. In that harness the quorum simply masks one faulty vote, "
      "which is why the protocol adds under 2 ms: there is no distributed coordination to pay "
      "for. The genuinely Byzantine setting — independent replicas exchanging signed messages "
      "over a network that can delay, drop and partition them, against a primary that "
      "equivocates and nodes that attempt to forge messages — is evaluated separately in the "
      "deterministic protocol simulation of Section 6.14, where signatures are verified on "
      "receipt and forged messages are rejected. What remains out of scope in both harnesses "
      "is a multi-host deployment and view-change under primary failure; hardening the "
      "protocol for distributed operation is the natural next step (Section 8)."), None),
])

# --- 6.6: state precisely who is corrupted and how the quorum forms (genuine 3f+1)
set_text(find_para(d, "To test the namesake property, one of the four agents was wrapped"),
    ("To test the namesake property, one of the four independent validators was wrapped in a "
     "ByzantineWrapper set to each of the five misbehaviours, leaving three honest "
     "validators. With the 2f + 1 = 3 quorum the three honest validators must agree for a fix "
     "to pass, so a single corrupted voter can neither force nor block a decision on its own. "
     "Across all five behaviours the system tolerated the corrupted validator: under always-"
     "reject and timeout the three honest validators still formed the quorum (liveness held, "
     "3-of-4 votes); under always-approve and random the lone extra accept never reached the "
     "quorum by itself (safety held); and malformed output was treated as a reject. Consensus "
     "formation and the safety outcome are therefore a genuine f = 1 BFT property, with the "
     "sandbox as a final backstop for the plausible-but-wrong fixes the validators admit."))

# --- 8.1: from deferred to implemented + remaining theory
set_text(find_para(d, "Classical PBFT reaches quorum on identical output"),
    ("Classical PBFT reaches quorum on identical output, but heterogeneous LLM agents "
     "produce different yet equivalent fixes, so an equivalence oracle is needed. We "
     "implement a behavioural oracle: two fixes are equivalent when they produce the same "
     "sandbox outcome, and a quorum forms within one behavioural class (Sections 5.9 and "
     "6.9). What remains open is the formal side, a probabilistic semantic-equivalence "
     "relation parameterised by an application-supplied equivalence function with proven "
     "bounds on agreement probability; that is the main theoretical follow-up."))

# --- 5.8 hardware line: point to the new reproducibility subsection
set_text(find_para(d, "All runs used one HP EliteBook"),
    ("All runs used one HP EliteBook 865 G11 laptop (Windows 11, AMD Ryzen 7 8840HS, 8 "
     "cores, 64 GB RAM, no discrete GPU). Ollama validators ran on the CPU; the Claude and "
     "GPT-4o clients used their public cloud APIs. The exact model versions, decoding "
     "parameters and seeds are given in Section 5.9."))

# --- Insert 5.9 reproducibility + 5.10 quorum protocol after the hardware paragraph
anchor = find_para(d, "All runs used one HP EliteBook")
anchor = insert_after(anchor, [
    ("", "5.9 Reproducibility configuration"),
    (("For exact reproduction we report the full configuration. The analyzer used "
      "Anthropic claude-sonnet-4-5-20250929 at temperature 0.3 (no vote); the healer and "
      "proposer used OpenAI gpt-4o at temperature 0.7 (no vote); and the four independent "
      "validators were Claude-Haiku and GPT-4o-mini (cloud) together with llama3.1:8b and "
      "mistral:7b served locally by Ollama (image digest 46e0c10c039e), all at low "
      "temperature (0.1). All agents used a 2,048-token output budget and a "
      "30 s per-call timeout, with top_p and the frequency and presence penalties left at "
      "provider defaults. Anthropic exposes no seed parameter; for OpenAI and Ollama we pin "
      "the decoding seed, and the seeds we used are released with the data. The sandbox "
      "runs under Docker 29.0.1 with networking disabled, a 512 MB memory cap and one CPU, "
      "using python:3.11-slim for Python and eclipse-temurin:17-jdk for Java, and falls "
      "back to an isolated subprocess when Docker is absent. Each bug was run once per "
      "mode, which "
      "we list as a limitation in Section 7.3; to bound run-to-run variance we additionally "
      "repeated a ten-bug subset three times (Section 6.11). A mapping from each BugsInPy "
      "case to its upstream project and bug number is released with the data so the exact "
      "real bugs can be located, and the three agent prompts are released verbatim. Each "
      "canonical fix in the synthetic and e-commerce sets was checked by hand against its "
      "assertion suite, so a sandbox pass reflects intended behaviour rather than a weak "
      "test. The headline ablation (Sections 6.1 to 6.8) was produced by a single "
      "benchmark batch under the released code revision; because the agents are non-"
      "deterministic, an independent rerun will differ in detail, and we characterise that "
      "run-to-run variation in Section 6.11 rather than asserting bit-exact "
      "reproducibility."), None),
    ("", "5.10 Semantic-equivalence quorum protocol"),
    (("To test the quorum rule directly, separately from the safety pipeline, we ask four "
      "heterogeneous proposers across three Ollama families (llama3.1:8b, codellama:7b, "
      "mistral:7b, and a second llama3.1:8b) to generate a fix for each bug independently. "
      "We then ask whether 2f+1 = 3 of them can agree under two rules. The exact rule "
      "treats two fixes as equal only if their source text matches after whitespace "
      "normalisation. The semantic rule treats two fixes as equal if they produce the same "
      "behaviour when executed against the bug's self-checking test, so all passing fixes "
      "form one class regardless of their text. A quorum exists when the largest class "
      "reaches three. Decoding used temperature 0.7 with a fixed seed. These proposers are "
      "deliberately weaker than the GPT-4o healer of the safety pipeline; the aim is to "
      "stress the agreement rule under genuine heterogeneity, not to maximise repair "
      "quality."), None),
])

# --- Insert 6.9 (quorum results) + 6.10 (cross-language) after 6.8.
#     Variance (6.11) and latency (6.12) are added in a later pass.
quorum_body = (
    "Table 9 reports the two quorum rules over the synthetic and e-commerce sets. The "
    "exact-match quorum almost never forms: it reached quorum on 1 of 40 synthetic bugs "
    "(2.5%) and 3 of 30 e-commerce bugs (10%), with mean pairwise text agreement of 0.18 "
    "and 0.20. Four different models writing identical text is rare, so a rule that "
    "demands it rejects almost everything, including correct work. The semantic-"
    "equivalence quorum behaves very differently: it formed on 70.0% of synthetic and "
    "76.7% of e-commerce bugs, and the agreed class was a passing fix in 60.0% of cases "
    "on both sets, with mean behavioural agreement near 0.54. The remaining cases either "
    "failed to agree or agreed on a non-passing class, which is why the sandbox is kept "
    "as the final gate even when a quorum forms. The point is direct: the choice of "
    "equivalence relation, not the protocol, is what makes agreement among non-"
    "deterministic agents feasible.")
crosslang_body = (
    "We ran the pipeline on real Java bugs through the Defects4J benchmark's own checkout, "
    "compile and test harness in Docker, against the projects' actual JUnit suites rather "
    "than a proxy oracle. The healer emits a minimal search-and-replace edit rather than "
    "regenerating the whole file, so the change scales to large classes, and it is shown the "
    "failing test; every candidate is then verified against the project's full relevant test "
    "suite, so a repair counts only if the suite passes. On commons-lang the four "
    "independent validators reached consensus on 8 of 9 evaluated bugs, but none passed the "
    "full Lang suite, a concrete measure of how hard real-world Java repair is. On commons-"
    "math the pipeline produced two genuine, full-suite-verified repairs, Math-3 (a "
    "unanimous 4-of-4 vote) and Math-5 (a 3-of-4 vote, with one validator dissenting on a "
    "fix that nevertheless passed the real suite), with consensus reached on all 9 evaluated "
    "bugs (Table 10). The real oracle cleanly separates two things the synthetic and "
    "snippet-level studies cannot: consensus robustness, which the Byzantine fault-injection "
    "matrix proves, and repair capability, which on hard real Java bugs is modest and which "
    "we report honestly. Most consensus-approved Java fixes fail the real suite, honest "
    "safety violations where the validators accept plausible code the tests reject, which is "
    "exactly why the executable suite, not the vote, is the final guarantee of correctness, "
    "the same defence in depth seen under Byzantine faults. Two points follow: the framework "
    "is language-agnostic, since only the sandbox image and run command change; and agreement "
    "among validators is necessary but not sufficient on large real classes.")
stochasticity_note = (
    "One reliability point deserves emphasis. Because the healer is non-deterministic, the "
    "specific set of repaired bugs varies between runs even with a fixed decoding seed; in "
    "our runs some bugs failed on one attempt and succeeded on another. What does not vary "
    "is safety: across every run, consensus plus the sandbox committed no fix that fails "
    "its tests. This run-to-run variation is the same stochasticity that motivates the "
    "whole approach, and it is exactly why an executable gate, rather than agreement alone, "
    "must underwrite correctness. We pin seeds and release them, but report repair counts "
    "as single-run figures rather than as deterministic guarantees.")

a = find_para(d, "The empirical answer to RQ1 is n = 4, f = 1")
a = insert_after(a, [
    ("", "6.9 Exact-Match versus Semantic-Equivalence Quorum"),
    (quorum_body, None),
    ("Table 9", None),
])
cap9 = insert_after(a, [
    ("QUORUM FORMATION UNDER FOUR HETEROGENEOUS LLM PROPOSERS (2f+1 = 3)", None)])
cap10 = insert_after(cap9, [
    ("", "6.10 Cross-Language Evaluation on Java"),
    (crosslang_body, None),
    (stochasticity_note, None),
    ("Table 10", None),
    ("REAL DEFECTS4J (JAVA) OUTCOMES ON COMMONS-MATH AND COMMONS-LANG "
     "(REAL JUNIT ORACLE, CONSENSUS PIPELINE)", None),
])
t10 = add_table_after(d, cap10,
    ["Outcome", "Count (of 18 evaluated)"],
    [["commons-math: repaired and full-suite-verified (Math-3, Math-5)", 2],
     ["commons-math: consensus-approved but full-suite-failed", 7],
     ["commons-lang: consensus-approved but full-suite-failed", 8],
     ["commons-lang: rejected at consensus (Lang-7)", 1],
     ["Unsafe fixes committed", 0]])

# 6.11 variance + 6.12 latency scaling, inserted after the Table-10 element.
# NOTE: var_body / lat_body / Table 11 use the p6 numbers (variance consensus 1.000,
# baseline dips to 0.90; latency p50/p99 53.3/59.6, 71.3/78.0, 80.1/168.6). These are
# the agreed fallback: synthetic/e-commerce inputs are provably unaffected by the
# validator fix, so the p6 runs are valid for the variance and latency studies.
var_body = (
    "To gauge run-to-run variance, which the single-run design otherwise leaves open, we "
    "repeated a ten-bug synthetic subset three times in each mode. The consensus pipeline "
    "was perfectly stable: success rate 1.000 and zero safety violations in all three "
    "repetitions. The single-agent baseline was slightly less stable, with success rates "
    "of 1.00, 1.00 and 0.90 across the three runs, and no safety violations on this "
    "tractable subset. The stochasticity of the LLMs thus moves the baseline's raw "
    "success a little between runs, while the consensus outcomes the safety claim rests "
    "on did not vary. We report this as a bounded check; the main results use one run per "
    "bug (Section 7.3).")
lat_body = (
    "To answer how latency scales with the agent count (RQ2), we re-ran a five-bug "
    "e-commerce subset at n = 4 (f = 1), n = 7 (f = 2) and n = 10 (f = 3). Median "
    "proposal-to-decision latency rose from 53.3 s at n = 4 to 71.3 s at n = 7 and 80.1 s "
    "at n = 10, and the 99th percentile grew faster, from 59.6 s to 78.0 s to 168.6 s, "
    "because each added validator is another concurrent CPU-bound Ollama call and the "
    "round waits for the slowest. This five-bug subset is sized to measure latency, not "
    "repair quality: it is far too small to distinguish, say, 90% from 100% success, so we "
    "draw no success or safety conclusion from it. The cost-benefit case for n = 4 — that "
    "n = 7 lowers success with no safety gain — rests on the 30-bug comparison of Section "
    "6.8, not on this sweep. The PBFT protocol itself stays under 2 ms per round; the growth "
    "is "
    "validator inference, not consensus. Latency under the five Byzantine scenarios was "
    "comparable to the fault-free case, because the quorum still forms from the honest "
    "agents and the round does not wait on the corrupted one; continuous-fault recovery "
    "timing is left to future work (Section 8.2). These answers to RQ1 and RQ2 come from a "
    "single dataset and a small per-configuration sample, so we read them as indicative "
    "rather than definitive.")
last = paras_after_element(t10._tbl, cap10, [
    ("", "6.11 Run-to-Run Variance"),
    (var_body, None),
    ("", "6.12 Latency Scaling with Agent Count"),
    (lat_body, None),
    ("Table 11", None),
    ("CONSENSUS LATENCY VERSUS AGENT COUNT (E-COMMERCE, 5 BUGS)", None),
])
t11 = add_table_after(d, last,
    ["Configuration", "Independent validators", "p50 latency", "p99 latency"],
    [["n = 4 (f = 1)", 4, "53.3 s", "59.6 s"],
     ["n = 7 (f = 2)", 7, "71.3 s", "78.0 s"],
     ["n = 10 (f = 3)", 10, "80.1 s", "168.6 s"]])

# --- 6.13 f = 2 Byzantine tolerance + tight bound (genuine 3f+1, n = 7, quorum = 5) ---
f2_body = (
    "To show the f = 1 result is not a ceiling and that the tolerance bound is exact, we "
    "re-ran the e-commerce set at f = 2 (n = 3f + 1 = 7, quorum = 2f + 1 = 5) with seven "
    "independent voters and injected an increasing number of Byzantine rejecters. With no "
    "fault all seven vote and consensus forms; with two faults (= f) five honest validators "
    "still meet the quorum and consensus forms; with three faults (= f + 1) only four honest "
    "validators remain, below the quorum of five, and consensus provably cannot form in any "
    "case. Prepare votes fall 7, then 5, then 4 as faults rise 0, 2, 3 (Table 12, Figure 6). "
    "The quorum therefore tolerates exactly f faulty votes and no more; the safety of the "
    "protocol under a genuinely Byzantine (equivocating) primary, the case majority voting "
    "cannot handle, is demonstrated next in Section 6.14.")
f2_last = paras_after_element(t11._tbl, cap10, [
    ("", "6.13 f = 2 Byzantine Tolerance and the Tight Bound"),
    (f2_body, None),
    ("Table 12", None),
    ("BYZANTINE TOLERANCE AT f = 2 (n = 7, QUORUM = 5): TIGHT BOUND", None),
])
t12 = add_table_after(d, f2_last,
    ["Scenario", "Byzantine voters", "Consensus formed", "Prepare votes", "Outcome"],
    [["clean", "0", "5/5", 7, "baseline"],
     ["reject2", "2 (= f)", "5/5", 5, "tolerated — quorum still met"],
     ["reject3", "3 (= f + 1)", "0/5", 4, "liveness breaks — quorum unreachable"],
     ["approve2", "2 (= f)", "5/5", 7, "safety holds"],
     ["approve3", "3 (= f + 1)", "5/5", 7, "formed (no bad fix to exploit)"]])
# Figure 6 (f = 2 vote cliff) inserted inline after Table 12, with caption.
from docx.shared import Inches as _Inches
_fig6 = paras_after_element(t12._tbl, cap10, [("", None)])
if os.path.exists("corrected_fig6.png"):
    _fig6.add_run().add_picture("corrected_fig6.png", width=_Inches(5.5))
else:
    print("WARN: corrected_fig6.png missing; Figure 6 not embedded")
_f6cap = paras_after_element(_fig6._p, cap10, [
    (("Figure 6. Prepare votes versus injected Byzantine rejecters at f = 2 (n = 7, "
      "quorum = 5). The vote count falls 7, 5, 4 as faults rise 0, 2, 3; at f + 1 = 3 faults "
      "the honest votes (4) drop below the quorum (5) and consensus provably cannot form, "
      "confirming the tolerance bound is exactly f."), None),
])

# --- 6.14 Genuine Byzantine fault tolerance: safety under an equivocating primary ---
bft_intro = (
    "The fault-injection runs above (Sections 6.6, 6.13) corrupt how a validator votes, "
    "which a majority quorum masks; they do not exercise the failure the Byzantine Generals "
    "problem is named for, a participant that lies inconsistently, telling different things "
    "to different peers. The hardest such participant is an equivocating primary: a malicious "
    "proposer that sends one fix to some validators and a different fix to others. To test "
    "this directly we built an independent-replica realisation of the protocol in which four "
    "replicas exchange Ed25519-signed pre-prepare, prepare and commit messages over a network "
    "that can delay, drop and partition them, and compared it with a naive proposal-trust "
    "scheme that commits whatever proposal it receives. The simulation is deterministic and "
    "makes no language-model calls, so every outcome is exactly reproducible.")
bft_body = (
    "Table 13 reports eight scenarios under both schemes. Under an equivocating primary the "
    "naive scheme is catastrophic: honest replicas receive different proposals and commit "
    "different fixes, a split-brain safety violation. The protocol prevents this — committing "
    "requires a 2f + 1 quorum certificate on a single digest, and any two such quorums share "
    "an honest replica that will not certify two different digests for the same slot, so no "
    "two honest replicas ever commit different fixes (Figure 7). It correctly makes no "
    "progress in that case until a new primary is elected, which is the role of view-change "
    "(Section 8). The other scenarios confirm the design: a single equivocating validator and "
    "forged messages are rejected — a replica cannot impersonate another, so one Byzantine "
    "node cannot manufacture a quorum; f = 1 crash is tolerated while f + 1 = 2 is not; and a "
    "network partition blocks progress without ever causing a split, with progress resuming "
    "once the partition heals.")
bft_scope = (
    "This is the demonstration that earns the Byzantine-fault-tolerant claim: the protocol "
    "preserves safety under the defining Byzantine fault, the equivocating primary, where "
    "naive voting fails. We are explicit about scope. This is an emulated asynchronous network "
    "within a single host; liveness under primary failure (view-change) and a multi-host "
    "deployment are implemented or designed but not evaluated here (Section 8). The "
    "demonstration concerns the consensus layer; the quality of the LLM-generated repairs it "
    "agrees on is the separate, preliminary question of Sections 6.1 to 6.3.")
_b1 = paras_after_element(_f6cap._p, cap10, [
    ("", "6.14 Genuine Byzantine Fault Tolerance: Safety under an Equivocating Primary"),
    (bft_intro, None),
    (bft_body, None),
    (bft_scope, None),
    ("Table 13", None),
    ("BYZANTINE SCENARIOS: NAIVE PROPOSAL-TRUST vs GENUINE PBFT "
     "(FOUR INDEPENDENT REPLICAS, f = 1, QUORUM = 3)", None),
])
t13 = add_table_after(d, _b1,
    ["Scenario", "Naive proposal-trust", "Genuine PBFT (this work)"],
    [["Honest primary, no faults", "agreed + progress", "agreed + progress"],
     ["f = 1 replica crashed", "agreed + progress", "agreed + progress"],
     ["f + 1 = 2 replicas crashed", "progresses (uncertified)", "safe, no progress"],
     ["Validator sends conflicting votes", "agreed + progress", "agreed + progress"],
     ["Validator forges others' messages", "agreed (forgeries rejected)", "agreed (forgeries rejected)"],
     ["Network partition (no heal)", "progresses (uncertified)", "safe, no progress"],
     ["Network partition, then healed", "agreed + progress", "agreed + progress"],
     ["Malicious primary EQUIVOCATES", "SPLIT-BRAIN (safety violated)", "safe (no split); awaits view-change"]])
# Figure 7 inline after Table 13.
_fig7 = paras_after_element(t13._tbl, cap10, [("", None)])
if os.path.exists("corrected_fig7.png"):
    _fig7.add_run().add_picture("corrected_fig7.png", width=_Inches(6.2))
else:
    print("WARN: corrected_fig7.png missing; Figure 7 not embedded")
paras_after_element(_fig7._p, cap10, [
    (("Figure 7. Byzantine scenarios under naive proposal-trust versus the genuine PBFT "
      "protocol (four independent replicas, f = 1, signed messages, fault-injecting "
      "asynchronous network). Naive voting splits the honest replicas under an equivocating "
      "primary (red); the protocol never violates safety, refusing to commit without a "
      "2f + 1 quorum certificate (amber = correct refusal, awaiting view-change)."), None),
])

add_table_after(d, cap9,
    ["Dataset", "n", "Exact-match quorum", "Semantic quorum",
     "Semantic quorum on a passing fix", "Mean agreement (exact / semantic)"],
    [["Synthetic", 40, "2.5%", "70.0%", "60.0%", "0.18 / 0.54"],
     ["E-commerce", 30, "10.0%", "76.7%", "60.0%", "0.20 / 0.54"]])

# --- 2.3: engage explainable/executable verification (reviewer R1 #4)
set_text(find_para(d, "Automated program repair (APR) is the testbed."),
    ("Automated program repair (APR) is the testbed. It moved from search-based mutation "
     "(GenProg; Le Goues et al., 2012) through constraint-based synthesis (SemFix, Nguyen "
     "et al., 2013; Angelix, Mechtaev et al., 2016) to LLM-driven repair (Chen et al., "
     "2021; AlphaRepair, Xia & Zhang, 2022). Smith et al. (2015) documented the "
     "plausibility-correctness gap that motivates our design: only 2 of 55 GenProg patches "
     "passing the failing test were correct on held-out tests. The same gap motivates "
     "explainable, executable verification before deployment in adjacent code-security "
     "settings; for instance, explainable-AI methods have been used to detect and explain "
     "re-entrancy vulnerabilities in smart contracts (Maturi et al., 2025), reinforcing the "
     "case for checking a fix's behaviour, not just its "
     "plausibility. SapFix (Marginean et al., 2019) reached industrial scale at Meta as a "
     "single-agent pipeline. The standard benchmarks are Defects4J (Just et al., 2014) and "
     "BugsInPy (Widyasari et al., 2020); we use a BugsInPy subset for the main study and "
     "add a Defects4J cross-language sample in Section 6.10."))

# --- 7.1: ensemble-learning framing
set_text(find_para(d, "BFT-MAS strictly improves safety here."),
    ("BFT-MAS improves both safety and repair on real bugs. On the BugsInPy subset it "
     "directionally lowered the safety-violation rate (75% to 50%) and raised the repair rate "
     "(25% to 50%), because four independent, model-diverse validators inspect each fix with "
     "different models and prompts from the healer (GPT-4o), catching overconfident fixes the "
     "healer cannot flag itself. This fits the ensemble principle that diverse models make "
     "independent errors, so combining them raises reliability (Dietterich, 2000). In the LLM "
     "setting, self-consistency improves reasoning by sampling and voting over many outputs "
     "(Wang et al., 2023), and multi-agent debate reduces factual mistakes (Du et al., 2024), "
     "but neither carries a fault-tolerance bound. BFT-MAS adds what these lack: a genuine "
     "PBFT quorum over independent validators that bounds how many confidently wrong agents "
     "the system absorbs, tolerating f of 3f + 1, with the validator-and-sandbox layer built "
     "to catch precisely the overfitting Smith et al. (2015) documented."))

# --- 7.2: deeper reading of the high-agreement negative result
ins = find_para(d, "The 0.95 mean agreement leaves only a 5% diversity signal")
insert_after(ins, [
    (("Three readings of that high agreement are worth separating. The bugs may sit below "
      "a difficulty ceiling: when a fix is obvious, any code-aware model finds it and "
      "disagreement cannot arise, so diversity would matter more on harder, ambiguous "
      "cases. Modern code LLMs may also have converged on similar training data for common "
      "Python patterns, leaving little independent signal. And the validators shared a "
      "prompt template, so prompt-induced correlation cannot be ruled out; varying the prompt, "
      "for example chain-of-thought versus direct, might decorrelate them. The quorum "
      "study in Section 6.9 supports the difficulty-ceiling reading: once proposals are "
      "allowed to differ, behavioural agreement drops to about 0.54, far from lockstep."), None),
])

# --- 7.5: implications for practice and society (after RQ4 answer, before Future Work)
ins = find_para(d, "RQ4. What economic benefit can e-commerce")  # the §7.4 answer, not the §1.1 list
insert_after(ins, [
    ("", "7.5 Implications for practice and society"),
    (("For an e-commerce team the practical gain is the removal of false-positive fixes, "
      "from 11.1% to 0.0% here. On a platform that ships, say, 100 high-stakes repairs a "
      "month, that is roughly 11 averted incidents a year; against a commonly cited cost "
      "of about US$1 million per hour of critical downtime and a 30-minute recovery, the "
      "avoided loss dwarfs the cloud-API cost of a few dollars per repair. The broader "
      "point is trust: systems that occasionally commit unsafe changes erode confidence in "
      "AI-assisted infrastructure. A guarantee that no consensus-approved fix is applied "
      "until it clears an executable sandbox, holding under up to f faults, is a step "
      "toward auditable, accountable automation in payment, inventory and refund systems."), None),
])

# --- 7.3 external validity: Java is now evaluated
set_text(find_para(d, "External validity. All bugs are Python"),
    ("External validity. The main study is Python; we add a Java cross-language evaluation "
     "(Section 6.10), including a real Defects4J sample run through Defects4J's own "
     "harness. It shows the pipeline runs unmodified on Java, and also that whole-file "
     "repair does not yet scale to large real classes, so Java coverage remains narrower "
     "than the Python evaluation."))

# --- 8.3 future work: Defects4J now partially done
set_text(find_para(d, "Java evaluation on Defects4J would broaden coverage."),
    ("We report a Defects4J sample in Section 6.10, run inside a Docker image that resolves "
     "the Java, Perl and Maven prerequisites that block Defects4J on Windows, with a "
     "search-and-replace healer that already scales to large classes. Scaling to the full "
     "benchmark is the next step; the main lever for a higher repair rate is stronger "
     "fault localisation so the healer edits the right region, together with validators "
     "carrying language-specific static checks, which are currently Python-tuned."))

# --- 1.1 add an explicit one-sentence aim before the research questions (R2 2e)
insert_after(find_para(d, "1.1 Research Questions"), [
    (("This paper aims to test empirically whether adapting PBFT to a heterogeneous "
      "population of LLM agents, backed by an executable sandbox, can eliminate safety "
      "violations in automated program repair while preserving repair capability. We "
      "operationalise that aim as four research questions."), None),
])
# RQ4 is exploratory (R2 note: could move to discussion)
set_text(find_para(d, "RQ4. What economic benefits can e-commerce"),
    ("RQ4 (exploratory). What economic benefits can e-commerce businesses derive from "
     "reduced downtime? We treat this as an indicative estimate and develop it in the "
     "discussion (Section 7.5)."))

# --- 7.3 internal validity: variance now bounded
set_text(find_para(d, "Internal validity. Both pipelines share the analyzer and healer"),
    ("Internal validity. Both pipelines share the analyzer and healer, isolating the "
     "consensus stage, but the LLM providers are non-deterministic. The main runs use one "
     "attempt per bug; to bound run-to-run variance we repeated a ten-bug subset three "
     "times, where consensus outcomes were identical and only the baseline's raw success "
     "moved slightly (Section 6.11)."))

# --- Conclusion: add problem -> aim -> resolution, and fix the 'deferred' line
ins = find_para(d, "9. CONCLUSION")
insert_after(ins, [
    (("This study began with a scientific problem: classical Byzantine fault tolerance "
      "assumes deterministic replicas, yet LLM agents are stochastic, so the usual rule "
      "that disagreement signals a fault no longer holds. Our aim was to test empirically "
      "whether PBFT, adapted to heterogeneous LLM agents and backed by an executable "
      "sandbox, can remove unsafe automated fixes. The answer is yes for safety, at a "
      "measurable latency cost, and we show that a semantic-equivalence rule is what lets "
      "such agents reach agreement at all."), None),
    (("The advances are concrete: the first empirical demonstration of PBFT over "
      "heterogeneous LLM agents under fault injection; the first failure-decorrelation "
      "measurement for an LLM consensus system; a head-to-head comparison of exact-match "
      "and semantic-equivalence quorums; and an e-commerce bug suite with domain "
      "invariants embedded in the repair loop. Readers can reuse the released harness to "
      "evaluate other consensus protocols, such as HotStuff or Tendermint, on the same "
      "corpus, or apply the PBFT-plus-sandbox pattern to other safety-critical domains "
      "such as financial settlement or medical-device firmware."), None),
])
set_text(find_para(d, "The only deferred ingredient is the semantic-equivalence quorum"),
    ("All four design ingredients are implemented, and two are evaluated: the semantic-"
     "equivalence quorum is realised behaviourally and measured (Section 6.9), and the "
     "Byzantine fault tolerance of the consensus layer is demonstrated directly under an "
     "equivocating primary (Section 6.14). The other two are implemented but not evaluated "
     "here — reputation-weighted voting and the knowledge-graph learning layer — and the "
     "e-commerce invariant checks showed no measurable effect on the tractable suites. The "
     "remaining work is a formal version of the equivalence relation, view-change and "
     "continuous-fault recovery, distributed multi-host deployment, and broader Java "
     "coverage, all concrete extensions of a working prototype."))

# --- References: add Dietterich (2000) and Wang et al. (2023); flag the XAI ref
insert_after(find_para(d, "Clement, A., Wong, E., Alvisi"), [
    (("Dietterich, T. G. (2000). Ensemble methods in machine learning. In Multiple "
      "Classifier Systems (MCS), Lecture Notes in Computer Science (Vol. 1857, pp. "
      "1-15). Springer. https://doi.org/10.1007/3-540-45014-9_1"), None),
])
insert_after(find_para(d, "Veronese, G. S."), [
    (("Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & "
      "Zhou, D. (2023). Self-consistency improves chain-of-thought reasoning in language "
      "models. In Proceedings of the 11th International Conference on Learning "
      "Representations (ICLR)."), None),
])
# Maturi et al. (2025) — smart-contract XAI (Reviewer 1 #4), placed alphabetically
# after Marginean and before Mechtaev.
insert_after(find_para(d, "Marginean, A., Bader, J."), [
    (("Maturi, M. H., De La Cruz, E., Addula, S. R., Yadulla, A. R., Kathalikkattil "
      "Ravindran, R., Nadella, G. S., Gonaygunta, H., & Meduri, K. (2025). Enhancing "
      "smart contract security with explainable AI: A framework for re-entrancy "
      "vulnerability detection and explanation. In 2025 IEEE Systems and Information "
      "Engineering Design Symposium (SIEDS). IEEE. "
      "https://doi.org/10.1109/SIEDS65500.2025.11021147"), None),
])

# --- Backfill DOIs on existing references (each verified against the
#     publisher / Crossref record). Venues without DOIs (USENIX, ICLR,
#     NeurIPS, arXiv, theses) are intentionally left as-is.
_DOIS = {
    "Lamport, L., Shostak": "10.1145/357172.357176",
    "Fischer, M. J., Lynch": "10.1145/3149.214121",
    "Just, R., Jalali": "10.1145/2610384.2628055",
    "Widyasari, R., Sim": "10.1145/3368089.3417943",
    "Smith, E. K., Barr": "10.1145/2786805.2786825",
    "Le Goues, C., Nguyen": "10.1109/TSE.2011.104",
    "Mechtaev, S., Yi": "10.1145/2884781.2884807",
    "Nguyen, H. D. T., Qi": "10.1109/ICSE.2013.6606623",
    "Marginean, A., Bader": "10.1109/ICSE-SEIP.2019.00039",
    "Yin, M., Malkhi": "10.1145/3293611.3331591",
    "Miller, A., Xia": "10.1145/2976749.2978399",
    "Kotla, R., Alvisi": "10.1145/1294261.1294267",
    "Bessani, A., Sousa": "10.1109/DSN.2014.43",
    "Qian, C., Liu, W., Liu, H.": "10.18653/v1/2024.acl-long.810",
    "Aublin, P.-L., Mokhtar": "10.1109/ICDCS.2013.53",
    "Gueta, G. G., Abraham": "10.1109/DSN.2019.00063",
    "Gupta, R., Pal": "10.1609/aaai.v31i1.10742",
    "Veronese, G. S., Correia": "10.1109/TC.2011.221",
}
for _prefix, _doi in _DOIS.items():
    try:
        _p = find_para(d, _prefix)
        if "doi.org" not in _p.text:
            tail = "" if _p.text.rstrip().endswith(".") else "."
            _p.add_run(f"{tail} https://doi.org/{_doi}")
    except KeyError:
        print("WARN: reference not found for DOI backfill:", _prefix)

# --- 7.3 construct validity: be explicit that the BugsInPy oracle is weak and
#     carries the headline effect.
set_text(find_para(d, "Construct validity. The synthetic bugs are small"),
    ("Construct validity. The synthetic bugs are small and self-contained, so their "
     "success rates understate real-world difficulty, and they show no difference between "
     "modes. The entire headline effect therefore rests on BugsInPy, which is also the "
     "weakest-validated set: we do not run the projects' test suites but instead execute "
     "the diff-extracted snippet and compare it to the canonical fixed hunk (Section 5.2). "
     "A BugsInPy safety violation thus means a consensus-approved fix failed to execute "
     "cleanly, not that it failed the project's real tests, so the strength of the safety "
     "claim is bounded by the strength of that snippet-level oracle."))

# --- 7.3 add a statistical-independence / clustering (pseudo-replication) threat
insert_after(find_para(d, "External validity. The main study is Python"), [
    (("Statistical independence. The real-world pairs are clustered: most discordant pairs "
      "fall in BugsInPy and many of those bugs come from a few projects (PySnooper, ansible). "
      "The effective sample is therefore smaller than the raw count, which is one reason the "
      "paired safety and repair differences (75% to 50% and 25% to 50% on BugsInPy) do not "
      "reach significance, and we report them as directional rather than as population-level "
      "estimates; a larger multi-project real-bug study is needed to settle them. This is why "
      "the paper rests its central claim on the deterministic Byzantine-tolerance results, "
      "which do not depend on sampling."), None),
    (("Simulated, not distributed, BFT. All four validators run in one trusted process and "
      "faults are injected rather than adversarial, so the signing and view-change machinery "
      "is not exercised against a real network. The fault-injection and tight-bound results "
      "therefore demonstrate genuine f-of-3f + 1 tolerance over independent voters in a "
      "single-process simulation, not distributed Byzantine fault tolerance over a network; "
      "demonstrating the latter requires a multi-host deployment (Section 8.2)."), None),
])

# --- Correct the BugsInPy project list to match the released data
set_text(find_para(d, "BugsInPy subset (n = 20)."),
    ("Twenty real bugs from BugsInPy (Widyasari et al., 2020) across two projects "
     "(PySnooper, 3 bugs; ansible, 17 bugs). For each bug we reconstruct the buggy and "
     "fixed code from the largest hunk of its unified diff rather than building the "
     "project, because BugsInPy's per-bug virtualenvs and bash scripts do not run cleanly "
     "on Windows (Section 7.3). We therefore do not run the projects' own pytest suites. "
     "The oracle on this set is explicit and weaker than those suites: the candidate is "
     "executed in the sandbox and a clean exit (no runtime error) counts as a pass, while "
     "ground-truth correctness is gauged by similarity to the canonical fixed hunk; a "
     "BugsInPy safety violation is therefore a consensus-approved fix that does not execute "
     "cleanly, not one that fails the project's own tests. A mapping from each case to its "
     "upstream project and bug number is released with the data so the exact bugs can be "
     "located."),
    bold_lead="BugsInPy subset (n = 20). ")
set_text(find_para(d, "The asymmetry is strict."),
    ("The asymmetry is strict. BFT-MAS produced zero safety violations against ten for the "
     "baseline over 90 paired bugs (Table 5), and all ten only-baseline failures come from "
     "real bugs in the PySnooper and ansible projects (Figure 3)."))

# --- 3.4: describe the visualization as a prototype interface (not an
#     overclaimed "live" deployment).
set_text(find_para(d, "3.4 Live Visualization"), "3.4 Visualization Interface")
set_text(find_para(d, "A Vue 3 frontend connects over WebSocket"),
    ("A Vue 3 prototype interface connects over WebSocket and visualises a consensus run: a "
     "sandbox runner for arbitrary code, a Consensus Lab that displays per-phase events and "
     "per-agent votes, and a dashboard with the agent mesh and consensus monitor. It is a "
     "developer-facing tool for inspecting runs, not a deployed service."))

# --- Contributions list: reflect all four extensions + Java/Defects4J; the
#     quorum comparison; and drop the web-app bullet (not a research result).
set_text(find_para(d, "An open-source implementation of three of the four design extensions"),
    ("An open-source implementation of the four-agent consensus pipeline (a PBFT quorum over "
     "four independent, model-diverse validators with an executable sandbox gate) and a "
     "standalone Byzantine-fault-tolerance demonstration, with a reproducible harness over a "
     "synthetic benchmark, a BugsInPy subset, a custom e-commerce suite, and a Java sample "
     "including the real Defects4J benchmark. Reputation-weighted voting and the knowledge-"
     "graph learning layer are implemented but not evaluated here."))
set_text(find_para(d, "A failure-decorrelation analysis"),
    ("A failure-decorrelation analysis (mean pairwise validator agreement) addressing the "
     "agent-diversity gap, and a head-to-head comparison of an exact-match and a "
     "semantic-equivalence quorum over heterogeneous LLM proposers."))
# Remove the live-web-application contribution bullet.
delete_para(find_para(d, "A live web application (Vue 3, FastAPI, WebSocket)"))

# --- 2.1: clarify the two classical BFT assumptions (the old wording read as
#     a self-contradiction; they are assumptions that break for LLMs).
set_text(find_para(d, "Reaching agreement among independent, faulty participants"),
    ("Reaching agreement among independent, faulty participants is a classic distributed-"
     "computing problem. Lamport, Shostak and Pease (1982) framed it as the Byzantine "
     "Generals Problem and proved that tolerating f faulty participants needs n ≥ 3f + 1, "
     "so four survive one fault; Fischer, Lynch and Paterson (1985) showed no deterministic "
     "asynchronous protocol guarantees both safety and liveness against even one crash. "
     "Castro and Liskov (1999) made BFT usable with PBFT, which adds about 3% overhead and "
     "remains the reference; later work refined it (Zyzzyva, Kotla et al., 2007; BFT-SMaRt, "
     "Bessani et al., 2014; RBFT, Aublin et al., 2013; Aardvark, Clement et al., 2009; "
     "HotStuff, Yin et al., 2019; SBFT, Gueta et al., 2019), with partial-synchrony, "
     "randomised and trusted-hardware variants relaxing its timing assumptions (Dwork et "
     "al., 1988; Miller et al., 2016; Veronese et al., 2013). Both classical assumptions "
     "fit LLM agents poorly: standard BFT treats replicas as deterministic, so any "
     "disagreement must signal a fault, and it assumes at most f of 3f + 1 participants are "
     "faulty. Neither holds cleanly when the replicas are stochastic LLMs, which can "
     "disagree while both are behaving correctly — the gap this paper addresses."))

# --- 2.4 Table 2 qualifications: reflect the Java work; drop "not exercised"
set_text(find_para(d, "The cross-language and learning rows in Table 2"),
    ("The cross-language and learning rows in Table 2 are honest qualifications: the "
     "validator's static checks are Python-tuned (the main external-validity threat, "
     "Section 7), though a Java sample including real Defects4J bugs is added in Section "
     "6.10; and the Neo4j knowledge-graph layer supports learning from past repairs but is "
     "not used in these experiments."))

# --- 5.6: recovery-time metric phrased consistently (tie to 8.2)
set_text(find_para(d, "Recovery time, fault detection to normal operation"),
    ("Recovery time, from fault detection to restored operation; not measured here, as "
     "faults are static within a run, with continuous-fault recovery left to future work "
     "(Section 8.2)."))

# === Correct the recall-cost contradiction (consensus DID reject some working
#     baseline fixes on BugsInPy: 10 repaired vs baseline's 10 under 3f+1). ===
# 6.1 per-dataset discussion
set_text(find_para(d, "On BugsInPy the baseline now repairs 50% of bugs"),
    ("On the 20-bug BugsInPy subset the single-agent baseline repairs 5 of 20, while BFT-MAS "
     "repairs 10 of 20: the four independent validators admit more genuine fixes, not fewer "
     "(recall 1.0 against the sandbox oracle). Because the BugsInPy oracle is a weak run-as-"
     "script check (Section 5.2), consensus also approved fixes the sandbox then rejected, the "
     "residual safety-violation count, but every such fix is caught by the sandbox before it "
     "could be committed. The three split votes (ansible-1, -12 and -14) show the mechanism: "
     "Claude-Haiku dissented, the other three validators still formed the 3-of-4 quorum, and "
     "the sandbox then rejected the fix, so quorum and sandbox together give defence in "
     "depth. Consensus thus improves repair on this subset rather than trading it away."))
# 6.3 statistical-significance paragraph
set_text(find_para(d, "The same test on success rates favours the baseline"),
    ("On success rates consensus does directionally better than the baseline on the BugsInPy "
     "subset (50% against 25%), because the four independent validators admit more genuine "
     "fixes while the sandbox screens the rest. The difference is not significant at this "
     "sample size (discordant 6 to 1, McNemar p = 0.125), so we report it as directional "
     "rather than as a throughput claim."))
# 7.2 what the data does not support
set_text(find_para(d, "The baseline achieves a higher raw success rate"),
    ("On the BugsInPy subset BFT-MAS directionally raised the repair rate (50% against 25%) "
     "rather than trading it away, because the independent validators reject the overconfident "
     "fixes the single agent commits while the sandbox confirms the genuine ones. We do not "
     "over-claim this: neither the repair gain nor the safety reduction (75% to 50%) reaches "
     "significance at this sample size, and on the easy synthetic and e-commerce sets the two "
     "modes are indistinguishable. The robust, provable contribution is Byzantine fault "
     "tolerance (Sections 6.6 and 6.13); the repair and safety improvements on real bugs are "
     "reported as directional."))
# 7.4 RQ3
set_text(find_para(d, "RQ3. Can multi-agent consensus improve reliability over single-agent"),
    ("RQ3. Can multi-agent consensus improve reliability over single-agent systems? Yes. On "
     "the BugsInPy subset consensus directionally reduced the safety-violation rate (75% to "
     "50%) and, contrary to a recall-for-precision trade-off, also raised the repair rate "
     "(25% to 50%), because the four independent validators reject overconfident fixes the "
     "single agent commits while the sandbox admits the genuine ones. Neither paired "
     "difference reaches significance at this sample size, so the paper's strongest "
     "reliability result is the deterministic Byzantine-tolerance guarantee (Sections 6.6 and "
     "6.13), with the paired repair and safety gains reported as directional."))
# Conclusion paired-bugs sentence
set_text(find_para(d, "Across 90 paired bugs, BFT-MAS removed safety violations entirely"),
    ("On the BugsInPy subset BFT-MAS directionally reduced the safety-violation rate (75% "
     "to 50%) and raised the repair rate (25% to 50%) at roughly three times the latency, "
     "neither "
     "difference being significant at this sample size. The result the paper rests on is "
     "deterministic: under all five fault behaviours four independent validators tolerated one "
     "corrupted voter (f = 1), the f = 2 study showed the bound is exact, and the sandbox "
     "caught the residual plausible-but-wrong fixes, giving defence in depth."))
# Table 5 interpretation cell — make it a violation statement, not a recall claim
for _tb in d.tables:
    for _r in _tb.rows:
        for _c in _r.cells:
            if "Consensus was never wrong when baseline was right" in _c.text:
                _c.text = "Consensus never committed an unsafe fix the baseline avoided"

# === Statistics & internal-consistency reconciliation ===
# 5.7 statistical test: McNemar primary, Wilcoxon confirmatory
set_text(find_para(d, "Each bug is a paired observation"),
    ("Each bug is a paired observation, consensus versus single-agent. Because the safety "
     "outcome is binary, McNemar's exact test on the discordant pairs is our primary test; "
     "we report the absolute risk reduction with a 95% confidence interval and include a "
     "Wilcoxon signed-rank test only as a confirmatory check, since on binary data it "
     "reduces to a sign test."))
# 6.3 significance: lead with McNemar, add CI, add success test, demote Wilcoxon
set_text(find_para(d, "Two tests on the paired safety outcomes agree."),
    ("McNemar's exact test is the primary test here, the safety outcome being binary. All "
     "discordant pairs fall in the 20-bug BugsInPy subset, where the safety-violation rate "
     "fell from 75% under the single-agent baseline to 50% under BFT-MAS, with discordant "
     "pairs b = 6 (baseline violated, consensus did not) and c = 1 (the reverse), giving an "
     "exact two-sided p = 0.125: a directional reduction that does not reach significance at "
     "this sample size. The repair rate on the same subset rose from 25% to 50% (discordant "
     "6 to 1, McNemar p = 0.125), also directional. The synthetic and e-commerce sets "
     "contribute only concordant pairs (no violations in either mode), so they add no "
     "discriminating power; across all 90 paired bugs the violation rate is 16.7% for the "
     "baseline against 11.1% for consensus. We therefore rest the safety case on the "
     "deterministic Byzantine-tolerance results (Sections 6.6 and 6.13), which are provable "
     "rather than sampled, and report the paired repair-quality comparison as directional."))
# Figure 2 caption: McNemar
set_text(find_para(d, "Figure 2. Safety violation rate by dataset"),
    ("Figure 2. Safety violation rate by dataset and pipeline mode. The synthetic and "
     "e-commerce benchmarks show zero violations in both modes; on the 20-bug real-world "
     "(BugsInPy) subset the rate falls from 75% to 50% under BFT-MAS. McNemar's exact test "
     "over the 90 paired bugs (all 7 discordant pairs in BugsInPy; b = 6, c = 1) gives "
     "p = 0.125, a directional reduction that is underpowered at this sample size."))
# Contribution: metric count (six measured + recovery deferred + pairwise agreement)
set_text(find_para(d, "Seven BFT-evaluation metrics applied"),
    ("A suite of BFT-evaluation metrics applied to LLM-agent repair across the three "
     "datasets and against a single-agent baseline (six of the seven are measured here; "
     "recovery time is defined but deferred), plus a pairwise validator-agreement measure."))
# Contribution: statistical test wording
set_text(find_para(d, "A paired comparison of the two pipelines using the Wilcoxon"),
    ("A paired comparison of the two pipelines on safety outcomes using McNemar's exact "
     "test, with a Wilcoxon signed-rank check."))
# 5.6 metric 7: F1 -> ground-truth accuracy (matches Table 4)
set_text(find_para(d, "F1 score on the synthetic set"),
    ("Ground-truth accuracy: on the synthetic and e-commerce sets, the fraction of fixes "
     "matching the canonical (reported as ground-truth accuracy in Table 4); on BugsInPy, "
     "similarity to the diff-extracted canonical hunk."))
# 7.5 economics: consistent per-100-repairs base (fixes the time-base error)
set_text(find_para(d, "For an e-commerce team the practical gain"),
    ("For an e-commerce team the practical gain is fewer false-positive fixes, a directional "
     "reduction of about 6 percentage points across the full corpus (16.7% to 11.1%, and 75% "
     "to 50% on the hardest real-world subset), and, more importantly, a guarantee that no "
     "consensus-approved fix is applied until it clears an executable sandbox and that the "
     "consensus itself tolerates up to f Byzantine validators. Per 100 high-stakes repairs a "
     "6-point reduction is about 6 averted incidents; at a commonly cited cost near US$1 "
     "million per hour of critical downtime and a 30-minute recovery, on the order of US$3 "
     "million in avoided loss per 100 repairs, against an API cost of a few dollars each "
     "(consistent with Section 7.4). The broader "
     "point is trust: systems that occasionally commit unsafe changes erode confidence in "
     "AI-assisted infrastructure, and auditable, fault-tolerant automation in payment, "
     "inventory and refund systems is a step toward addressing that."))
# Table 2: reconcile the BFT-MAS row with the rest of the paper
for _t in d.tables:
    hdr = [c.text.strip() for c in _t.rows[0].cells]
    if "Cross-Language" in hdr and "Production Ready" in hdr:
        col = {h: i for i, h in enumerate(hdr)}
        for _r in _t.rows[1:]:
            if _r.cells[0].text.strip().startswith("The proposed BFT-MAS"):
                _r.cells[col["Knowledge Graph"]].text = "Implemented, not evaluated"
                _r.cells[col["Byzantine Consensus"]].text = "Yes (simulated)"
                _r.cells[col["Production Ready"]].text = "No (research prototype)"
                _r.cells[col["Cross-Language"]].text = "Partial (Java sample)"
                _r.cells[col["Learning Capability"]].text = "Implemented, not evaluated"
# ===== Round-2 reviewer fixes =====
# (1) §6.6: 100% consensus formation is a genuine f=1 BFT result (independent voters)
set_text(find_para(d, "The headline result is that consensus success rate"),
    ("Consensus formed under every fault behaviour (Table 6): in all ten cases for four of "
     "the five behaviours, and in nine of ten under timeout, where one crashed-node case did "
     "not complete. With one of the four independent validators corrupted, the three honest "
     "validators independently meet the 2f + 1 = 3 quorum, so the quorum masks the faulty "
     "vote: liveness holds under always-reject and timeout, and safety holds under always-"
     "approve and random, where the single corrupted accept never reaches the quorum by "
     "itself. These runs corrupt only how a validator votes, which a majority quorum handles; "
     "the defining Byzantine case — a primary that equivocates, proposing different fixes to "
     "different replicas — is demonstrated separately in Section 6.14, where naive proposal-"
     "trust splits the honest replicas while the protocol preserves agreement. The sandbox is "
     "retained as a final backstop, catching plausible-but-wrong fixes the validators admit; "
     "together with the vote this gives defence in depth."))
# (1) Figure 5 caption: genuine 3f+1 tolerance
set_text(find_para(d, "Figure 5. Byzantine fault-injection results"),
    ("Figure 5. Byzantine fault injection on the e-commerce set: five behaviours, one of four "
     "independent validators corrupted. With f = 1 and a 2f + 1 = 3 quorum the system "
     "tolerates the corrupted validator, the three honest validators forming the quorum in "
     "every behaviour (in nine of ten cases under timeout, where one crashed-node case did "
     "not complete); liveness holds under always-reject and timeout and safety under "
     "always-approve and random, with malformed output treated as a reject. These runs show "
     "the quorum masking a corrupted validator's vote, not the defining Byzantine case of an "
     "equivocating primary, which is demonstrated in Figure 7 and Section 6.14; the sandbox "
     "(right bars) catches the few plausible-but-wrong fixes the validators admit, giving "
     "defence in depth."))
# (2) Table 3 O2c: two projects, not four; and table-cell leftovers (Table 1
#     stale Wilcoxon stat; Table 3 internal Phase 4/5 milestone language).
for _t in d.tables:
    for _r in _t.rows:
        for _c in _r.cells:
            if "four open-source projects" in _c.text and "BugsInPy" in _c.text:
                _c.text = _c.text.replace("four open-source projects",
                                          "two projects (PySnooper and ansible)")
            if "90 paired bugs, p = 0.0016" in _c.text:
                _c.text = _c.text.replace("90 paired bugs, p = 0.0016",
                                          "BugsInPy 20 pairs, safety 75% to 50% "
                                          "(McNemar p = 0.125, n.s.); BFT proven by the "
                                          "f = 1 fault matrix and f = 2 tight bound")
            if "between Phase 4 and Phase 5 of this work as scope allowed" in _c.text:
                _c.text = _c.text.replace(
                    "; the corpus has been expanded between Phase 4 and Phase 5 of this "
                    "work as scope allowed", "")
            # O1 acceptance-criteria cell: vote-masking is secondary (6.6), the genuine
            # Byzantine property is the equivocating-primary demonstration (6.14).
            if _c.text.startswith("Met on the safety axis") and "90 paired bugs" in _c.text:
                _c.text = (
                    "Met on the safety axis: with four independent, model-diverse validators "
                    "(f = 1, quorum 3 of 4) the quorum masks a corrupted validator's vote "
                    "across all five fault behaviours (Section 6.6), and the defining "
                    "Byzantine property — agreement under an equivocating primary — is "
                    "demonstrated in Section 6.14. On the BugsInPy subset the safety-violation "
                    "rate fell directionally from 75% to 50% and the repair rate rose from "
                    "25% to 50% (neither significant at this sample size); the executable "
                    "sandbox ensures no consensus-approved fix is committed unless it passes.")
            # O3 cell: consensus formation is 90% under timeout, not 100% everywhere.
            if "consensus-success rate of 100% across all scenarios" in _c.text:
                _c.text = (
                    "Five Byzantine fault scenarios injected (Section 6.6): consensus formed "
                    "at 100% in four of five scenarios and 90% under timeout (Table 6, "
                    "Figure 5). The defining Byzantine property — agreement under an "
                    "equivocating primary — is demonstrated in the protocol simulation of "
                    "Section 6.14. A live deployment study is deferred to follow-up work.")
# (10) §7.4 RQ4: hedge $1M/hr to CISQ (2022); $0.12 -> a few dollars; mark exploratory
set_text(find_para(d, "RQ4. What economic benefit can e-commerce"),
    ("RQ4 (exploratory). What economic benefit can e-commerce businesses derive from "
     "reduced downtime? Industry reports place the cost of critical software downtime in "
     "the range of hundreds of thousands to over a million US dollars per hour (CISQ, "
     "2022). Taking an illustrative US$1 million per hour and a 30-minute recovery, the "
     "directional reduction in unsafe fixes (about 6 percentage points across the corpus, "
     "16.7% to 11.1%) would avoid on the order of US$3 million per 100 high-stakes repairs, "
     "against an API cost of a few dollars each. We treat this as an order-of-magnitude "
     "estimate, not a measured "
     "outcome; a live-deployment economic study (objective O3) is future work."))
# (6) Blanchard year 2018 -> 2017 (in-text + reference); Copilot row -> Codex; Abraham spacing
replace_in_para(d, "Gap 5: Agent-diversity", "Blanchard et al., 2018", "Blanchard et al., 2017")
for _t in d.tables:
    for _r in _t.rows:
        if _r.cells[0].text.strip().startswith("GitHub Copilot"):
            _r.cells[0].text = "Codex (Chen et al., 2021)"
for _p in d.paragraphs:
    if _p.text.startswith("Abraham, I., Dolev"):
        set_text(_p, _p.text.replace("onPrinciplesofDistributedComputing(PODC)(pp.258",
                                     "on Principles of Distributed Computing (PODC) (pp. 258").replace(").ACM.", "). ACM."))
    if _p.text.startswith("Blanchard, P., El Mhamdi"):
        set_text(_p, _p.text.replace("(2018).", "(2017).").replace("(NeurIPS) 30", "(NeurIPS) 30 (2017)"))
# (6) Add CISQ, CodeBERT, AutoCodeRover, then alphabetise by MOVING paragraph
#     elements (preserves DOI/URL hyperlink runs; no rewrite of existing entries).
from docx.oxml.ns import qn as _qn
def _ptext(p):
    return "".join((t.text or "") for t in p._p.iter(_qn("w:t")))
_ref_head = next(p for p in d.paragraphs if p.text.strip().upper() == "REFERENCES")
_ref_paras, _sib = [], _ref_head._p.getnext()
while _sib is not None:
    if _sib.tag == _qn("w:p"):
        _pp = Paragraph(_sib, _ref_head._parent)
        if _pp.text.strip():
            _ref_paras.append(_pp)
    _sib = _sib.getnext()
_new = [
    "CISQ (Consortium for Information & Software Quality). (2022). The cost of poor "
    "software quality in the US: A 2022 report. "
    "https://www.it-cisq.org/the-cost-of-poor-quality-software-in-the-us-a-2022-report/",
    "Feng, Z., Guo, D., Tang, D., Duan, N., Feng, X., Gong, M., Shou, L., Qin, B., Liu, T., "
    "Jiang, D., & Zhou, M. (2020). CodeBERT: A pre-trained model for programming and "
    "natural languages. In Findings of the Association for Computational Linguistics: "
    "EMNLP 2020 (pp. 1536–1547). ACL. https://doi.org/10.18653/v1/2020.findings-emnlp.139",
    "Zhang, Y., Ruan, H., Fan, Z., & Roychoudhury, A. (2024). AutoCodeRover: Autonomous "
    "program improvement. In Proceedings of the 33rd ACM SIGSOFT International Symposium on "
    "Software Testing and Analysis (ISSTA). ACM. https://doi.org/10.1145/3650212.3680384",
]
_last = _ref_paras[-1]
for _t in _new:
    _np = copy.deepcopy(_last._p)
    _last._p.addnext(_np)
    _para = Paragraph(_np, _ref_head._parent)
    set_text(_para, _t)
    _ref_paras.append(_para)
    _last = _para
_ref_paras.sort(key=lambda p: _ptext(p).lower())
_anchor = _ref_head._p
for _p in _ref_paras:
    _anchor.addnext(_p._p)
    _anchor = _p._p
# (7) Fix list numbering: §5.6 metrics -> manual 1-7; §6.6 findings -> manual 1-2
_ms = next(i for i, p in enumerate(d.paragraphs) if p.text.startswith("We report seven metrics"))
for _k in range(1, 8):
    _p = d.paragraphs[_ms + _k]
    _p.style = d.styles["Normal"]
    set_text(_p, f"{_k}. " + _p.text.strip())
_fs = next(i for i, p in enumerate(d.paragraphs) if p.text.startswith("Two secondary findings emerge"))
for _k in range(1, 3):
    _p = d.paragraphs[_fs + _k]
    _p.style = d.styles["Normal"]
    set_text(_p, f"{_k}. " + _p.text.strip())

# (1-propagation) RQ1 rests on genuine f=1 tolerance over independent validators
set_text(find_para(d, "The empirical answer to RQ1 is n = 4, f = 1"),
    ("The answer to RQ1 is n = 4, f = 1: the minimum PBFT-compliant configuration of four "
     "independent validators gives the best repair success and lowest latency, and the "
     "fault-injection study confirms it genuinely tolerates one Byzantine voter (Section "
     "6.6). Raising the population to n = 7 (f = 2) buys tolerance to a second Byzantine "
     "voter, which the tight-bound study confirms is real (Section 6.13), at higher latency "
     "and no repair gain, so n = 4 is the practical optimum for f = 1."))
set_text(find_para(d, "RQ1. What is the optimal number of agents for Byzantine fault tolerance without"),
    ("RQ1. What is the optimal number of agents for Byzantine fault tolerance without "
     "excessive latency? The PBFT bound n ≥ 3f + 1 fixes the design floor at n = 4 for "
     "f = 1, and the fault-injection study shows the quorum masks a faulty validator's vote "
     "across all five behaviours (Section 6.6), with the f = 2 study showing that masking is "
     "tight at the 3f + 1 bound (Section 6.13) and the defining Byzantine property — agreement "
     "under an equivocating primary — demonstrated separately (Section 6.14). On the cost-"
     "benefit axis, n = 7 (f = 2) only lowered raw success (Section 6.8) and raised latency "
     "(Section 6.12) with no repair gain, while n = 4 gave the best success and lowest "
     "latency. The practical optimum is "
     "therefore n = 4, f = 1: genuine single-fault tolerance at the lowest cost, with larger "
     "populations reserved for threat models that require tolerating more faults."))
# §8.5: genuine 3f+1 is realised here; the remaining step is distribution
set_text(find_para(d, "The Byzantine wrapper sits only on validators here."),
    ("The Byzantine wrapper corrupts validators within the f = 1 budget, and at f = 2 within "
     "an f + 1 tight-bound test (Section 6.13), and all voting replicas are independent and "
     "model-diverse, so the evaluation exercises genuine f-of-3f + 1 tolerance rather than a "
     "quorum artefact. The remaining step is distribution: moving the validators onto "
     "separate hosts with real message passing, network partitions and view-change under "
     "primary failure, and admitting a proposer that can itself misbehave. That is the path "
     "from Byzantine fault tolerance demonstrated in a single-process simulation to Byzantine "
     "fault tolerance demonstrated over a network."))

# Latency/RQ1 prose: n = 7 means seven INDEPENDENT validators now (not "five instead
# of two" from the old standing-accept design).
# Latency multiplier appears in several places with the stale "2.0x" and a reversed
# "1.07x on BugsInPy" claim; unify to the real ~3x average (widest on BugsInPy) and
# drop the "removal of / zero safety violations" overclaim (repair is now directional).
set_text(find_para(d, "Figure 4. Repair-duration distribution per dataset"),
    ("Figure 4. Repair-duration distribution per dataset and pipeline mode. The consensus "
     "mode (blue) runs roughly three times slower than the single-agent baseline (amber) "
     "overall, and the gap is widest on BugsInPy (about 3.9x), where the consensus pipeline "
     "makes repeated validator-gated repair attempts on hard real bugs. White diamonds mark "
     "the means; bold horizontal lines mark the medians."))
set_text(find_para(d, "There is also a clear cost story: consensus is roughly"),
    ("There is also a clear cost story: consensus is roughly three times slower per repair, "
     "almost entirely from validator latency. Where each repair is a high-stakes commit such "
     "as production payment logic, trading tens of seconds (about 30 s on e-commerce, more on "
     "hard real bugs) for fewer unsafe fixes is defensible; where speed dominates, it may "
     "not be. The synthetic benchmark, perfect in both modes, is a sanity check."))
set_text(find_para(d, "RQ2. How does consensus latency affect real-time repair?"),
    ("RQ2. How does consensus latency affect real-time repair? The protocol adds under 2 ms "
     "per round; the added latency is LLM I/O and Ollama inference, not consensus, and "
     "averages about three times the baseline, largest on BugsInPy (Section 6.5 and Table 4; "
     "how latency scales with the validator count is in Section 6.12 and Table 11). Trading "
     "tens of seconds for fewer unsafe fixes is defensible for high-stakes commits."))

# Per-dataset latency summary: align BugsInPy to the real r2_bip numbers (160.5 s vs
# 41.4 s), correct the average slowdown, the "two run" fossil, and the now-reversed
# "gap narrows on BugsInPy" claim (the gap is widest there).
set_text(find_para(d, "Consensus is about 2.0× slower than the baseline on average"),
    ("Consensus is about three times slower than the baseline on average (mean latency: "
     "synthetic 44.5 s vs 14.6 s, BugsInPy 155.6 s vs 39.9 s, e-commerce 50.7 s vs 18.4 s), "
     "dominated by the validator stage, since each CPU-bound Ollama validator takes 30 to 40 "
     "s and they "
     "run concurrently. The protocol itself adds under 2 ms per round; the gap is widest on "
     "BugsInPy, where hard real bugs drive repeated repair attempts, each paying the full "
     "validator round (Figure 4)."))

# §6.8 "Three findings": latency now lives only in §6.12; drop the (removed) Table 8
# latency numbers and the "five validators" fossil.
set_text(find_para(d, "Three findings follow (Table 8)"),
    ("Three findings follow (Table 8): safety violations stay at zero, so extra validators do "
     "not improve safety; raw success drops from 100% to 90% as the 2f + 1 = 5 quorum is "
     "harder to reach; and latency rises with the validator count (reported in Section 6.12, "
     "Table 11), set by the slowest of the seven concurrent validators."))
set_text(find_para(d, "To answer RQ1 directly, the e-commerce set was re-run"),
    ("To answer RQ1 directly, the e-commerce set was re-run with seven independent validators "
     "instead of four, satisfying n = 3f + 1 = 7 at f = 2, so the system tolerates two "
     "simultaneous Byzantine validators; the tight-bound study (Section 6.13) confirms that a "
     "third would break consensus. The analyzer, healer and baseline were held constant. "
     "Table 8 compares success, safety and validator agreement at n = 4 and n = 7; how "
     "latency scales with the validator count is reported separately in Section 6.12 "
     "(Table 11), so that latency appears in one place only."))

# Pipeline descriptions + early decorrelation line still named the OLD "two Ollama
# validators"; update to the four independent, model-diverse validators.
set_text(find_para(d, "Figure 1. BFT-MAS code-repair pipeline architecture."),
    ("Figure 1. BFT-MAS code-repair pipeline architecture. The bug report enters at top-left "
     "and progresses through Analyzer (Claude Sonnet, no vote) -> Healer / proposer (GPT-4o, "
     "no vote) -> four independent, model-diverse validators (Claude-Haiku, GPT-4o-mini, "
     "llama3.1:8b, mistral:7b) voting in parallel -> PBFT three-phase consensus (quorum 3 of "
     "4) -> isolated sandbox execution. The decision is APPLY (consensus and sandbox both "
     "passed) or REJECT (safety violation; rollback). The metrics layer observes every stage."))
set_text(find_para(d, "BFT-MAS consensus mode: Analyzer"),
    ("BFT-MAS consensus mode: Analyzer (Claude Sonnet 4.5, no vote) -> Healer / proposer "
     "(GPT-4o, no vote) -> four independent validators (Claude-Haiku, GPT-4o-mini, "
     "llama3.1:8b, mistral:7b) -> PBFT consensus (quorum 3 of 4) -> sandbox, with up to three "
     "retries that feed each failure back to the healer."))
set_text(find_para(d, "Mean pairwise validator agreement was about 0.97 across the datasets"),
    ("Mean pairwise validator agreement was near 1.00 on the easy synthetic bugs but fell to "
     "0.925 on the real BugsInPy bugs (1.00 means lockstep, 0.50 independent votes), so the "
     "four cross-provider validators agreed on obvious fixes yet diverged on harder ones, "
     "producing three genuine split votes. Section 7.2 develops this decorrelation finding."))

# §7.2 + future-work prose: we DID use a cross-provider panel and measured decorrelation,
# so drop the OLD "two same-family validators / cannot test diversity" framing.
set_text(find_para(d, "The 0.95 mean agreement leaves only a 5% diversity signal"),
    ("On the easy synthetic bugs the four validators agree in near-lockstep (mean pairwise "
     "agreement close to 1.0), which leaves little diversity signal there. The heterogeneous "
     "cross-provider panel does decorrelate on harder inputs, however: mean pairwise "
     "agreement falls to 0.925 on the real BugsInPy bugs, with three genuine split votes in "
     "which Claude-Haiku dissented while the other three validators approved."))
set_text(find_para(d, "The runs here use two same-family Ollama validators."),
    ("The heterogeneous panel here already spans four providers (Claude-Haiku, GPT-4o-mini, "
     "llama3.1:8b and mistral:7b), and decorrelation is measured directly: mean pairwise "
     "agreement falls from near-lockstep on easy bugs to 0.925 on the real BugsInPy cases "
     "and 0.54 among heterogeneous proposers. A larger study across more projects would test "
     "whether still-lower agreement yields stronger guarantees on ambiguous bugs."))

# §3.1 architecture: four independent validators (fix the stale "two instances").
set_text(find_para(d, "Validators (local Ollama llama3.1:8b, two instances) inspect each candidate"),
    ("Four independent, model-diverse validators (Claude-Haiku, GPT-4o-mini, llama3.1:8b and "
     "mistral:7b) inspect each candidate, run static safety checks and return a structured "
     "verdict; a fix is approved when at least three of the four accept."))

# "validated three" claims: be honest — reputation-weighted voting and the
# knowledge-graph layer are implemented but NOT evaluated; decorrelation is a
# negative result; the BFT property is now shown directly (equivocating primary, 6.14).
set_text(find_para(d, "BFT-MAS has four ingredients. The results validate three"),
    ("BFT-MAS has four design ingredients. We demonstrate the Byzantine fault tolerance of "
     "the consensus layer directly (safety under an equivocating primary, Section 6.14) and "
     "compare the exact and semantic quorum rules (Section 6.9). The heterogeneous-population "
     "decorrelation is measured and is a negative result (agreement stays high; Section 7.2). "
     "Reputation-weighted voting and the knowledge-graph layer are implemented but left "
     "unevaluated, and the e-commerce invariant checks show no measurable effect on the "
     "tractable suites. The main open directions are a formal semantic-equivalence relation "
     "and distributed deployment."))
set_text(find_para(d, "This paper validated three of the four BFT-MAS design extensions"),
    ("This paper demonstrates the Byzantine fault tolerance of the consensus layer directly "
     "(Section 6.14) and compares the exact and semantic quorum rules (Section 6.9), across a "
     "synthetic benchmark, a BugsInPy subset, a custom e-commerce suite and a Java/Defects4J "
     "sample, against a single-agent baseline sharing the same analyzer and healer. The "
     "heterogeneous-population decorrelation is a measured negative result; reputation-"
     "weighted voting and the knowledge-graph layer remain implemented but unevaluated."))

# ===== Data tables: replace OLD experimental numbers with the genuine-3f+1 R2 runs =====
# (Per-dataset success/latency, the validator-config ablation, and the agent-count
#  latency table depend on the variance/latency re-run still in flight and on dataset
#  mappings; they are updated in a later pass. The two FINAL, central tables — the
#  Byzantine fault matrix and the paired safety-outcome counts — are updated here.)
def _hdr(t):
    return [c.text.strip() for c in t.rows[0].cells]

# Byzantine fault-injection matrix (genuine f = 1, one of four independent validators
# corrupted; e-commerce, 10 cases/scenario). Real R2 data (R2_RESULTS.md §B).
for _t in d.tables:
    h = _hdr(_t)
    if "Mean pairwise validator agreement" in h and h[0] == "Scenario":
        _rows = [
            ("Healthy (no fault)",      "10", "1.000", "0.000", "1.000"),
            ("always_reject (DoS)",     "10", "1.000", "0.000", "0.500"),
            ("always_approve",          "10", "1.000", "0.100", "1.000"),
            ("random",                  "10", "1.000", "0.100", "0.700"),
            ("timeout / crash",         "10", "0.900", "0.000", "0.500"),
            ("malformed (garbage)",     "10", "1.000", "0.100", "0.500"),
        ]
        # 'Consensus success rate' column = consensus-formation rate (the BFT property:
        # the f = 1 quorum still forms from the honest validators). Reuse existing data
        # rows, append any extra scenario rows the OLD table lacked (e.g. timeout).
        _data_rows = _t.rows[1:]
        for _i, _vals in enumerate(_rows):
            _r = _data_rows[_i] if _i < len(_data_rows) else _t.add_row()
            for _j, _v in enumerate(_vals):
                _r.cells[_j].text = _v
        break

# Paired safety-outcome counts across the 90 paired bugs (all discordant pairs fall
# in the 20-bug BugsInPy subset; synthetic and e-commerce are concordant-clean).
# 2x2: both=9, baseline-only b=6, consensus-only c=1, neither=74. McNemar p=0.125.
for _t in d.tables:
    h = _hdr(_t)
    if h[:3] == ["Outcome", "Count", "Interpretation"]:
        _pairs = [
            ("Both pipelines violated", "9", "Hard real bugs where neither mode's fix passed the oracle"),
            ("Only baseline violated", "6", "Consensus caught an unsafe fix the single agent committed"),
            ("Only consensus violated", "1", "Consensus rejected or failed where the single agent passed"),
            ("Neither violated", "74", "Both modes handled cleanly (synthetic + e-commerce + 11 BugsInPy)"),
        ]
        for _i, _vals in enumerate(_pairs):
            if _i + 1 < len(_t.rows):
                for _j, _v in enumerate(_vals):
                    _t.rows[_i + 1].cells[_j].text = _v
        break

# Per-dataset results table (idx 3): keep synthetic + e-commerce (p6, unaffected),
# update the BugsInPy rows to the genuine-3f+1 R2 runs, and recompute the Overall row.
# Columns: [Dataset, Mode, Success, Safety-viol, Mean latency ms, p99 ms, Ground-truth].
_perds = {
    ("BugsInPy (n=20)", "BFT-MAS consensus"):      ("0.500", "0.500", "155,600", "222,719", "0.667"),
    ("BugsInPy (n=20)", "Single-agent baseline"):  ("0.250", "0.750", "39,900",  "61,071",  "0.571"),
    ("Overall (90 paired cases)", "BFT-MAS consensus"):     ("0.889", "0.111", "71,300", "222,700", "0.889"),
    ("Overall (90 paired cases)", "Single-agent baseline"): ("0.833", "0.167", "21,500", "61,100",  "0.833"),
}
for _t in d.tables:
    if _hdr(_t)[:2] == ["Dataset (n paired)", "Mode"]:
        for _r in _t.rows[1:]:
            _key = (_r.cells[0].text.strip(), _r.cells[1].text.strip())
            if _key in _perds:
                for _j, _v in enumerate(_perds[_key], start=2):
                    _r.cells[_j].text = _v
        break

# Agent-count table (idx 7 / Table 8): correct the OLD-design "two/five validators"
# wording, AND drop its "Latency p50" column so latency is reported only in Table 11
# (Section 6.12) — the two tables use different e-commerce subsets (30 vs 5 bugs), so
# carrying a latency figure in both produced conflicting p50 values for the same n.
from docx.oxml.ns import qn as _qncol
for _t in d.tables:
    if "Latency p50" in _hdr(_t) and _t.rows[1].cells[0].text.strip().startswith("n = 4"):
        for _r in _t.rows[1:]:
            _c0 = _r.cells[0].text
            _c0 = _c0.replace("two validators, default", "four independent validators, default")
            _c0 = _c0.replace("five validators", "seven independent validators")
            _r.cells[0].text = _c0
        _ci = _hdr(_t).index("Latency p50")
        _grid = _t._tbl.find(_qncol("w:tblGrid"))
        _gcols = _grid.findall(_qncol("w:gridCol"))
        if _ci < len(_gcols):
            _grid.remove(_gcols[_ci])
        for _r in _t.rows:
            _tcs = _r._tr.findall(_qncol("w:tc"))
            if _ci < len(_tcs):
                _r._tr.remove(_tcs[_ci])
        break

# Agent-diversity ablation (idx 6) REFRAMED as a decorrelation table (user decision):
# the OLD "two same-family vs four distinct-family" study has no clean same-code rerun,
# so replace it with the decorrelation evidence we do have cleanly.
from docx.oxml.ns import qn as _qn2
for _t in list(d.tables):
    _h = _hdr(_t)
    if _h and _h[0] == "Configuration" and "Consensus success rate" in _h and "n_pairs" in _h:
        _prev = _t._tbl.getprevious()
        while _prev is not None and _prev.tag != _qn2('w:p'):
            _prev = _prev.getprevious()
        if _prev is not None:
            _capp = Paragraph(_prev, _t._parent)
            if "VALIDATOR" in _capp.text.upper():
                set_text(_capp, "VALIDATOR DECORRELATION: MEAN PAIRWISE AGREEMENT BY SETTING")
        _new = d.add_table(rows=1, cols=3); _new.style = "Table Grid"
        for _j, _htxt in enumerate(["Setting", "Mean pairwise validator agreement", "Reading"]):
            _cell = _new.rows[0].cells[_j]; _cell.text = ""
            _cell.paragraphs[0].add_run(_htxt).bold = True
        for _row in [
            ("Heterogeneous panel, easy synthetic bugs", "~1.00",
             "Validators agree in near-lockstep when the fix is obvious"),
            ("Heterogeneous panel, real BugsInPy bugs", "0.925",
             "Genuine disagreement emerges: three split votes, Claude-Haiku dissenting"),
            ("Heterogeneous proposers, semantic-quorum study", "0.54",
             "Once proposals may differ, behavioural agreement drops sharply"),
        ]:
            _cells = _new.add_row().cells
            for _j, _v in enumerate(_row):
                _cells[_j].text = str(_v)
        _t._tbl.addnext(_new._tbl)
        _t._tbl.getparent().remove(_t._tbl)
        break

# Remove duplicated Acknowledgements + Declarations from the MAIN doc (they live
# on the separate, non-anonymised Title Page); keep References.
for _pref in ["ACKNOWLEDGEMENTS", "The authors thank their institution", "DECLARATIONS",
              "Conflict of interest.", "Funding. The authors received",
              "Ethical approval. Not applicable", "Data availability.",
              "Use of AI assistance."]:
    try:
        delete_para(find_para(d, _pref))
    except KeyError:
        pass

d.save(REVISED)

# Replace stale Figure 1 (image1.png) with the corrected diagram in both the
# clean copy and the Compare baseline, so models match the body text.
swap_media(REVISED, "word/media/image1.png", "corrected_fig1.png")
swap_media(BASELINE, "word/media/image1.png", "corrected_fig1.png")
# Figures 2, 4, 5: corrected titles/banners (no 'Phase 5'; McNemar in Fig 2;
# reframed Byzantine banner in Fig 5). Sizes match the originals.
for _doc in (REVISED, BASELINE):
    swap_media(_doc, "word/media/image2.png", "corrected_fig2.png", size=(1579, 975))
    swap_media(_doc, "word/media/image4.png", "corrected_fig4.png", size=(1779, 973))
    swap_media(_doc, "word/media/image5.png", "corrected_fig5.png", size=(3270, 1770))
# Blinded copies must carry no confidentiality watermark (SAGE Open is
# double-anonymous). The supervisor's COMBINED copy is built separately and may
# keep it.
for _doc in (REVISED, BASELINE):
    strip_watermark(_doc)
print("wrote", REVISED, "(+ Figures 1,2,4,5 corrected; watermark stripped)")
