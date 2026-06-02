# -*- coding: utf-8 -*-
"""Chapter 5 and 6 expansion prose (no em-dashes)."""

SECTIONS = [
("5.1 Presentation of Experimental Results", [
 "Before interpreting the results it is useful to restate what was measured and on which "
 "data, so that the discussion that follows is anchored to the evidence rather than to "
 "expectation. Three defect sets were used: a synthetic micro-benchmark designed to "
 "exercise known fault categories, a real-world subset drawn from BugsInPy, and an "
 "e-commerce micro-benchmark carrying domain invariants. The consensus mode was compared "
 "against a single-agent baseline on the same defects, and a separate adversarial matrix "
 "exercised the protocol under injected member faults and an equivocating primary. The "
 "safety results come from the adversarial matrix and the equivocation experiment, while "
 "the repair-rate results come from the paired defect sets.",
 "Keeping these sources distinct matters for honest interpretation. The safety findings "
 "are demonstrations of a property under controlled fault injection, and they are "
 "deterministic given the seed, so they support strong statements. The repair-rate "
 "findings are statistical outcomes on modest samples, so they support only directional "
 "statements. The discussion below respects this asymmetry, treating the safety results as "
 "the firm contribution and the repair-rate results as encouraging but preliminary "
 "evidence that motivates a larger study.",
]),
("5.2 Interpretation of Results", [
 "The central interpretation is that the consensus layer delivers what it was designed to "
 "deliver, which is safety under adversarial members, and that it does so by construction "
 "rather than by accident. The equivocating-primary result is the clearest evidence: where "
 "a naive vote splits the honest validators across conflicting fixes, the PBFT "
 "configuration preserves agreement because quorum intersection forces the honest members "
 "onto a single digest or onto no commit at all. Because this behaviour follows from the "
 "2f + 1 quorum rule rather than from any property of a particular model, it is expected to "
 "generalise to other generators and other defect types, which is the strongest claim the "
 "study makes.",
 "The repair-rate interpretation is more measured. On the real-world subset the consensus "
 "mode improved both the safety-violation rate and the repair rate relative to the "
 "baseline, with the discordant pairs favouring consensus six to one, but the exact "
 "McNemar p-value of 0.125 means the sample is too small to call the effect significant. "
 "The reasonable reading is that the direction is consistent with the safety mechanism "
 "doing useful work downstream, while the magnitude awaits confirmation on a larger "
 "dataset. The study resists the temptation to present the directional result as more than "
 "it is, because doing so would undermine the credibility of the firmer safety claim.",
 "A third interpretation concerns the negative results, which are as informative as the "
 "positive ones. Validator decorrelation was imperfect, falling from near-total agreement "
 "on easy synthetic cases to a lower but still high level on the harder real-world subset, "
 "which shows that model diversity reduces but does not eliminate correlated error. The "
 "e-commerce invariant gate showed no measurable effect on the headline outcomes, which "
 "indicates that the quorum and sandbox already screened the unsafe candidates and that the "
 "invariant check functions as defence in depth rather than as a primary filter. Reporting "
 "these honestly strengthens rather than weakens the thesis, because it shows the "
 "conclusions track the data.",
]),
("5.3 Comparison with Existing Methods", [
 "Compared with single-agent LLM repair, the consensus layer trades latency for a safety "
 "guarantee that the single agent cannot offer at all. A single agent has no independent "
 "check on its own output, so its safety rests entirely on the base model behaving well, "
 "which the failure modes of stochastic generation make untenable for autonomous "
 "production use. The consensus layer replaces that implicit trust with an explicit fault "
 "budget and a proven agreement property, at the cost of running several validators per "
 "decision. For an operator weighing autonomous remediation, this is the relevant "
 "comparison, and it favours the consensus layer wherever the cost of an unsafe fix "
 "exceeds the cost of additional inference.",
 "Compared with existing multi-agent frameworks, the distinction is the nature of the "
 "aggregation. Coordinator-mediated frameworks reintroduce a single point of trust, and "
 "majority-vote frameworks over homogeneous agents fail in correlated ways; neither "
 "withstands an equivocating or adversarial member. The present approach differs by using "
 "a genuine Byzantine-agreement protocol over heterogeneous voters with the proposer "
 "excluded from voting, which is what allows it to survive the equivocation attack that "
 "defeats a naive vote. The comparison is therefore not about incremental quality on a "
 "benchmark but about a qualitative safety property that the other arrangements do not "
 "claim and were not designed to provide.",
 "Against the automated-program-repair literature more broadly, the contribution is "
 "complementary rather than competitive. The consensus layer does not generate patches and "
 "so does not compete with search-based, semantic or learning-based generators; it governs "
 "whether their output may be applied. This means advances in any of those generation "
 "techniques can be adopted beneath the same safety boundary, which is a more durable "
 "position than tying the contribution to a particular generation method that future work "
 "may supersede.",
]),
("5.4 Critical Analysis of Findings", [
 "A critical reading must confront the limitations squarely. The most significant is "
 "sample size: the repair-rate evidence rests on modest defect sets, and the headline "
 "paired comparison does not reach statistical significance. This limits the strength of "
 "any claim about how much the consensus layer improves repair outcomes, and it is the "
 "reason those outcomes are labelled preliminary throughout. The remedy is a larger "
 "replication with more defects and more provider diversity, which the reproducible harness "
 "is explicitly designed to support but which available compute did not permit within this "
 "study.",
 "A second limitation is the oracle. The Python experiments use a run-as-script oracle "
 "that is weaker than a full test suite, so a fix counted as successful there may still be "
 "overfitted. The study mitigates this by adding the Defects4J full-suite evaluation and "
 "by reporting zero unsafe commits under that stricter standard, but the asymmetry between "
 "the strong Java oracle and the weaker Python oracle remains a threat to the "
 "interpretation of the Python repair rates. A third limitation is scope: the safety "
 "demonstration is confined to a single-host simulation and does not include the "
 "view-change that would provide liveness under a failed primary, nor multi-host "
 "deployment. These are real boundaries on what the study proves, and they are stated as "
 "such rather than glossed over.",
 "Set against these limitations, the findings are robust where it matters most. The "
 "safety property is demonstrated by construction under the strongest single-member attack "
 "in the matrix, it does not depend on sample size because it is deterministic given the "
 "seed, and it does not depend on the oracle because it concerns agreement rather than "
 "patch quality. A fair critical summary is therefore that the study firmly establishes the "
 "safety contribution it set out to make, while the downstream repair benefits it enables "
 "are promising but await a larger and better-instrumented evaluation.",
]),
("6.2 Conclusions", [
 "The study set out to determine whether genuine Byzantine fault tolerance can be brought "
 "to bear on the decision to apply an automated repair, and whether doing so yields a "
 "demonstrable safety guarantee. The answer, on the evidence gathered, is that it can and "
 "it does. A consensus layer of 3f + 1 model-diverse validators with a 2f + 1 quorum, "
 "excluding the proposer from voting and authenticating every message, preserves agreement "
 "under an equivocating primary where a naive vote splits, rejects forged messages, "
 "tolerates faults up to the replication bound and fails safely beyond it. This is the "
 "core conclusion, and it earns the project its title on the safety axis through direct "
 "demonstration rather than assertion.",
 "The secondary conclusions are reported with calibrated confidence. The consensus layer "
 "is associated with improved safety-violation and repair rates on the real-world subset, "
 "in a consistent direction, but the effect does not reach statistical significance on the "
 "available sample and is therefore preliminary. Model diversity reduces correlated error "
 "without eliminating it, and the e-commerce invariant gate acts as defence in depth rather "
 "than as a primary filter. Each of these is stated as the data warrant, and together they "
 "describe an approach whose safety contribution is firm and whose repair contribution is "
 "promising and worth scaling.",
 "The broader conclusion is methodological. By treating an unreliable LLM agent as a "
 "Byzantine replica and applying a protocol with a proven safety property, the study shows "
 "that the decades of distributed-systems theory developed for crashed and compromised "
 "servers can be repurposed to govern stochastic reasoning agents. This reframing is the "
 "durable idea the dissertation contributes, and it is independent of any particular model "
 "or benchmark: as generators improve, the same safety boundary continues to apply, which "
 "is what makes the contribution worth building on.",
]),
("6.3.2 Recommendations for Future Research", [
 "Three lines of future work follow directly from the limitations identified. The first is "
 "a large-scale replication of the repair-rate evaluation, with a substantially larger "
 "defect set and more provider diversity, so that the directional improvement observed here "
 "can be confirmed or refuted with adequate statistical power. The reproducible harness was "
 "built with this extension in mind, and the main barrier is compute rather than design, so "
 "this is the most immediately actionable next step.",
 "The second line is to complete the protocol on the liveness axis. Implementing the "
 "PBFT view-change would allow the system to make progress under a failed or "
 "permanently-faulty primary rather than merely failing safely, and deploying the "
 "validators across multiple physical hosts would move the demonstration from a single-host "
 "simulation toward a realistic distributed setting. Together these would let a future "
 "study claim both safety and liveness under the full PBFT fault model. The third line is "
 "to strengthen the oracle throughout, replacing the run-as-script Python oracle with "
 "full-suite verification comparable to the Defects4J evaluation, so that reported repair "
 "rates carry the same confidence as the safety results. Pursuing these three directions "
 "would convert the present study's firm but bounded safety contribution into a complete "
 "and well-powered account of Byzantine fault-tolerant autonomous repair.",
]),
]
