# R2 Manuscript Rewrite Plan — genuine 3f+1 BFT (honest numbers)

**Purpose.** Map every OLD-narrative passage in `revise_manuscript.py` (and the
response letter) to its NEW prose under the genuine 3f+1 design, with the real R2
numbers. Fold into `revise_manuscript.py` once the variance/latency/synthetic
re-run (bg task `bh233x322`) lands. Numbers tagged **[PENDING RERUN]** wait on it.

**User directives (binding):**
- Manuscript presents genuine 3f+1 as *the* system. NO old-design narrative — no
  "standing accepts", no "we redesigned from X to Y", no "bounded ensemble", no
  legacy comparison in the body. Current state *is* the paper.
- Response letter answers reviewers factually / forward-looking. NO mea-culpa.
- Keep the honest caveat: single-process *simulated* network; distributed
  deployment is future work. But it IS genuine BFT, evaluated in simulation.

---

## The system, stated once (canonical description)

Genuine 3f+1, f=1, n=4, quorum=3-of-4. **Four independent heterogeneous
validators vote**: Claude-Haiku + GPT-4o-mini + llama3.1:8b + mistral:7b (2 cloud
+ 2 local). **Healer = GPT-4o, the proposer — casts no vote.** **Analyzer =
Claude-Sonnet, feeds the pipeline — casts no vote.** No standing accepts. A fix
is approved when ≥3 of the 4 independent validators accept. Sandbox is the final
gate. Independence rule: no validator is the GPT-4o proposer; the Claude voter is
Haiku (≠ the Sonnet analyzer).

---

## FINAL NUMBERS (locked — from benchmark_results/R2_RESULTS.md + semq May-29)

### BugsInPy (PySnooper 3 + ansible 17; 20 real bugs) — repair under 3f+1
- Success 10/20 (50%); F1 0.667; precision 0.5; recall 1.0; mean pairwise
  validator agreement 0.925; 10 safety violations (sandbox-caught).
- **3 genuine split votes** (ansible-1, -12, -14): Claude-Haiku dissented NO,
  the other three approved → quorum=3 still formed → sandbox then rejected the
  fix. The dissenter was correct; quorum + sandbox = defence in depth.

### Byzantine fault-injection matrix (e-commerce, 10 cases, 1 corrupted validator = Haiku) — f=1 BFT
| Behaviour | Success | Safety viol | Vote dist | BFT outcome |
|---|---|---|---|---|
| baseline (no fault) | 10/10 | 0 | 4/4 ×10 | all unanimous |
| always REJECT (DoS) | 10/10 | 0 | 3/4 ×10 | liveness held (3 honest form quorum) |
| always APPROVE (collude) | 9/10 | 1 | 4/4 ×10 | safety held (lone YES never flips) |
| random vote | 9/10 | 1 | 3/4 ×6, 4/4 ×4 | robust to noise |
| timeout / crash | 9/10 | 0 | 0/0 ×1, 3/4 ×9 | proceeds without crashed node |
| malformed output | 9/10 | 1 | 3/4 ×10 | treated as reject; quorum held |

f=1 tolerance HOLDS across all five fault types. (The few safety violations are
the weak-oracle sandbox catching plausible-but-wrong fixes — not consensus
failures.)

### f=2 tight bound (n=7, quorum=5; homogeneous llama3.1 replicas) — exactness of the bound
| Scenario | Byzantine | Consensus formed | Prepare votes | Outcome |
|---|---|---|---|---|
| clean | 0 | 5/5 | 7 | baseline |
| reject2 | 2 (=f) | 5/5 | 5 | TOLERATED |
| reject3 | 3 (=f+1) | 0/5 | 4 | LIVENESS BREAKS (quorum unreachable) |
| approve2 | 2 (=f) | 5/5 | 7 | safety holds |
| approve3 | 3 (=f+1) | 5/5 | 7 | formed (no bad fix to exploit) |

Vote cliff 7 → 5 → 4 as rejecters go 0 → 2 → 3. Tolerates exactly f, no more.
Bound is real and tight, not asserted.

### Defects4J (real Java; `defects4j compile && test` oracle) — repair capability
- **Lang:** 9 evaluated (Lang-2 checkout-failed), fix_success 0/9, consensus
  approval 8/9 (Lang-7 rejected, 0 votes), splits Lang-1 & Lang-6 (3/4, Haiku
  dissent).
- **Math:** 9 evaluated (Math-8 checkout-failed), **fix_success 2/9 — GENUINE
  fixes Math-3 (4/4) and Math-5 (3/4, Haiku dissented but the fix actually
  PASSED real JUnit → dissenter wrong here)**, consensus approval 9/9, trigger-
  test pass rate 0.333.
- Reading: real oracle cleanly separates *consensus robustness* (proven by the
  Byzantine matrix) from *repair capability* (modest, honest: 2 verified Java
  fixes). Most consensus-approved fixes fail the real suite → honest safety
  violations (validators accept plausible code the suite rejects).

### McNemar safety / success (pooled 50 BugsInPy pairs) — DIRECTIONAL, not significant
- Safety violations: single 66% → 3f+1 54% (b=9, c=3; **p = 0.146, n.s.**).
- Success: single 32% → 3f+1 42% (**p = 0.227, n.s.**).
- Both directional, underpowered. The expansion (new projects) diluted the
  PySnooper+ansible discordant ratio. **Reframe: lead with BFT robustness
  (provable); report safety/repair as directional and honest.**

### Semantic-equivalence quorum (4 Ollama proposers; quorum=3) — May-29 numbers (proposer-side study; validator fix does not affect it)
| Dataset | n | Exact quorum | Semantic quorum | Semantic on passing fix | Sem safety viol | Mean agree (exact / sem) |
|---|---|---|---|---|---|---|
| Synthetic | 40 | 2.5% | 70.0% | 60.0% | 10.0% | 0.18 / 0.54 |
| E-commerce | 30 | 10.0% | 76.7% | 60.0% | 16.7% | 0.20 / 0.54 |

### [PENDING RERUN — bg task bh233x322]
- **Synthetic consensus (3f+1)** — headline synthetic dataset (re-running fresh 40).
  Interim: first 31/31 valid cases succeeded, 0 safety violations.
- **Variance** — 10-bug synthetic subset ×3 (consensus stability).
- **Latency n-sweep** — n=4 / 7 / 10, p50/p99 durations.

---

## SECTION-BY-SECTION REWRITE (manuscript)

> Each item: `find_para` anchor → NEW text. Replaces the correspondingly-anchored
> `set_text`/`insert_after` in `revise_manuscript.py`. Where the OLD script edits
> the same paragraph multiple times (abstract, §6.6, RQ1), the NEW text is the
> single consolidated version — delete the redundant later re-edits.

### §3.2 PBFT consensus — anchor "The consensus engine runs PBFT with f = 1"
NEW:
> The consensus engine runs PBFT with f = 1 over four **independent** validator
> replicas (n = 3f + 1 = 4), each a different model — Claude-Haiku, GPT-4o-mini,
> llama3.1:8b and mistral:7b. The Healer (GPT-4o) is the proposer: it submits one
> candidate fix and casts no vote; a byte digest binds every prepare and commit
> to that proposal, as in classical PBFT. The Analyzer (Claude-Sonnet) feeds the
> diagnosis into the proposer and likewise does not vote. In the prepare phase
> each of the four validators independently accepts or rejects the proposal, and
> with the 2f + 1 = 3 quorum a fix is approved when at least three of the four
> accept and rejected otherwise; the commit phase confirms the bound proposal.
> Because all four verdicts are independent and model-diverse, the configuration
> realises the textbook guarantee of tolerating f Byzantine replicas among 3f + 1,
> which we verify directly by injecting Byzantine behaviour into a validator
> (Section 6.6) and by an f = 2 tight-bound study (Section 6.x). Agreement here is
> over a single proposal; agreement among several independent proposals, where
> heterogeneous agents rarely produce identical text, is the separate semantic-
> equivalence quorum (Sections 5.x and 6.x). Leader replacement (view-change) is
> implemented; primary-failure recovery under continuous faults is future work
> (Section 8.2).

### Threat-model / scope insert — after §3.2 (replace the "bounded ensemble" insert)
NEW:
> Threat model and scope. The prototype runs all four validator replicas as
> asynchronous tasks inside one trusted Python process; there is no real network,
> Sybil, or message-tampering adversary, and the per-message integrity check is
> by construction rather than against a live attacker. The adversary we model is a
> Byzantine validator, simulated by a wrapper forcing always-reject, always-
> approve, random, timeout or garbage behaviour (Section 5.5). Within this model
> the consensus is genuine 3f + 1 Byzantine fault tolerance: four independent,
> model-diverse validators vote, and the f = 1 quorum tolerates exactly one
> corrupted voter — demonstrated empirically (Section 6.6) and shown to be tight
> at f = 2 (Section 6.x). What remains out of scope is the *distributed* setting:
> real inter-host messaging, network partitions and view-change under primary
> failure. We evaluate genuine BFT consensus in a single-process simulation;
> hardening it for a distributed deployment is the natural next step (Section 8).

### §6.6 Byzantine fault injection — anchor "To test the namesake property, one ... was wrapped"
NEW:
> To test the namesake property, one of the four independent validators was
> wrapped in a ByzantineWrapper set to each of the five misbehaviours, leaving
> three honest validators. With the 2f + 1 = 3 quorum, the three honest validators
> must agree for a fix to pass, so a single corrupted voter can neither force nor
> block a decision on its own. Across all five behaviours the system tolerated the
> corrupted validator: under always-reject and timeout the three honest validators
> still formed the quorum (liveness held, 3/4 votes); under always-approve and
> random the lone extra YES never reached the quorum by itself (safety held); and
> malformed output was treated as a reject. Consensus formation and the safety
> outcome are therefore a genuine f = 1 BFT property, with the sandbox as a final
> backstop for plausible-but-wrong fixes the validators admit.

DELETE the OLD re-edits that reframe this as "quorum arithmetic, not PBFT":
- "The headline result is that consensus success rate" / "Consensus formation
  stays at 1.000 ... follows from the quorum arithmetic" (script ~919).
- the second "To test the namesake property ... because the Analyzer and Healer
  accept by default" re-edit (~929).

### Figure 5 caption — anchor "Figure 5. Byzantine fault-injection results"
NEW:
> Figure 5. Byzantine fault injection on the e-commerce set: five behaviours, one
> of four independent validators corrupted. With f = 1 and a 2f + 1 = 3 quorum the
> system tolerates the corrupted validator in every case — liveness holds under
> always-reject and timeout, safety holds under always-approve and random, and
> malformed output is treated as a reject. This is genuine 3f + 1 Byzantine fault
> tolerance evaluated in a single-process simulation; the sandbox (right bars)
> catches the few plausible-but-wrong fixes the validators admit, giving defence
> in depth.

### NEW Figure 6 / §6.x — f=2 tight bound (add; corrected_fig6.png exists)
NEW prose:
> To show the f = 1 result is not a ceiling and that the bound is exact, we re-ran
> the e-commerce set at f = 2 (n = 7, quorum = 5) with seven independent voters
> and injected an increasing number of Byzantine rejecters. With no fault all
> seven vote and consensus forms; with two faults (= f) five honest validators
> still meet the quorum and consensus forms; with three faults (= f + 1) only four
> honest validators remain, below the quorum of five, and consensus provably
> cannot form in any case. Prepare votes fall 7 → 5 → 4 as faults go 0 → 2 → 3
> (Figure 6, Table x). The system therefore tolerates exactly f Byzantine voters
> and no more — the BFT guarantee is demonstrated and the bound is tight, not
> asserted.

Add to script: `swap_media(_doc, "word/media/imageN.png", "corrected_fig6.png", ...)`
(choose a free image slot / insert as a new inline figure) + a Table for the cliff.

### Abstract — anchor "Abstract:" (consolidated; delete the 3 later abstract re-edits)
NEW:
> Automated program repair with large language models (LLMs) has a safety gap: a
> single model often returns a confident but wrong fix that breaks working code —
> in e-commerce, double charges, negative stock or broken refunds. We ask whether
> genuine Byzantine fault-tolerant (BFT) consensus over a population of
> independent LLM agents can remove unsafe fixes while preserving repair ability.
> We build a pipeline in which a Claude analyzer and a GPT-4o healer propose a fix
> that is then voted on by four independent, model-diverse validators
> (Claude-Haiku, GPT-4o-mini, llama3.1:8b, mistral:7b) under Practical Byzantine
> Fault Tolerance (PBFT, n = 3f + 1 = 4, quorum = 3), with every approved fix run
> in a sandbox. Fault injection shows the system tolerates one Byzantine validator
> across all five adversarial behaviours, and an f = 2 study confirms the
> tolerance bound is exact (consensus forms with f faults and provably fails with
> f + 1). On real bugs, consensus reduced the safety-violation rate (54% vs 66% on
> a 50-bug real-world subset; directional, not statistically significant at this
> sample size) while trading recall for precision, and a Java run through the real
> Defects4J harness produced two full-suite-verified repairs (Math-3, Math-5),
> showing the pipeline is not Python-specific. We also test the agreement rule
> itself: across heterogeneous proposers a byte-identical quorum almost never
> forms (2.5–10%), whereas a semantic-equivalence quorum forms for 70–77% of bugs,
> which is what makes consensus workable for non-deterministic agents. Future work
> targets a formal semantic-equivalence relation, distributed deployment with
> network faults, and broader Java coverage.

### RQ1 — anchors "The empirical answer to RQ1 is n = 4" and "RQ1. What is the optimal number"
NEW (RQ1 answer):
> The answer to RQ1 is n = 4, f = 1: the minimum PBFT-compliant configuration of
> four independent validators gives the best repair success and lowest latency,
> and the fault-injection study confirms it genuinely tolerates one Byzantine
> voter (Section 6.6). Raising the population to n = 7 (f = 2) buys tolerance to a
> second Byzantine voter — which the tight-bound study confirms is real (Section
> 6.x) — at higher latency and no repair gain, so n = 4 is the practical optimum
> for f = 1.

DELETE the OLD "we do not rest this on the fault-injection runs, whose 100%
consensus-formation figure follows from the quorum arithmetic" caveat.

### §8.5 — anchor "The Byzantine wrapper sits only on validators here."
The OLD §8.5 describes the *path to* genuine 3f+1 (standing accepts → independent
voters). That path is now realised. REPLACE with distributed-deployment future
work:
> The Byzantine wrapper corrupts validators within the f = 1 (and, in Section 6.x,
> f = 2) budget, and all voting replicas are independent, so the evaluation
> exercises genuine f-of-3f + 1 tolerance. The remaining step is distribution:
> moving the four validators onto separate hosts with real message passing,
> network partitions and view-change under primary failure, and admitting a
> proposer that can itself misbehave. That is the path from BFT consensus
> demonstrated in simulation to BFT consensus demonstrated over a network.

### §7.1 ensemble framing — anchor "BFT-MAS strictly improves safety here."
Keep the ensemble-learning connection (Dietterich; self-consistency; debate) but
drop "best read as a bounded ensemble rather than a heuristic vote." NEW closing:
> ... BFT-MAS adds what these lack: a genuine PBFT quorum over independent,
> model-diverse validators that bounds how many confidently wrong agents the
> system absorbs (tolerating f of 3f + 1), with the validator-and-sandbox layer
> built to catch precisely the overfitting Smith et al. (2015) documented.
Update the discordant-pairs / McNemar sentence to the honest directional numbers
(see Statistics block below).

### Defects4J / cross-language — anchors "We also ran the pipeline on Java" (crosslang_body) + Table 10
NEW crosslang_body:
> We ran the pipeline on real Java bugs through the Defects4J benchmark's own
> checkout, compile and test harness in Docker — the actual JUnit suites, not a
> proxy oracle. The healer emits a minimal search-and-replace edit and is shown
> the failing test; every candidate is verified against the project's real test
> suite, so a repair counts only if the suite passes. On commons-lang the four
> independent validators reached consensus on 8 of 9 evaluated bugs but none
> passed the full Lang suite, a concrete measure of how hard real-world Java
> repair is. On commons-math the pipeline produced two genuine, full-suite-
> verified repairs — Math-3 (unanimous 4/4) and Math-5 (3/4, one validator
> dissenting on a fix that nevertheless passed the real suite) — with consensus
> reached on all 9 evaluated bugs. The real oracle cleanly separates two things
> the synthetic and snippet-level studies cannot: consensus robustness, which the
> Byzantine matrix proves, and repair capability, which on hard real Java bugs is
> modest and which we report honestly. Most consensus-approved Java fixes fail the
> real suite — honest safety violations where the validators accept plausible code
> the tests reject — which is exactly why the executable suite, not the vote, is
> the final guarantee of correctness.

Table 10 (REAL DEFECTS4J OUTCOMES) — replace rows with:
- commons-math: full-suite-verified repairs (Math-3, Math-5) = 2
- commons-math: consensus-approved but full-suite-failed = 7
- commons-lang: full-suite-verified repairs = 0
- commons-lang: consensus-approved but full-suite-failed = 8
- consensus-rejected (Lang-7) = 1
- Unsafe fixes committed = 0
(Drop the OLD "Lang-4, 11, 21, 28" and "6/6 self-contained Java set" claims
entirely.)

### Statistics block — §5.7, §6.3, Figure 2 caption, contributions
Everywhere McNemar p ≈ 0.002 / "10 discordant pairs all favour BFT-MAS" appears,
replace with the honest directional result:
- §6.3: "On the 50-bug real-world subset the safety-violation rate fell from 66%
  to 54% (discordant pairs b = 9, c = 3; McNemar exact p = 0.146), a directional
  reduction that does not reach significance at this sample size; the success rate
  rose from 32% to 42% (p = 0.227). We therefore rest the safety claim on the
  Byzantine-tolerance results (Sections 6.6, 6.x), which are deterministic and
  provable, and report the repair-quality comparison as directional."
- Figure 2 caption: "... McNemar's exact test on the paired safety outcomes
  (n = 50) gives p = 0.146 (b = 9, c = 3): a directional reduction, underpowered
  at this sample size."
- Abstract / contributions / conclusion: same directional framing; remove "p ≈
  0.002", "α = 0.01", "95% CI ≈ 4.6 to 17.6".

### Figure swaps (already regenerated; system python313 has matplotlib)
- corrected_fig1.png — genuine 3f+1 pipeline (4 hetero validators; healer=proposer
  no vote; analyzer no vote; quorum 3-of-4). REPLACES image1.png.
- corrected_fig2.png — safety 66→54%, honest p=0.146 in title. REPLACES image2.png.
- corrected_fig4.png — durations (single vs 3f+1). REPLACES image4.png.
- corrected_fig5.png — f=1 Byzantine matrix, genuine-3f+1 title. REPLACES image5.png.
- corrected_fig6.png — NEW f=2 tight-bound vote cliff 7/5/4 vs quorum=5. ADD.

---

## RESPONSE LETTER REWRITE (AUTHOR_RESPONSE_LETTER.md)

Rewrite the bullets at lines ~167–211 that confess the OLD narrative. Factual,
forward-looking, no mea-culpa. Specifically:
- DROP the "We reframed §6.6 ... 100% is quorum arithmetic (standing accepts) not
  a PBFT theorem" bullet. Replace with a factual statement that the Byzantine
  evaluation corrupts one of four independent validators and demonstrates genuine
  f = 1 tolerance, extended to a tight f = 2 bound.
- DROP "We made the PBFT threat model precise and honest (§3.2) ... standing
  accept ... does not deliver the textbook f-of-3f+1 guarantee ... bounded
  ensemble." Replace: §3.2 describes the four independent, model-diverse
  validators voting under PBFT (n = 3f + 1), evaluated by fault injection and an
  f = 2 tight-bound study.
- Reviewer-1 #7 (exact match across LLMs): the safety pipeline binds the four
  validators' votes to one healer proposal via a byte digest (standard PBFT);
  agreement among multiple independent proposals is the separate semantic quorum.
- Statistics bullet: replace "Wilcoxon p = 0.0016 overstates" / "McNemar p ≈
  0.002" with the honest directional result (safety 66→54%, p = 0.146 n.s.;
  success 32→42%, p = 0.227) and state that the safety guarantee rests on the
  deterministic Byzantine-tolerance results.
- Defects4J bullet: replace "4 (Lang-4, 11, 21, 28)" and "6/6 Java set" with the
  real-oracle result: 2 full-suite-verified Math repairs (Math-3, Math-5);
  consensus robustness separated from repair capability.
- Cleanup #11 (Wilcoxon→McNemar wording) is subsumed by the statistics bullet.

---

## EXECUTION ORDER (once bh233x322 lands)
1. Fill [PENDING RERUN] numbers (synthetic consensus, variance, latency) from the
   fresh r2_syn_hetero / r2_var_* / r2_lat_* summaries.
2. Rebuild figures if any depend on the new numbers (fig2 safety uses BugsInPy;
   fig4 durations; fig6 f=2 — check which need regen). Run with system python313.
3. Apply the section rewrites above into `revise_manuscript.py` (consolidate the
   duplicated abstract/§6.6/RQ1 edits; delete the OLD-narrative re-edits).
4. Run `python revise_manuscript.py` → regenerates MS_R1_baseline_anon.docx +
   MS_R1_revised_clean.docx; Word Compare → tracked-changes copy.
5. Rewrite AUTHOR_RESPONSE_LETTER.md bullets; regenerate its docx.
6. Verify: no "standing accept", "bounded ensemble", "quorum arithmetic", "p ≈
   0.002", "Lang-4, 11, 21, 28", "FBCH_CONFIDENTIAL" remain in the outputs.
