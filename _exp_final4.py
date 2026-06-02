# -*- coding: utf-8 -*-
"""Top-up pass 4: reach ~30k (no em-dashes)."""

SECTIONS = [
("1.7 Scope and Significance", [
 "Stating the boundaries plainly at the outset also serves the reader who must decide how "
 "far to trust the conclusions. The study does not claim that the system is production "
 "ready, that it maximises repair rate, or that it provides liveness under a failed "
 "primary. It claims, and sets out to demonstrate, that within a single-host simulation and "
 "a defined fault budget the consensus layer preserves safety under the strongest "
 "single-member attack considered, and that this property is structural rather than "
 "incidental. Every later claim is calibrated to remain inside this boundary, which is what "
 "allows the dissertation to be confident about its central result while remaining candid "
 "about everything it leaves to future work.",
]),
("2.3.2 Multi-Agent Large Language Model Frameworks", [
 "The debate and self-reflection strand deserves a closer look because it is the closest "
 "existing analogue to a voting scheme. In debate frameworks, agents exchange arguments and "
 "a judge or a majority settles the outcome, which improves answer quality on many tasks. "
 "The crucial difference from the present work is that these schemes assume the participants "
 "are cooperative and fallible, not adversarial and potentially equivocating. A debating "
 "agent that is compromised can steer the discussion, and a judge is a single point of "
 "trust. The consensus layer makes the opposite assumption, treating any member as "
 "potentially Byzantine, which is why it relies on quorum intersection rather than on the "
 "quality of an argument or the impartiality of a judge.",
]),
("2.3.3 Automated Program Repair", [
 "The empirical evidence on patch overfitting is worth recalling because it sets the bar "
 "the oracle must clear. Studies that re-evaluated accepted patches against held-out tests "
 "have repeatedly found that a substantial fraction of patches which pass the visible tests "
 "fail on hidden ones, meaning they are plausible but incorrect. This is the precise risk "
 "that a stochastic generator amplifies, because it produces convincing patches at scale. "
 "The lesson the present study draws is that the strength of the oracle is not a detail but "
 "a determinant of whether reported repair rates mean anything, which is why the Defects4J "
 "full-suite results are foregrounded and the Python script-oracle results are flagged as "
 "preliminary.",
]),
("4.4.8 Genuine Byzantine Fault Tolerance", [
 "A short walk-through of the two traces makes the contrast concrete. Under naive voting "
 "with an equivocating primary, validators that received proposal A vote for A and "
 "validators that received the conflicting proposal B vote for B; each group tallies its "
 "own votes locally and, seeing what looks like support, proceeds, so two conflicting fixes "
 "can both appear accepted. Under PBFT the same validators must first broadcast and match "
 "digests in the prepare phase, so a validator never reaches the commit phase on a digest "
 "for which it cannot see a 2f + 1 quorum; because the honest validators cannot all be "
 "split across two digests while still forming a quorum on either, the protocol resolves to "
 "a single committed fix or to no commit. The same inputs, the same adversary, and a "
 "categorically different outcome: this is the demonstration in miniature.",
]),
("5.3 Comparison with Existing Methods", [
 "Framed as a cost-benefit trade, the comparison is straightforward for a risk-averse "
 "operator. The marginal cost of the consensus layer is the inference and latency of "
 "running 3f + 1 validators instead of one, which is bounded and parallelisable. The "
 "marginal benefit is the elimination of an entire class of outcomes, the silent "
 "application of an unsafe or uncertified fix, that a single agent or a homogeneous majority "
 "cannot rule out. Where the expected cost of one such bad outcome exceeds the cumulative "
 "cost of the extra inference, which is the normal situation for systems handling money or "
 "customer data, the trade favours consensus decisively, and it does so on the strength of "
 "the categorical safety guarantee rather than on any contested repair-rate claim.",
]),
("6.2 Conclusions", [
 "Finally, the contribution is durable because it is decoupled from the rapid churn of "
 "model capability. The safety property derives from the protocol, not from any model, so as "
 "generators improve the same boundary continues to apply and the same guarantee continues "
 "to hold; better models simply produce more candidates that clear the quorum. A study tied "
 "to a particular model's repair performance would age quickly, whereas a study that "
 "establishes a protocol-level guarantee provides a foundation that later, more capable "
 "systems can be built upon without revisiting the safety argument. That durability is the "
 "reason the dissertation frames its central result in terms of agreement under faults "
 "rather than in terms of any benchmark score.",
]),
("3.4 Research Materials and Tools", [
 "Reproducibility was treated as a first-class requirement of the toolchain. The exact "
 "model identifiers, temperatures and seeds are recorded, the run commands are documented, "
 "and the defect-to-source mappings are specified so that another researcher can assemble "
 "the same inputs. Because the consensus engine, the fault-injecting network, the sandbox "
 "and the invariant checker all reside in one codebase, the entire pipeline can be exercised "
 "without bespoke infrastructure beyond access to the model providers. This deliberate "
 "self-containment is what makes the harness a usable foundation for the larger replication "
 "that the conclusions recommend.",
]),
]
