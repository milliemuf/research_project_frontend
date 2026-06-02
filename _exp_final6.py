# -*- coding: utf-8 -*-
"""Top-up pass 6: just over 30k (no em-dashes)."""

SECTIONS = [
("5.1 Presentation of Experimental Results", [
 "A note on how the figures and tables in this chapter should be read will help the "
 "interpretation that follows. The paired-outcome tables should be read down the discordant "
 "pairs, since those are the cases that carry the inferential weight; the adversarial-matrix "
 "figures should be read across the behaviours, comparing the naive and protocol columns to "
 "see where agreement is preserved; and the latency figure should be read as means per "
 "decision against validator count, separating the timing question from the success "
 "question. Presented together, these views are intended to let the reader reconstruct the "
 "argument from the evidence rather than take the summary on trust.",
]),
("4.4.2 Statistical Significance", [
 "For completeness, the analysis was framed in advance around the discordant pairs rather "
 "than chosen after inspecting the data, which guards against the selective reporting that "
 "inflates false positives. The decision to use the exact binomial form rather than the "
 "chi-square approximation was likewise made because the small count of discordant pairs "
 "violates the large-sample assumptions of the approximation, so the exact test is the "
 "honest choice even though it is more conservative. Reporting the test this way ensures the "
 "preliminary repair claim cannot be accused of having been engineered to reach "
 "significance, since by construction it does not.",
]),
("1.4 Justification", [
 "Finally, the choice to demonstrate rather than merely argue the safety property is itself "
 "a justified methodological stance. Safety claims in agentic systems are frequently "
 "asserted from architecture diagrams without being subjected to adversarial test, and such "
 "assertions are difficult to falsify and easy to overstate. By building a fault-injection "
 "harness and exhibiting the property under the strongest single-member attack, the study "
 "makes a claim that could in principle have failed and did not, which is a stronger form of "
 "evidence than any architectural argument. This commitment to falsifiable demonstration is "
 "what the rest of the dissertation is organised to deliver.",
]),
]
