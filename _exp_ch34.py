# -*- coding: utf-8 -*-
"""Chapter 3 and 4 expansion prose (no em-dashes)."""

SECTIONS = [
("3.2 Research Design", [
 "The study adopts a design-science and quantitative-experimental strategy, which fits a "
 "research aim that is both to construct an artefact and to measure its behaviour. The "
 "design-science element produces the artefact, namely the Byzantine fault-tolerant "
 "consensus layer and the surrounding repair pipeline, and the experimental element "
 "subjects that artefact to controlled conditions in which independent variables, such as "
 "the adversarial behaviour of a member or the number of validators, are manipulated while "
 "dependent variables, such as the safety-violation rate and the repair rate, are observed. "
 "This combination is appropriate because neither approach alone would suffice: a pure "
 "construction would yield an artefact with no evidence of its properties, while a pure "
 "experiment would have nothing to test.",
 "Three principles govern the design. The first is controlled comparison: every "
 "consensus-mode result is paired against a single-agent baseline on the same defects, so "
 "that any difference can be attributed to the consensus layer rather than to the "
 "underlying generator. The second is adversarial evaluation: rather than only measuring "
 "behaviour on benign inputs, the design injects faults, including a primary that "
 "equivocates, so that the safety property is observed under stress. The third is "
 "reproducibility: exact models, temperatures, seeds and run commands are recorded so that "
 "an independent researcher can repeat the procedure. These principles are what allow the "
 "later chapters to make claims that are conditional on stated assumptions rather than "
 "general assertions.",
]),
("3.4 Research Materials and Tools", [
 "The implementation stack was chosen for transparency and reproducibility rather than for "
 "novelty. The orchestration layer and the consensus engine are written in Python, the "
 "validators are accessed through provider APIs spanning more than one model family, and "
 "message authentication uses Ed25519 signatures from a standard cryptography library so "
 "that forged messages can be detected on receipt. The fault-injecting network, the "
 "sandbox and the invariant checker are all part of the same codebase, which means the "
 "entire pipeline can be exercised end to end without external services beyond the model "
 "providers. This matters for the credibility of the safety claims, because it allows the "
 "adversarial scenarios to be run deterministically given a fixed seed.",
 "The choice to sign messages and to verify those signatures on receipt is not "
 "incidental. Without authentication, a Byzantine member could impersonate others and "
 "manufacture a quorum, which would void the safety argument. With authentication, a "
 "forged or tampered message is discarded before it can influence a vote, so the only "
 "power a faulty member retains is to vote badly with its own identity, which is exactly "
 "the power the 3f + 1 bound is designed to absorb. The harness records every message, "
 "vote and certificate, producing an auditable trace that underpins the per-case results "
 "reported later in this chapter.",
]),
("3.5.2 PBFT Consensus Engine", [
 "The consensus engine instantiates the safety half of PBFT over the validator population. "
 "For the default fault target f = 1 it runs n = 3f + 1 = 4 independent validators with an "
 "agreement quorum of 2f + 1 = 3, and the proposing healer and the analyzer are excluded "
 "from voting so that the voting population is genuinely independent of the proposer. A "
 "repair round proceeds through the three classical phases. In pre-prepare the healer "
 "broadcasts the candidate fix together with the byte digest of the proposal. In prepare "
 "each validator independently evaluates the candidate and broadcasts an accept or reject "
 "vote bound to that digest. In commit a validator that has gathered a prepare quorum "
 "broadcasts its commit, and only after gathering a commit quorum on the same digest does "
 "it decide to apply the fix.",
 "The engine enforces an equivocation guard so that a member cannot send conflicting "
 "votes for the same slot to different peers, and it builds explicit 2f + 1 certificates "
 "that record which validators vouched for a committed digest. If a quorum cannot form, "
 "for example because more than f members are faulty or the network is partitioned, the "
 "engine makes no progress rather than committing an uncertified fix. This deliberate "
 "preference for safety over liveness is the behaviour that the adversarial experiments in "
 "Chapter 4 are designed to confirm, and it is the property on which the project's title "
 "depends.",
]),
("3.5.4 Byzantine Fault-Injection Harness", [
 "The fault-injection harness is the instrument that turns a safety claim into a "
 "measurable quantity. It can perturb the system at two levels. At the network level it "
 "can delay, drop or partition messages, simulating the asynchrony that PBFT is designed "
 "to tolerate. At the member level it can replace an honest validator with one of several "
 "adversarial behaviours: always-reject, which refuses every fix; always-approve, which "
 "accepts every fix including unsafe ones; random, which votes arbitrarily; and garbage, "
 "which emits malformed or contradictory messages. The most demanding scenario combines "
 "these with an equivocating primary that sends different proposals to different "
 "validators, which is the classical attack that a naive vote cannot survive.",
 "By running each scenario in both a naive-voting configuration and the PBFT "
 "configuration, the harness produces a direct contrast. The naive configuration shows the "
 "failure mode that the protocol is meant to prevent, such as honest validators committing "
 "different fixes when the primary equivocates, while the PBFT configuration shows the "
 "safety property being preserved. This paired design is what allows Chapter 4 to attribute "
 "the preserved agreement to the protocol rather than to luck, and it is the basis for the "
 "scenario matrix presented there.",
]),
("3.6.2 Statistical Test", [
 "The primary statistical test is McNemar's exact test, which is the appropriate choice "
 "for paired binary outcomes on the same set of defects. Because each defect is attempted "
 "in both the single-agent baseline and the consensus mode, the natural unit of analysis "
 "is the discordant pair, that is a defect on which the two modes disagree. McNemar's test "
 "conditions on the number of discordant pairs and asks whether the split between the two "
 "directions of disagreement is more extreme than chance would produce. The exact binomial "
 "form is used rather than the chi-square approximation because the number of discordant "
 "pairs is small, and the exact form does not rely on large-sample assumptions that the "
 "data do not meet.",
 "The study is deliberately conservative in how it reports this test. On the paired "
 "real-world subset the discordant pairs split six to one in favour of the consensus mode, "
 "which yields an exact two-sided p-value of 0.125. This does not meet the conventional "
 "0.05 threshold, and the result is therefore reported as directional rather than "
 "statistically significant. Presenting the finding this way is a matter of research "
 "integrity: the direction of the effect is consistent and encouraging, the sample is too "
 "small to license a significance claim, and the honest description is that the evidence is "
 "suggestive and warrants a larger replication.",
]),
("4.4.4 Latency Profile", [
 "The latency profile quantifies the cost of the safety the consensus layer provides. "
 "Because a repair round requires a population of validators to evaluate the candidate and "
 "exchange two rounds of messages, the wall-clock time per decision is higher than that of "
 "a single agent, and it grows with the validator count as the quorum size increases. The "
 "measured means show this overhead clearly, and the study reports them as means "
 "consistently across the relevant tables and figures so that the reader can weigh the "
 "safety benefit against the time cost without having to reconcile inconsistent figures.",
 "Two qualifications accompany the latency results. First, the dominant term is the model "
 "inference time of the validators rather than the message exchange, so the overhead scales "
 "with how many independent evaluations are demanded rather than with protocol chatter; "
 "this means the cost is amenable to the obvious engineering remedy of evaluating "
 "validators in parallel. Second, the latency sweep over validator counts speaks only to "
 "timing and not to success or safety, which are established separately on the larger "
 "defect sets; the study is explicit about this division so that the small sweep is not "
 "read as evidence about repair quality.",
]),
("4.4.8 Genuine Byzantine Fault Tolerance", [
 "The equivocating-primary experiment is the centre of the safety argument, and its "
 "interpretation deserves to be stated plainly. When the primary equivocates, it sends one "
 "proposal to some validators and a conflicting proposal to others, attempting to drive the "
 "honest members toward committing different fixes for the same defect. In the naive-voting "
 "configuration this attack succeeds: honest validators, each acting on the proposal they "
 "received, reach different local decisions, and the result is a split in which conflicting "
 "fixes can both appear committed. This is exactly the inconsistency that a simple majority "
 "of independent voters cannot prevent, because the voters never reconcile what they were "
 "shown.",
 "In the PBFT configuration the same attack fails to break agreement. The prepare and "
 "commit phases force the validators to exchange and match digests before any decision, so "
 "a validator commits only on a digest for which a 2f + 1 quorum has vouched. Because any "
 "two such quorums share at least one honest member, the honest members cannot be split "
 "across conflicting digests, and the protocol either commits a single agreed fix or makes "
 "no commit at all. The experiment therefore demonstrates the safety property directly "
 "rather than inferring it: under the strongest single-member attack in the matrix, "
 "agreement is preserved, forged messages are rejected, and no uncertified fix reaches the "
 "sandbox. This is the evidence on which the project earns its title on the safety axis.",
 "It is equally important to state what this experiment does not show. It does not "
 "establish liveness under a failed primary, which classical PBFT recovers through a "
 "view-change that this implementation does not include, and it does not exercise "
 "deployment across multiple physical hosts. These are named as future work. The claim the "
 "experiment supports is bounded and precise: within a single-host simulation and a stated "
 "fault budget, the protocol preserves safety under an equivocating primary where a naive "
 "vote does not.",
]),
("4.4.9 Cross-Language Evaluation", [
 "The cross-language evaluation exists to test the pipeline against a stronger oracle than "
 "the Python experiments use. Defects4J provides real Java defects together with the host "
 "projects' own test suites, so a fix can be required to pass the full suite rather than a "
 "single reproduction script. Under this stricter standard the pipeline produced two "
 "genuine full-suite-verified repairs on the commons-math project, while on commons-lang it "
 "produced no full-suite passes, and crucially it produced zero unsafe commits across the "
 "evaluation. The headline number is therefore small, but it is trustworthy in a way that "
 "a script-oracle number is not, because every reported repair survived the project's own "
 "regression tests.",
 "The contrast between the two projects is itself instructive. commons-math defects "
 "tended to be localised numerical or logic errors that an LLM could correct without "
 "disturbing the wider codebase, whereas commons-lang defects more often required edits "
 "whose side effects tripped other tests in the full suite. Reporting both outcomes, "
 "rather than only the successes, gives an honest picture of where the approach currently "
 "reaches and where it does not, and it reinforces the study's general stance that the "
 "value of the consensus layer lies in never committing an unsafe fix rather than in "
 "maximising the raw count of fixes.",
]),
("4.5 Proposed Model", [
 "Taken together, the results support a proposed model in which autonomous repair is "
 "organised as a layered pipeline with the consensus engine as its safety governor. An "
 "analyzer localises the defect, a healer proposes one or more candidate fixes, an "
 "independent model-diverse quorum decides whether any candidate may be applied, and a "
 "sandbox with domain-invariant checks acts as the final gate before a fix touches real "
 "state. The novel element is not any single component but the insertion of a genuine "
 "Byzantine-agreement decision between proposal and application, which converts an "
 "unaccountable single-agent action into an auditable collective one with a stated fault "
 "budget.",
 "The model is deliberately generator-agnostic. Because the consensus engine judges "
 "candidates rather than producing them, it can sit above any present or future "
 "patch-generation technique, and improvements in generation translate into more "
 "candidates clearing the quorum without weakening the safety guarantee. This separation "
 "of concerns is the practical contribution the study offers to operators who wish to "
 "automate remediation: the safety boundary is fixed and auditable, while the generation "
 "behind it can evolve. The experiments validate the safety boundary directly and report "
 "the downstream repair gains as preliminary, which is the division of confidence the "
 "evidence justifies.",
]),
]
