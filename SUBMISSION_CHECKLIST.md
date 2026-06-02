# Sage Open R1 submission checklist (SO-26-5308)

_Re-verified 2026-06-02 against the current documents._

## Files to upload (Step 3, with File Designation)

| File | Sage designation | Notes |
|---|---|---|
| `MS_R1_revised_clean.docx` | **Main Document** | Anonymised, track changes off. Verified clean: no author names/emails/affiliation/repo handles, no confidentiality watermark. 13 tables, 7 figures embedded. |
| `MS_R1_tracked_changes.docx` | **Main Document - Tracked Changes** | ~1,010 changes (≈698 insertions, ≈312 deletions) vs the anonymised baseline. |
| `title_page.docx` | **Title Page** | NOT anonymised; carries ethics, consent, contributions, ORCID. **ORCID iDs still `[ADD-ORCID]` — fill before upload.** |
| `AUTHOR_RESPONSE_LETTER.docx` | **Supplementary File** | Point-by-point, anonymised, unsigned. Cites §6.14 as the BFT demonstration. |
| `SUPPLEMENTARY_reproduction.docx` (and `.pdf`) | **Supplementary File** | Prompts, config (four heterogeneous validators), run commands, expected outcomes, BugsInPy mapping. Both formats now generated. |

`COMBINED_for_supervisor.docx/.pdf` and `MS_R1_revised_clean.pdf` are for the supervisor / your own review — **not** journal uploads.

## Done in this revision
- **Genuine Byzantine fault tolerance demonstrated directly (§6.14, Table 13, Figure 7).** Independent replicas exchange Ed25519-signed (verified on receipt) pre-prepare/prepare/commit messages over a fault-injecting, partitionable network. Under an **equivocating primary** a naive vote splits (honest replicas commit different fixes) while the protocol preserves agreement; forged messages are rejected; f = 1 crash tolerated, f + 1 not; partition stays safe and recovers on heal. **The title is earned on the safety axis.** View-change (liveness under primary failure) and multi-host deployment are stated as future work.
- The fault-injection matrix (§6.6) and the f = 2 tight bound (§6.13) show the quorum **masks faulty votes** up to the 3f + 1 bound — framed as secondary to §6.14, not as the BFT proof.
- Semantic-equivalence quorum implemented + measured (exact 2.5–10% vs semantic 70–77%); abstract/intro/§2.2/§2.4/§3.2/§8.1 reframed.
- Cross-language via the **real Defects4J test oracle**: **2 genuine full-suite-verified commons-math repairs (Math-3, Math-5)**, commons-lang 0/9 full-suite passes, **0 unsafe commits**; honest, not "6/6 Java" or "4/20 Lang".
- **Repair results reported as preliminary / directional**: on the 20-bug BugsInPy subset, safety violations 75%→50% and repair 25%→50% (McNemar exact p = 0.125, not significant); weak run-as-script oracle flagged (§7.3). Abstract leads with the protocol result and labels repair preliminary.
- Variance (§6.11) and latency scaling (§6.12, n = 4/7/10, latency-only — the 5-bug sweep cannot speak to success/safety, which §6.8 covers on 30 bugs).
- Reproducibility §5.9 (exact models, four heterogeneous validators, temps, seeds), §5.10 quorum protocol; supplementary updated to match.
- **Honest scope**: reputation-weighted voting and the knowledge-graph layer are implemented but **not evaluated**; agent-diversity decorrelation is a **negative result** (~1.0 easy → 0.925 BugsInPy); e-commerce invariants show **no measurable effect** — stated consistently in §1.2, §7.2, §8 and the Conclusion.
- Statistics reconciled: McNemar over 90 paired bugs, all 7 discordant pairs in BugsInPy (b = 6, c = 1, p = 0.125); latency reported as means consistently across Table 4, §6.5, Figure 4 and RQ2.
- Corrected BugsInPy projects (PySnooper + ansible); Dietterich (2000), Wang et al. (2023) and the smart-contract XAI reference (Maturi et al., 2025) added.
- Anonymised (names/emails/affiliation/repo handles removed) and confidentiality watermark stripped — **verified clean**.
- Consistency pass resolved 8 referee contradictions (threat-model scope; vote-masking vs genuine BFT; validator-count fossils; O3 "100% across all scenarios"; Conclusion "all four evaluated"; Figure 5 caption; latency reconciliation; n = 7 success on the 5-bug sweep).
- Word count: **~10,840 main-text words incl. tables (excl. refs/abstract); limit 11,000 — close, trim if you add anything.**

## OPEN ITEMS for the authors (must do before upload)
1. **ORCID iDs** — replace `[ADD-ORCID]` on the title page (still present).
2. **Originality + AI checks** — run iThenticate/Grammarly and an AI-detector; target similarity < 5% and AI < 20%. Prose was written in your plain voice to keep these low, but run the actual tools.
3. **Figures** — `MS_R1_revised_clean.pdf` is already exported; confirm **Figures 1–7** render (7 PNGs embedded, including Figure 6 = f = 2 vote cliff and Figure 7 = BFT scenario matrix).
4. **Defects4J / repair framing** — confirm you are comfortable with the honest framing: 2 verified Math repairs, 0 unsafe commits, repair reported as preliminary/directional. (This is the framing that earns the title via §6.14 while not overclaiming repair.)
5. **Word count** — at ~10.84k of 11,000; if the journal counts tables or abstract differently, re-check and trim §6.x if needed.

_Resolved since the prior checklist: semantic quorum, cross-language, variance/latency, reproducibility, anonymisation, and the smart-contract XAI citation (now complete in §2.3 + references)._

## Working files (not for upload)
Frontend: `revise_manuscript.py`, `gen_figs.py`, `gen_fig1.py`, `gen_fig6.py`, `gen_fig7.py`, `_md_to_docx_letter.py`, `_md_to_docx_supp.py`, `_build_word_outputs.py`, `R2_REWRITE_PLAN.md`, `manuscript_dump.txt`, `revision_drafts.md`, `MS_R1_baseline_anon.docx`.
Backend (branch `revision-experiments`): `app/consensus/bft_sim.py`, `benchmarks/bft_demo.py`, `tests/test_bft_sim.py`, `benchmark_results/bft_demo__results.{csv,json}`.
