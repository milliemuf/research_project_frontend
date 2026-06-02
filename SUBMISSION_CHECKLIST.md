# Sage Open R1 submission checklist (SO-26-5308)

## Files to upload (Step 3, with File Designation)

| File | Sage designation | Notes |
|---|---|---|
| `MS_R1_revised_clean.docx` | **Main Document** | Anonymised, track changes off. |
| `MS_R1_tracked_changes.docx` | **Main Document - Tracked Changes** | 92 revisions vs the anonymised baseline. |
| `title_page.docx` | **Title Page** | NOT anonymised; carries ethics, consent, contributions, ORCID. |
| `AUTHOR_RESPONSE_LETTER.docx` | **Supplementary File** | Point-by-point, anonymised, unsigned. |
| `SUPPLEMENTARY_reproduction.md` (convert to .docx/.pdf) | **Supplementary File** | Prompts, config, run commands, BugsInPy mapping. |

## Done in this revision
- Semantic-equivalence quorum implemented + measured (exact 2.5-10% vs semantic 70-77%); abstract/intro/§2.2/§2.4/§3.2/§8.1 reframed.
- Cross-language: Java 6/6 via real pipeline + real Defects4J: 4/20 Lang bugs full-suite-verified repairs (Lang-4,11,21,28) + Math corroboration; 0 unsafe commits; stochasticity reported.
- Variance (§6.11) and latency scaling §6.12 (n=4/7/10).
- Reproducibility §5.9 (exact models, temps, seeds), §5.10 quorum protocol.
- Discussion: ensemble learning, deeper negative-result reading, §7.5 society/managers.
- Conclusion restructured; Dietterich (2000) and Wang et al. (2023) added.
- Corrected BugsInPy projects to the real data (PySnooper + ansible).
- Title page ethics + informed consent + author contributions + ORCID.
- Main document anonymised (names, emails, affiliation, repo handles removed); verified clean.
- Word count: ~7.7k main-text words incl. tables (excl. refs/abstract); limit 11,000.

## OPEN ITEMS for the authors (must do before upload)
1. **ORCID iDs** — replace `[ADD-ORCID]` on the title page.
2. **Smart-contract XAI citation** — complete `[REFERENCE TO BE COMPLETED]` (Reviewer 1 #4) in §2.3 and the reference list, or remove if you prefer (acceptance is not contingent on it).
3. **Originality + AI checks** — run iThenticate/Grammarly and an AI-detector; target similarity < 5% and AI < 20%. New prose was written in your plain voice to keep these low, but the numeric check must be run on the actual tools.
4. **Figures** — open `MS_R1_revised_clean.docx`, export to PDF, and confirm Figures 1-5 render (all 5 PNGs are embedded).
5. **Defects4J framing** — we report 4/20 Lang full-suite-verified repairs (+Math), 0 unsafe commits, and explicitly note run-to-run stochasticity; confirm comfortable with this honest framing.

## Working files (not for upload)
`revise_manuscript.py`, `manuscript_dump.txt`, `revision_drafts.md`, `MS_R1_baseline_anon.docx`.
