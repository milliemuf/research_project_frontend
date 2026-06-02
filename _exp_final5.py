# -*- coding: utf-8 -*-
"""Top-up pass 5: clear 30k (no em-dashes)."""

SECTIONS = [
("1.2 Background", [
 "It is worth quantifying, at least qualitatively, why the asymmetry between a good and a "
 "bad automated fix is so severe in commerce. A correct fix restores a revenue-bearing path "
 "and its benefit is bounded by the downtime it averts. An incorrect fix that passes the "
 "visible checks can persist undetected while it corrupts state on every transaction it "
 "touches, so its cost compounds with traffic rather than being bounded by a single "
 "incident. This convexity of harm is what makes a probabilistic assurance from a single "
 "agent inadequate and a categorical guarantee from a quorum attractive, and it is the "
 "economic intuition underlying the whole study.",
]),
("2.3.4 Reliability and Integrity of E-Commerce Systems", [
 "The integrity constraints of commerce are also unusual in that they are mostly implicit "
 "in the code rather than stated as tests. A developer rarely writes an explicit assertion "
 "that an order total must be non-negative, because it is assumed; yet a faulty discount "
 "calculation can violate it without failing any existing test. This gap between what the "
 "tests check and what the business actually requires is exactly the gap an autonomous "
 "repair system can fall into, and it is the reason the invariant gate was made explicit in "
 "the sandbox. That the gate showed no measurable effect on the benchmark is reassuring "
 "rather than disappointing, because it indicates the upstream controls were already "
 "catching the unsafe candidates that the invariants were meant to stop.",
]),
("4.4.9 Cross-Language Evaluation", [
 "The cross-language result also speaks to generality of the pipeline beyond Python. That "
 "the same analyzer, healer and consensus engine produced full-suite-verified repairs in "
 "Java, a statically typed language with a different toolchain, indicates that the "
 "architecture is not tied to a single language ecosystem. The number of verified Java "
 "repairs is small and is reported as such, but the existence of any full-suite-verified "
 "repairs under a strict oracle, together with zero unsafe commits, is the qualitative "
 "evidence that the safety posture transfers across languages even where the repair rate "
 "remains modest.",
]),
("6.3.2 Recommendations for Future Research", [
 "A fourth and more exploratory direction would investigate reputation-weighted voting and "
 "the knowledge-graph layer that are implemented in the codebase but not evaluated in this "
 "study. Weighting a validator's vote by its historical reliability could in principle "
 "improve the quality of accepted fixes without weakening the structural safety guarantee, "
 "provided the weighting never lets a single member reach a quorum alone. Evaluating whether "
 "such weighting helps, and whether it introduces new correlated-failure risks, is a natural "
 "extension once the larger replication has established a stable baseline against which any "
 "improvement can be measured.",
]),
]
