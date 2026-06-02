# -*- coding: utf-8 -*-
"""Final expansion pass across remaining sections (no em-dashes)."""

SECTIONS = [
("1.1 Introduction", [
 "This dissertation is situated at the meeting point of three concerns that have, until "
 "now, been pursued largely in isolation: the dependability of distributed systems, the "
 "capability of large language models to reason about code, and the operational risk of "
 "modifying live commercial software. Each concern is individually well understood, yet "
 "their combination raises a question that none answers alone, namely how an autonomous "
 "system can be trusted to repair production code when the agent doing the reasoning is "
 "itself unreliable. The chapters that follow develop and test an answer built on Byzantine "
 "agreement, and this introductory chapter sets out the motivation, the problem, the "
 "objectives and the boundaries within which that answer is offered.",
]),
("1.9 Conclusion", [
 "This chapter has framed the study as an attempt to make autonomous repair safe enough to "
 "trust by importing a guarantee from distributed-systems theory. It has argued that a "
 "stochastic LLM agent is, for safety purposes, a Byzantine component, and that the 3f + 1 "
 "replication bound and 2f + 1 quorum offer a principled way to govern its output. It has "
 "stated the problem in two parts, a design gap and an evidence gap, and it has bounded the "
 "scope to the safety axis so that the claims made can be supported by the experiments "
 "reported later. The chapters that follow review the relevant literature, describe the "
 "artefact and method, present the empirical results, discuss their meaning and conclude "
 "with calibrated findings and concrete future work.",
]),
("2.1 Introduction", [
 "The purpose of this review is not to survey three fields exhaustively but to read them "
 "against one another in search of the specific intersection this study occupies. The "
 "review is therefore organised around a thesis, that genuine Byzantine agreement has not "
 "been applied to agentic repair, and it marshals the literature to establish both that the "
 "ingredients exist and that no one has yet combined them in the way proposed here. Each "
 "subsection examines one literature against the requirements that a contribution at the "
 "intersection would have to satisfy, and the chapter closes by naming five concrete gaps "
 "that the empirical work targets.",
]),
("2.4 Inclusion and Exclusion Criteria", [
 "The criteria that governed which sources were drawn upon were chosen to keep the review "
 "focused on the intersection rather than on any single field in full. Sources were "
 "included when they bore directly on Byzantine agreement and quorum design, on multi-agent "
 "or ensemble aggregation of model outputs, on automated program repair and its oracle "
 "problem, or on the integrity constraints peculiar to e-commerce systems. Foundational "
 "works were retained regardless of age because the replication bounds and the safety "
 "arguments they establish remain the reference points that current systems design to, "
 "while application papers were favoured when recent so that the account of model "
 "capability reflects the present state of the art.",
 "Sources were excluded when they addressed only one field without implication for the "
 "intersection, for example pure throughput optimisations of consensus protocols that do "
 "not bear on safety under adversarial members, or benchmark-leaderboard papers that report "
 "task success without any safety contract. This filtering is what allows the synthesis to "
 "be sharp: by setting aside material that does not speak to safety under faults, the "
 "review can state precisely what is missing and thereby justify the experiments that "
 "follow.",
]),
("2.5 Conclusion", [
 "The review has shown that each contributing field is mature but that their intersection "
 "is largely unoccupied. Byzantine fault tolerance offers a proven safety property but has "
 "not been applied to LLM agents; multi-agent frameworks offer practical machinery but "
 "aggregate opinions in ways that do not survive an adversarial member; automated repair "
 "offers the task and the metrics but is hampered by weak oracles and by the fluency with "
 "which modern models produce plausible but wrong patches. The five gaps named in the "
 "synthesis define the remit of the empirical chapters, and the methodology described next "
 "is designed so that each experiment provides evidence for or against the closing of a "
 "specific gap.",
]),
("3.1 Introduction", [
 "This chapter describes how the study was conducted in enough detail that an independent "
 "researcher could reproduce it. It states the research design and its justification, "
 "describes the three defect sets and the tools used, specifies the system architecture "
 "component by component, defines the metrics and the statistical test, and sets out the "
 "experimental procedure and the ethical considerations. The level of detail is deliberate, "
 "because the credibility of the safety claims rests on the experiments being repeatable "
 "and the adversarial scenarios being deterministic given a fixed seed.",
]),
("3.3.1 Synthetic Micro-Benchmark", [
 "The synthetic micro-benchmark was constructed to exercise known fault categories under "
 "controlled conditions, so that the pipeline's behaviour on each category could be "
 "observed without the confounds of real-world code. Each case pairs a seeded defect with "
 "a reproduction that fails before repair and is expected to pass after a correct fix, "
 "which gives a clean signal for the controlled comparison against the single-agent "
 "baseline. Because the defects are seeded, the benchmark also serves as a sanity check on "
 "the harness itself, confirming that the consensus and baseline modes behave as designed "
 "before they are exposed to harder, less predictable defects.",
]),
("3.3.2 BugsInPy Real-World Subset", [
 "The BugsInPy subset brings real defects from real Python projects into the evaluation, "
 "which is essential because synthetic faults can flatter a repair system by being more "
 "regular than nature. The subset was drawn to span more than one host project so that the "
 "results are not an artefact of a single codebase's style, and each defect is attempted "
 "in both modes to preserve the paired design on which the McNemar analysis depends. The "
 "honest caveat attached to this set is the oracle: success is judged by a run-as-script "
 "reproduction rather than the full project suite, so the repair outcomes on this subset "
 "are reported as preliminary and are complemented by the stronger Defects4J evaluation.",
]),
("3.3.3 E-Commerce Micro-Benchmark", [
 "The e-commerce micro-benchmark was designed to test whether domain invariants add "
 "protection beyond the generic repair check. Its cases embed the financial and inventory "
 "constraints that a commercial system must never violate, such as non-negative inventory "
 "and consistent order totals, so that a fix which restores a failing test while corrupting "
 "business state can be detected. As reported later, the invariant gate showed no "
 "measurable effect on the headline outcomes, a negative result that locates the invariant "
 "check as a defence-in-depth backstop rather than as the primary safety mechanism, and "
 "this benchmark is what makes that conclusion empirical rather than speculative.",
]),
("3.5.1 Agents", [
 "The agent roles are kept deliberately separate so that responsibility for proposing a "
 "fix is distinct from responsibility for approving it. The analyzer localises the defect "
 "and assembles the context, the healer proposes one or more candidate fixes, and the "
 "validators judge those candidates. Critically, neither the healer nor the analyzer votes "
 "in the quorum, which keeps the voting population independent of the proposer and prevents "
 "a proposer from approving its own work. This separation is what allows the Byzantine "
 "analysis to apply, because the votes that form a quorum come from members with no stake "
 "in the proposal.",
]),
("3.5.3 Isolated Sandbox and Domain Invariants", [
 "The sandbox is the final gate before a fix touches real state, and it serves two "
 "purposes. First, it executes the candidate in isolation so that a fix which passes the "
 "quorum can still be observed to behave correctly before it is applied, which guards "
 "against the residual risk that a quorum of validators is collectively mistaken. Second, "
 "it enforces the domain invariants, rejecting any fix whose execution would violate a "
 "business constraint even if the fix otherwise restores the failing test. The sandbox thus "
 "converts the consensus decision into an action only when both the quorum and the "
 "execution-time checks are satisfied, which is the layered safety posture the proposed "
 "model depends on.",
]),
("3.6.1 Metrics", [
 "The metrics are chosen to separate safety from repair so that the two contributions can "
 "be reported with the confidence each deserves. Safety is captured by the safety-violation "
 "rate and, in the adversarial experiments, by whether agreement is preserved and whether "
 "any uncertified or unsafe fix is committed. Repair is captured by the repair rate on the "
 "paired defect sets. Latency is reported as a mean per decision so that the cost of the "
 "consensus layer is visible alongside its benefit. Keeping these metrics distinct is what "
 "prevents a strong safety result from being conflated with a preliminary repair result, a "
 "distinction the discussion chapter relies on.",
]),
("3.6.3 Experimental Procedure", [
 "The procedure runs each defect through both the single-agent baseline and the consensus "
 "mode under fixed models, temperatures and seeds, recording every message, vote and "
 "certificate so that outcomes can be audited after the fact. The adversarial matrix is run "
 "separately, replacing honest validators with the injected behaviours and, in the most "
 "demanding scenario, an equivocating primary, and each scenario is executed in both the "
 "naive-voting and PBFT configurations so that the contrast attributes any preserved "
 "agreement to the protocol. Because the seeds are fixed, the adversarial results are "
 "deterministic and therefore reproducible, which is the property that lets the safety "
 "findings be stated as demonstrations rather than as observations that might not recur.",
]),
("3.7 Ethical Considerations", [
 "The ethical considerations centre on the risk that an autonomous repair system, if "
 "trusted incorrectly, could damage real commercial systems and the customers who depend "
 "on them. The study addresses this directly by never allowing a fix to reach real state "
 "without clearing both the quorum and the sandbox, and by designing the protocol to fail "
 "safely, making no commit when agreement cannot be reached, rather than acting under "
 "uncertainty. The evaluation itself was conducted entirely on benchmark defects and "
 "isolated sandboxes, so no production system was placed at risk, and the honest reporting "
 "of negative and preliminary results is itself an ethical commitment, since overstating "
 "the system's reliability would encourage exactly the unsafe trust the work seeks to "
 "prevent.",
]),
("3.8 Chapter Summary", [
 "In summary, the methodology pairs a constructed artefact with a controlled experimental "
 "evaluation, compares consensus against a single-agent baseline on three defect sets, and "
 "subjects the protocol to an adversarial matrix culminating in an equivocating primary. "
 "The architecture separates proposal from approval, authenticates every message, and gates "
 "every action behind both a quorum and a sandbox. The metrics separate safety from repair, "
 "the statistical test is chosen for paired binary outcomes, and the whole procedure is "
 "made reproducible through fixed models and seeds. The chapter that follows reports what "
 "this method found.",
]),
("4.1 Introduction", [
 "This chapter presents the empirical results in the order in which they build the "
 "argument, beginning with the paired repair-and-safety outcomes, proceeding through the "
 "decorrelation, latency and adversarial findings, and culminating in the equivocating-"
 "primary demonstration and the cross-language evaluation. The per-case results are "
 "included so that the aggregate figures can be traced to individual defects. Throughout, "
 "the firm safety findings and the preliminary repair findings are kept distinct, so that "
 "the reader can see exactly which claims rest on demonstration and which rest on a modest "
 "and not-yet-significant sample.",
]),
("4.2 Insights from the Data", [
 "Two insights emerge before any formal test is applied. The first is that the consensus "
 "mode never produced an unsafe commit in any configuration, including the adversarial "
 "ones, which is the qualitative signal that the safety mechanism is doing its job. The "
 "second is that the benefit of consensus is most visible on the harder real-world defects "
 "and least visible on the easy synthetic ones, where the single agent already succeeds, "
 "which is consistent with the intuition that independent agreement matters most when the "
 "task is genuinely difficult and a single model is most likely to be confidently wrong.",
]),
("4.3 Exploratory Data Analysis", [
 "Exploratory analysis of the per-case traces supports the headline figures and explains "
 "their shape. Where the consensus mode improved on the baseline, the improvement typically "
 "came from the quorum rejecting a plausible but wrong fix that the single agent would have "
 "applied, rather than from the quorum discovering a fix the single agent missed. This is an "
 "important nuance: the consensus layer's contribution is more about preventing bad actions "
 "than about generating better candidates, which aligns with its role as a safety governor "
 "rather than a generator and with the proposed model in which generation and approval are "
 "separated.",
]),
("4.4.1 Paired Safety-Violation Outcomes", [
 "The paired safety-violation outcomes are the clearest repair-side signal in the study. "
 "Because each defect is attempted in both modes, the comparison controls for defect "
 "difficulty, and the reduction in safety violations under consensus can be attributed to "
 "the quorum screening out unsafe candidates rather than to an easier set of defects. The "
 "outcomes feed directly into the McNemar analysis that follows, where the discordant pairs "
 "are the unit of inference, and they should be read together with the explicit statement "
 "that the resulting effect, while consistent in direction, does not reach significance on "
 "this sample.",
]),
("4.4.3 Failure Decorrelation", [
 "The decorrelation result is reported as a negative finding because honesty about it "
 "strengthens the wider argument. Model diversity reduced correlated error, with agreement "
 "among validators falling from near-total on the easy synthetic cases to a lower level on "
 "the harder real-world subset, but it did not make the validators independent. This means "
 "the quorum's protection is real but bounded: when a defect triggers a blind spot shared "
 "across model families, diversity alone will not save the vote. The practical implication "
 "is that increasing provider diversity is worthwhile but is not a substitute for the "
 "protocol's structural guarantees, which hold regardless of how correlated the honest "
 "votes happen to be.",
]),
("4.4.5 Byzantine Fault Tolerance Under Five Adversarial", [
 "The five-behaviour matrix shows the quorum absorbing faulty votes up to the replication "
 "bound. Against always-reject, always-approve, random and garbage members, the protocol "
 "continued to commit only certified fixes and never committed an unsafe one, because no "
 "single faulty member can manufacture a 2f + 1 quorum on its own. The always-approve case "
 "is the most instructive, since a member that accepts every fix, including unsafe ones, is "
 "exactly the kind of compromised reviewer that a naive scheme would trust; here the "
 "quorum requirement means its lone approval cannot carry a fix, and an unsafe candidate is "
 "rejected unless an honest majority is also fooled. This is the masking behaviour that the "
 "f = 2 tight-bound experiment then probes at its limit.",
]),
("4.4.6 Diverse-Validator Replication", [
 "The diverse-validator replication confirms that the protocol operates as intended when "
 "the validators are genuinely drawn from different model families rather than from one "
 "base model. This matters because the safety argument assumes the honest votes are "
 "independent enough that a faulty member cannot rely on the others sharing its error. The "
 "replication shows the quorum forming correctly across heterogeneous validators and the "
 "certificates recording which models vouched for each committed fix, which is the auditable "
 "evidence an operator would need to trust a committed decision after the fact.",
]),
("4.4.7 Validator-Count Variation", [
 "Varying the validator count demonstrates the replication bound in action. At n = 4 the "
 "system tolerates one faulty member, and at n = 7 it tolerates two, with the quorum size "
 "scaling as 2f + 1 in each case. The experiment confirms both halves of the guarantee: "
 "within the fault budget the quorum masks the faulty votes, and beyond it the protocol "
 "fails safely by making no commit rather than committing an uncertified fix. This is the "
 "behaviour that distinguishes a genuine Byzantine-agreement protocol from a voting "
 "heuristic, and it is the property the f = 2 configuration was added to verify.",
]),
("4.6 Conclusion", [
 "The results chapter has established the study's firm contribution, the preservation of "
 "safety under adversarial members and an equivocating primary, and has reported its "
 "preliminary contribution, the directional improvement in repair and safety-violation "
 "rates, with the honesty the sample size demands. It has also reported the informative "
 "negative results on decorrelation and domain invariants. Together these findings support "
 "the proposed model of a generator-agnostic consensus layer as a safety governor, which "
 "the next chapter discusses in relation to existing methods and the study's own "
 "limitations.",
]),
("6.1 Introduction", [
 "This final chapter draws the study to a close by stating its conclusions in proportion "
 "to the evidence, offering recommendations for practice and for future research, and "
 "reflecting on the broader idea the work contributes. The conclusions distinguish the firm "
 "safety result from the preliminary repair result, the recommendations translate the "
 "findings into actionable guidance, and the reflection identifies the durable "
 "methodological contribution that future work can build upon.",
]),
("6.3.1 Recommendations for Practice", [
 "For practitioners considering autonomous remediation, the central recommendation is to "
 "treat the safety boundary as fixed and auditable and the generator as replaceable. An "
 "operator should require that no fix reaches production without clearing an independent, "
 "model-diverse quorum and a sandbox that enforces domain invariants, and should accept the "
 "additional inference latency as the price of a guarantee that a single agent cannot "
 "provide. The consensus layer should be configured with a fault budget appropriate to the "
 "deployment, recognising that the protocol fails safely beyond that budget, and the "
 "audit trail of messages, votes and certificates should be retained so that any committed "
 "decision can be reconstructed and justified after the fact.",
]),
]
