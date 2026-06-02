# Response to Reviewers — Manuscript SO-26-5308 (R1)

We thank the editor and both reviewers for a careful and constructive reading. The
revision makes four substantive additions in direct response: (1) we implement and
empirically evaluate a semantic-equivalence quorum, so the central claim is now
demonstrated rather than deferred; (2) we add a cross-language evaluation on Java,
including the real Defects4J harness with its actual JUnit test oracle; (3) we demonstrate
the Byzantine fault tolerance of the consensus layer directly — independent replicas
exchanging signed messages over an asynchronous, partitionable network preserve agreement
under a malicious, equivocating primary where naive voting splits (Section 6.14) — together
with run-to-run variance and latency analyses; and (4) we add a full reproduction protocol
with exact models, seeds, prompts
and a Docker definition. Point-by-point responses follow; section and table numbers refer
to the revised manuscript. All changes are visible in the tracked-changes copy.

---

## Editor's requirements

**Ethics and informed-consent statements.** Added to the title page: an Ethics statement
and a separate Informed-consent statement. The study uses only publicly available
open-source defects and author-constructed code; it involves no human or animal subjects,
so approval and consent were not required, consistent with APA Section 8.05. The title
page now also carries author contributions and ORCID fields.

**Footnotes.** The manuscript contains no footnotes; nothing needed to be moved into the
body.

**Anonymisation.** The main document is anonymised: author names, affiliation, e-mail
addresses, repository usernames and the named institution have been removed or replaced
with neutral text. Author-identifying details remain only on the separate title page.

**Language editing.** The manuscript was edited for grammar and clarity (Grammarly plus a
manual pass).

---

## Reviewer 1

**1. The semantic-equivalence quorum was claimed but deferred; experiments used exact
match, so Gap 2 was unproven.** We agree this was the core weakness and have resolved it.
We implemented a behavioural semantic-equivalence quorum (Section 5.10) and evaluated it
head-to-head against the exact-match rule across heterogeneous proposers (Section 6.9,
Table 9). Across 70 bugs the exact rule reached quorum on 2.5–10% of cases, while the
semantic rule reached quorum on 70–77% and agreed on a passing fix in 60%. The claim is
now demonstrated, and we have rewritten the abstract, introduction, Section 2.2, Section
2.4 and Section 8.1 so the text matches what the prototype does.

**2 and 8. Validation was Python-only; include Defects4J (Java) or narrow the scope.** We
added a cross-language evaluation (Section 6.10) and ran the **real Defects4J benchmark**
through its own checkout/compile/test harness in Docker, against the projects' **actual
JUnit suites** rather than a proxy oracle. The healer produces a minimal search-and-replace
edit (not a whole-file rewrite) and is shown the failing test; every candidate is verified
against the project's full relevant test suite, so a repair counts only if the suite passes.
On commons-math the pipeline produced **two genuine, full-suite-verified repairs (Math-3,
unanimous 4-of-4; Math-5, 3-of-4 with one validator dissenting on a fix that nevertheless
passed the real suite)**, with consensus reached on all 9 evaluated bugs. On commons-lang
the four independent validators reached consensus on 8 of 9 evaluated bugs, but none passed
the full Lang suite — a concrete, honest measure of how hard real-world Java repair is, and
in every case the executable suite prevented an unverified fix from being reported as a
repair (Table 10). The real oracle cleanly separates two questions the synthetic and
snippet-level studies cannot: *consensus robustness*, which the Byzantine fault-injection
matrix proves, and *repair capability*, which on hard real Java bugs is modest and which we
report honestly. We are also explicit about reproducibility: the healer is non-deterministic,
so the specific set of repaired bugs varies between runs even with a pinned seed; what is
invariant is safety (no fix is reported as a repair unless the real suite passes). We
therefore report repair counts as single-run, seeded figures and release the seeds.

**3. Latency scaling with n and during fault recovery.** Added in Section 6.12 and Table
11. Median latency rises with the agent count (53.3 s at n = 4, 71.3 s at n = 7, 80.1 s at
n = 10) and the 99th percentile grows faster (59.6 s, 78.0 s, 168.6 s) as the round waits
for the slowest of the added validators, while safety and success are unchanged. The PBFT
protocol itself adds under 2 ms per round; the growth is validator inference, not
consensus. Under the five Byzantine scenarios consensus still formed every round from the
honest validators (Section 6.6), so fault behaviour did not inflate decision latency;
continuous-fault recovery timing remains future work (Section 8.2).

**4. Engage the explainable-AI smart-contract re-entrancy work.** Added to Section 2.3: we
connect the plausibility-correctness gap to the case for explainable, executable
verification in adjacent code-security settings and cite the suggested work (Maturi et al.,
2025), with full bibliographic details now in the reference list.

**5. Diverse LLMs produce different code, which contradicts an exact-match quorum.** This
is exactly the effect we now measure. Section 6.9 shows mean pairwise text agreement of
only 0.18–0.20 across heterogeneous proposers, which is why the exact rule almost never
forms a quorum and why the semantic rule is necessary. The decorrelation also appears in
the safety pipeline itself: the four cross-provider validators agree in near-lockstep on
easy bugs (~1.00) but fall to 0.925 on the real BugsInPy bugs, with three genuine split
votes (Section 7.2). The mechanism is no longer ambiguous.

**6. The abstract overstates "adapting PBFT".** The abstract is rewritten. It now states
the system precisely: a Claude analyzer and a GPT-4o healer propose a fix that is voted on
by four independent, model-diverse validators under PBFT (n = 3f + 1 = 4, quorum = 3), with
a sandbox as the final gate; it reports the genuine fault-tolerance results (f = 1 across
all five behaviours, f = 2 tight bound) and the separately evaluated semantic-equivalence
quorum without overclaiming.

**7. Clarify how consensus was reached using exact match across different LLMs.** Clarified
in Section 3.2: in the safety pipeline a single healer proposal is put to the four
independent validators, and a byte digest binds their votes to that one proposal (standard
PBFT), so "exact match" there refers to *proposal binding*, not to agreement among
different fixes. Agreement among multiple independent proposals is the separate
semantic-quorum study (Sections 5.10, 6.9).

---

## Reviewer 2

**1. Abstract restructure.** Rewritten to the suggested arc: problem, aim, method,
findings, meaning, and next steps.

**2. Introduction.** Adds a concrete e-commerce failure hook, separates the practical from
the scientific problem, refers to Table 1 rather than listing all five gaps in prose, and
states the aim and the four research questions explicitly. We also note that RQ1/RQ2 are
answered on a limited n-sweep.

**3. Repeatability and reliability.** Added a reproduction section (Section 5.9) with exact
model strings — analyzer claude-sonnet-4-5-20250929 (temperature 0.3, no vote), healer/
proposer gpt-4o (0.7, no vote), and the four independent validators (Claude-Haiku and
GPT-4o-mini in the cloud, llama3.1:8b and mistral:7b served locally by Ollama, all at 0.1)
— with token budgets, timeouts and seed handling (we pin seeds for OpenAI and Ollama;
Anthropic exposes none). The Docker sandbox image and limits are specified. A supplementary
file gives the full command sequence, the verbatim agent prompts, and a BugsInPy case-to-
project mapping. On single-run-per-bug: we add a variance study repeating a ten-bug subset
three times (Section 6.11). The consensus pipeline was identical across all three runs
(success 1.000, zero safety violations); only the single-agent baseline's raw success moved
(1.00, 1.00, 0.90), so the outcomes the safety claim rests on do not vary run to run. Test
adequacy: the synthetic and e-commerce canonical fixes were each verified by hand against
the bundled assertion suite.

**4. Discussion depth.** Section 7.1 now connects the result to ensemble learning
(Dietterich, 2000), self-consistency (Wang et al., 2023) and debate (Du et al., 2024), and
to overfitting in repair (Smith et al., 2015), while making clear that BFT-MAS adds what
those lack: a genuine PBFT quorum over independent validators that bounds how many
confidently wrong agents the system absorbs (tolerating f of 3f + 1). Section 7.2 expands
the decorrelation result with three readings (difficulty ceiling, model convergence,
prompt-induced correlation) and links it to the new quorum and split-vote data. A new
Section 7.5 frames the economic and societal implications for managers and for public
trust.

**5. Conclusion and release.** The conclusion now restates the scientific problem, the
aim, and how the results resolve it, and lists the concrete advances. Prompts, raw CSVs,
the BugsInPy mapping and the sandbox/Docker definition are released; an anonymised archive
is available to reviewers and a public DOI will be added on acceptance.

**6. Minor issues.** We checked the manuscript: the "BugsInPy" and "llama3.1" spellings are
correct throughout this version and Table 1 contains no stray markup (the artefacts the
reviewer saw were in the submitted PDF rendering). All in-text citations were checked
against the reference list, and Dietterich (2000) and Wang et al. (2023) were added. All
figures are present in the source; we will verify the PDF export preserves them.

---

## Additional changes (not specifically requested)

- **Byzantine fault tolerance, demonstrated directly (Section 6.14).** We were careful not
  to overclaim here. The fault-injection matrix (Section 6.6) and the f = 2 study (Section
  6.13) corrupt how a validator *votes*, which a majority quorum masks — useful, but not by
  itself the defining Byzantine property. To demonstrate that property we built an
  independent-replica realisation of the protocol: four replicas exchanging Ed25519-signed
  pre-prepare/prepare/commit messages over an asynchronous, partitionable network, and we
  pit it against a naive proposal-trust scheme. Under a **malicious primary that equivocates**
  (proposing fix X to some replicas and fix Y to others), the naive scheme splits — honest
  replicas commit different fixes (a safety violation) — while the protocol's 2f + 1 quorum
  certificates keep every honest replica in agreement (no split-brain). Forged messages are
  rejected (a replica cannot impersonate another, so one Byzantine node cannot manufacture a
  quorum), f = 1 crash is tolerated while f + 1 is not, and a partition blocks progress
  without ever causing a split, recovering on heal (Section 6.14, Table 13, Figure 7). The
  simulation is deterministic and uses no model calls. We are explicit that liveness under
  primary failure (view-change) and a multi-host deployment are implemented or designed but
  not yet evaluated (Section 8), and that the quality of the LLM repairs the protocol agrees
  on is a separate, preliminary question.
- **Statistics.** For the binary safety outcome we use McNemar's exact test as the primary
  test. All discordant pairs fall in the 20-bug BugsInPy subset, where the safety-violation
  rate fell from 75% to 50% (discordant pairs b = 6, c = 1; McNemar exact p = 0.125) and the
  repair rate rose from 25% to 50% (discordant 6 to 1; p = 0.125); both are directional and
  do not reach significance at this sample size, which we state plainly (across all 90 paired
  bugs the violation rate is 16.7% for the baseline against 11.1% for consensus). Accordingly
  we rest the paper's central reliability claim on the deterministic Byzantine-tolerance
  results above, which are provable rather than sampled, and report the paired repair and
  safety comparisons as directional. We also note the clustering of the real-world pairs (all
  discordant pairs in BugsInPy, concentrated in a few projects), so the effective sample is
  smaller than the raw count (Section 7.3).
- **Repair capability, reported honestly.** On the 20-bug BugsInPy subset the four
  independent validators admit more genuine fixes than the single agent (10 of 20 against
  5 of 20), not fewer; because the BugsInPy oracle is a weak run-as-script check (Section
  5.2), consensus also approves fixes the sandbox then rejects, but every such fix is caught
  before it could be reported as a repair. We make this construct-validity limitation
  explicit and tie the headline numbers to it.
- **Cross-language evaluation with a real oracle.** As noted under Reviewer 1, the Defects4J
  runs use the projects' real JUnit suites; the two verified commons-math repairs (Math-3,
  Math-5) and the modest commons-lang outcome are reported with no unverified fix counted as
  a repair.
- **Reproducibility configuration, threat model and scope (Section 3.2).** A new
  "Threat model and scope" paragraph states that the four validators run as asynchronous
  tasks in one trusted process, that the adversary modelled is a Byzantine validator
  injected by a wrapper, and that the per-message signatures protect integrity by
  construction. Within this model the consensus is genuine 3f + 1 Byzantine fault tolerance
  evaluated in a single-process simulation; what remains future work is the *distributed*
  setting — real inter-host messaging, network partitions and view-change under primary
  failure (Section 8.5).
- **Internal-consistency reconciliation.** Table 2's BFT-MAS row now reads Byzantine
  Consensus "Yes (simulated)", Cross-Language "Partial (Java sample)", Production Ready "No
  (research prototype)", and Knowledge Graph / Learning Capability "Implemented, not
  evaluated"; the metrics contribution lists six measured metrics plus pairwise agreement
  (recovery time deferred); §5.6 metric 7 is relabelled "ground-truth accuracy" to match
  Table 4; the §7.5 economic figures use a single "per 100 repairs" base; and the duplicated
  Acknowledgements / Declarations were removed from the main document (they remain on the
  Title Page).
- **Decorrelation.** We report mean pairwise validator agreement as a first-class result
  (Section 7.2): ~1.00 on easy synthetic bugs, 0.925 on the real BugsInPy bugs (with three
  genuine split votes), and 0.54 among heterogeneous proposers in the semantic-quorum study,
  directly addressing the agent-diversity gap.
- **The BugsInPy oracle is made explicit (§5.2).** The projects' own test suites are not
  run; the diff-extracted candidate is executed in the sandbox (a clean exit counts as a
  pass) and compared to the canonical fixed hunk. §7.3 flags this snippet-level oracle as
  the main construct-validity threat and notes the headline repair numbers rest on it.
- **References.** Added CISQ (2022), CodeBERT (Feng et al., 2020), AutoCodeRover (Zhang et
  al., 2024), Dietterich (2000), Wang et al. (2023) and Maturi et al. (2025); the Table 2
  "GitHub Copilot" row now cites Codex (Chen et al., 2021); the Blanchard et al. entry is
  corrected to 2017; and the reference list is now fully alphabetical with DOIs backfilled.
- **Figures.** Figure 1 is redrawn to the genuine pipeline (Claude analyzer and GPT-4o
  proposer, neither voting; four independent validators voting under a 3-of-4 quorum);
  Figures 2, 4 and 5 are regenerated with the genuine-3f + 1 framing and honest statistics;
  Figure 6 (the f = 2 vote cliff) is new.
