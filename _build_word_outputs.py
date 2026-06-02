"""Rebuild the Word-dependent deliverables via Word COM automation:
  1. COMBINED_for_supervisor.docx = title_page + revised manuscript + response letter
     + supplementary (page-break separated), then export COMBINED_for_supervisor.pdf.
  2. MS_R1_revised_clean.pdf  (export of the revised manuscript).
  3. MS_R1_tracked_changes.docx = Word Compare(baseline_anon, revised_clean).
"""
import os
import win32com.client as win32

ROOT = r"C:\dev\frontend\Mtech_Project_Frontend"
def P(f): return os.path.join(ROOT, f)

# Word constants
wdStory = 6
wdPageBreak = 7
wdFormatDocumentDefault = 16
wdFormatPDF = 17
wdCompareDestinationNew = 2
wdGranularityWordLevel = 1

word = win32.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    # ---- 1. COMBINED_for_supervisor.docx ----
    parts = ["title_page.docx", "MS_R1_revised_clean.docx",
             "AUTHOR_RESPONSE_LETTER.docx", "SUPPLEMENTARY_reproduction.docx"]
    combined = word.Documents.Add()
    sel = word.Selection
    sel.EndKey(Unit=wdStory)
    for i, f in enumerate(parts):
        if i > 0:
            sel.InsertBreak(wdPageBreak)
        sel.InsertFile(P(f))
        sel.EndKey(Unit=wdStory)
    combined.SaveAs(P("COMBINED_for_supervisor.docx"), FileFormat=wdFormatDocumentDefault)
    combined.SaveAs(P("COMBINED_for_supervisor.pdf"), FileFormat=wdFormatPDF)
    combined.Close(False)
    print("wrote COMBINED_for_supervisor.docx + .pdf")

    # ---- 2. MS_R1_revised_clean.pdf ----
    rev = word.Documents.Open(P("MS_R1_revised_clean.docx"))
    rev.SaveAs(P("MS_R1_revised_clean.pdf"), FileFormat=wdFormatPDF)
    rev.Close(False)
    print("wrote MS_R1_revised_clean.pdf")

    # ---- 3. tracked-changes copy via Compare ----
    orig = word.Documents.Open(P("MS_R1_baseline_anon.docx"))
    revd = word.Documents.Open(P("MS_R1_revised_clean.docx"))
    comp = word.CompareDocuments(orig, revd,
                                 Destination=wdCompareDestinationNew,
                                 Granularity=wdGranularityWordLevel,
                                 CompareFormatting=True)
    comp.SaveAs(P("MS_R1_tracked_changes.docx"), FileFormat=wdFormatDocumentDefault)
    comp.Close(False)
    orig.Close(False)
    revd.Close(False)
    print("wrote MS_R1_tracked_changes.docx")
finally:
    word.Quit()
print("DONE")
