# -*- coding: utf-8 -*-
"""Top-up pass 3: distinct content to reach ~30k (no em-dashes)."""

SECTIONS = [
("1.5 Objectives", [
 "Each objective is tied to a specific part of the empirical work so that the study can be "
 "judged against concrete evidence rather than against general aspirations. The objective of "
 "designing a genuine Byzantine-agreement consensus layer is realised in the architecture of "
 "Chapter 3 and tested by the equivocating-primary experiment of Chapter 4. The objective of "
 "demonstrating safety under adversarial members is realised by the fault-injection matrix "
 "and the validator-count variation. The objective of evaluating downstream repair is "
 "realised by the paired comparisons on the three defect sets and the cross-language "
 "Defects4J evaluation. Stating the objectives in this mapped form makes the rest of the "
 "dissertation accountable to them, because every objective points to an experiment whose "
 "result either supports it or qualifies it.",
]),
("1.6 Research Questions", [
 "The research questions follow from the objectives and are framed so that each admits an "
 "empirical answer. The first asks whether a genuine 3f + 1 protocol can preserve agreement "
 "under an adversarial or equivocating member where a naive vote cannot, which the "
 "adversarial experiments answer directly. The second asks what the consensus layer costs in "
 "latency relative to a single agent, which the latency profile answers. The third asks "
 "whether the layer improves downstream repair and safety-violation rates, which the paired "
 "comparisons answer in a directional but preliminary way. Posing the questions so that each "
 "is settled by a named measurement is what keeps the study disciplined and prevents the "
 "conclusions from drifting beyond the evidence.",
]),
("1.8 Definition of Key Terms", [
 "Several terms recur throughout the dissertation and are defined here precisely to avoid "
 "ambiguity. A quorum is the smallest set of validators whose agreement is required to commit "
 "a decision, fixed at 2f + 1 in this study. Equivocation is the act, by a faulty primary, of "
 "sending conflicting proposals to different validators in order to split their decisions. A "
 "certificate is the recorded set of 2f + 1 matching votes that justifies a committed fix and "
 "makes the decision auditable after the fact. The view-change is the PBFT sub-protocol that "
 "restores progress when a primary fails, which this study identifies as future work rather "
 "than implementing. An oracle, in the repair context, is the mechanism that decides whether a "
 "candidate fix is correct, ranging from a single reproduction script to a project's full test "
 "suite. Fixing these meanings now allows later chapters to use the terms without "
 "re-explaining them.",
]),
("2.2 Conceptual Framework", [
 "Two theoretical lenses inform the framework and are worth naming. The first is the "
 "principal-agent lens: the operator is a principal who delegates repair to agents whose "
 "interests and reliability cannot be fully observed, and the consensus layer functions as a "
 "governance mechanism that constrains what the agents can do on the principal's behalf. The "
 "second is the defence-in-depth lens from security engineering: safety is achieved not by a "
 "single perfect check but by layering independent controls, here the quorum, the sandbox and "
 "the domain invariants, so that a failure in one is caught by another. Reading the artefact "
 "through these lenses clarifies why the design separates proposal from approval and why it "
 "gates every action behind multiple independent controls rather than trusting any single "
 "one.",
]),
("3.2 Research Design", [
 "The design also anticipates the threats to validity that the discussion later examines, and "
 "mitigates them by construction where possible. The paired comparison is chosen specifically "
 "to neutralise defect-difficulty as a confound, the fixed models and seeds are chosen to make "
 "the adversarial results deterministic and therefore repeatable, and the addition of a "
 "full-suite oracle alongside the script oracle is chosen to bound the construct-validity "
 "weakness of the weaker measure. Designing these mitigations in from the start, rather than "
 "discovering the need for them after the fact, is what allows the later validity discussion to "
 "claim that the study is strong where its central safety claim lies.",
]),
("3.5 Data-Modelling Methodology", [
 "The architecture can be read as a single data flow. A defect enters the pipeline as a "
 "failing case; the analyzer transforms it into a localised context; the healer transforms "
 "that context into one or more candidate fixes; the consensus engine transforms the "
 "candidates and the validators' votes into either a certified decision or a refusal; and the "
 "sandbox transforms a certified decision into an applied action only if execution and the "
 "domain invariants permit. Viewing the system as this chain of transformations makes the "
 "role of each component explicit and shows where the safety controls sit, namely at the two "
 "transformations that can change real state, the consensus decision and the sandboxed "
 "application.",
]),
("4.4.10 Full Per-Case Experimental Results", [
 "The per-case tables that follow are included so that the aggregate figures in the preceding "
 "sections can be traced to individual defects, which is the level of detail a replication "
 "would need. Each table reports, for one defect set and mode, the outcome of every case, so "
 "that a reader can see not only how many defects were repaired or how many safety violations "
 "occurred but exactly which defects drove those totals. The Byzantine fault-injection tables "
 "similarly record the outcome of each adversarial scenario, allowing the claim that no unsafe "
 "fix was committed to be checked case by case rather than taken on trust. Reading these "
 "tables alongside the aggregate results is what turns the headline numbers into auditable "
 "evidence.",
]),
("4.3 Exploratory Data Analysis", [
 "The distribution of outcomes across the defect sets is itself revealing. On the synthetic "
 "set the outcomes cluster at the easy end, where both modes succeed, which is why that set "
 "contributes little to the paired comparison; its value is as a correctness check on the "
 "harness. On the real-world subset the outcomes spread out, producing the discordant pairs on "
 "which the statistical analysis depends, which confirms that the harder set is where the "
 "consensus layer's contribution becomes measurable. This spread is the reason the study draws "
 "its inferential weight from the real-world subset rather than from the synthetic cases.",
]),
("5.2 Interpretation of Results", [
 "Read for practical implication, the results suggest a clear deployment posture rather than a "
 "finished product. An operator could adopt the consensus layer today as a safety governor, "
 "configured to a conservative fault budget, and gain an auditable guarantee that no "
 "uncertified or unsafe fix is applied, while treating the repair-rate improvement as an "
 "expected but not yet quantified benefit. The interpretation that the evidence supports is "
 "therefore not that the system is ready to maximise autonomous repair, but that it is ready "
 "to make autonomous repair safe, which is a narrower and more defensible position and "
 "precisely the one the title stakes out.",
]),
("3.6.3 Experimental Procedure", [
 "Determinism is a deliberate feature of the procedure rather than an incidental property. By "
 "fixing the seeds that govern the network's drop, delay and partition behaviour, the same "
 "adversarial scenario produces the same trace on every run, which means a safety result can "
 "be reproduced exactly by an independent party rather than merely observed once. The complete "
 "trace of messages, votes and certificates is retained for each run, so that any reported "
 "outcome can be reconstructed and audited. This combination of determinism and full logging "
 "is what allows the safety findings to be presented as demonstrations that will recur rather "
 "than as observations that happened to occur.",
]),
]
