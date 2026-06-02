# -*- coding: utf-8 -*-
"""Final top-up pass: distinct content (validity, power, worked argument)."""

SECTIONS = [
("2.3 Theoretical and Empirical Literature", [
 "The literature reviewed in the subsections that follow is organised so that theory and "
 "evidence are read together within each strand rather than separated into abstract and "
 "applied halves. For Byzantine fault tolerance this means pairing the foundational "
 "impossibility and replication results with the systems that put them into practice; for "
 "multi-agent models it means pairing the architectural patterns with the empirical "
 "findings on ensembling and diversity; and for automated repair it means pairing the "
 "techniques with the evidence on patch overfitting that constrains them. Reading each "
 "strand in this integrated way is what makes the eventual synthesis specific enough to "
 "name gaps that the experiments can then address.",
]),
("2.3.1 Byzantine Fault Tolerance", [
 "It is worth working the quorum-intersection argument through concretely, because it is "
 "the single idea on which the whole safety claim rests. With n = 3f + 1 replicas and a "
 "quorum of 2f + 1, consider any two quorums Q1 and Q2 that each vouch for a committed "
 "value. Each quorum contains 2f + 1 members, and the total population is only 3f + 1, so "
 "by counting their intersection must contain at least (2f + 1) + (2f + 1) minus (3f + 1) "
 "members, which simplifies to f + 1. Since at most f members are faulty, at least one "
 "member of that intersection is honest, and an honest member never vouches for two "
 "conflicting values for the same slot. Therefore two conflicting values cannot both gather "
 "a quorum, which is exactly the agreement property. This small piece of arithmetic is why "
 "the replication bound is treated as a hard constraint rather than a parameter to tune.",
]),
("4.4.2 Statistical Significance", [
 "The reason the directional result does not reach significance is best understood as a "
 "question of statistical power rather than of effect direction. McNemar's exact test "
 "conditions on the discordant pairs, of which there were seven, split six to one. Even a "
 "perfect seven-to-zero split would yield an exact two-sided p-value of about 0.016, and "
 "the observed six-to-one split yields 0.125, so with only seven discordant pairs the test "
 "simply lacks the resolution to certify an effect at the conventional threshold. This is "
 "an argument for a larger sample, not against the effect: the direction is consistent and "
 "the per-case traces show the quorum doing intelligible work, but the honest conclusion is "
 "that the data are too few to license a significance claim, which is precisely why the "
 "study reports the repair outcome as preliminary throughout.",
]),
("5.4 Critical Analysis of Findings", [
 "It is useful to frame the limitations explicitly in terms of validity. Construct validity "
 "concerns whether the measures capture what they claim to; here the safety construct is "
 "well captured, because preserved agreement and zero unsafe commits are direct observations "
 "of the property of interest, whereas the repair construct is weakened on the Python set by "
 "the run-as-script oracle, which is why the Defects4J full-suite evaluation was added as a "
 "stronger measure. Internal validity concerns whether the observed differences are caused "
 "by the consensus layer rather than by confounds; the paired design, in which each defect "
 "is attempted in both modes, controls for defect difficulty, and the fixed seeds make the "
 "adversarial outcomes deterministic, which together give the internal validity its strength.",
 "External validity concerns how far the findings generalise. The safety findings "
 "generalise well in principle, because they follow from the quorum arithmetic rather than "
 "from any property of a particular model or defect, so they should hold for other "
 "generators and other tasks within the stated fault budget. The repair findings generalise "
 "poorly at present, because they rest on small samples from a limited set of projects, and "
 "extending them is the first item of future work. Naming the limitations in these three "
 "categories rather than as a single list makes clear that the study is strong exactly where "
 "its central claim lies and weak exactly where it labels its claims preliminary, which is "
 "the alignment between confidence and evidence that the whole dissertation aims for.",
]),
("5.3 Comparison with Existing Methods", [
 "A more concrete comparison helps locate the contribution. A single-agent repair system "
 "makes one model call to decide whether to apply a fix and offers no fault budget at all, "
 "so its safety is undefined under a compromised or hallucinating model. A homogeneous "
 "majority of k agents drawn from one base model offers an apparent fault budget but a real "
 "one near zero against correlated error, because the agents share blind spots and can be "
 "wrong together. The consensus layer offers a defined fault budget of f within a population "
 "of 3f + 1 heterogeneous validators, with a proven agreement property and an auditable "
 "certificate per decision. The cost is f-dependent inference and latency, but the safety "
 "property is categorical rather than probabilistic, and it is that categorical guarantee, "
 "absent from both alternatives, that justifies the additional cost for autonomous "
 "production use.",
]),
("6.2 Conclusions", [
 "Stated as a single contribution, the dissertation shows that a stochastic reasoning agent "
 "can be governed by the same Byzantine-agreement machinery developed for crashed and "
 "compromised servers, and that doing so yields a safety guarantee that is demonstrated "
 "rather than asserted. The firm result is the preservation of agreement under an "
 "equivocating primary within a stated fault budget; the preliminary results are the "
 "directional improvements in repair and safety-violation rates; and the negative results "
 "on decorrelation and domain invariants locate the boundaries of what diversity and "
 "invariant checking add. The value of the work is that each of these is reported in "
 "proportion to its evidence, so that what a reader takes away is calibrated to what the "
 "study actually established.",
]),
]
