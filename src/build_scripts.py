"""Build the speaker scripts from src/deck_content.py:
    reports/WhichTexasBird_Speaker_Scripts.pdf   (read/print)
    reports/WhichTexasBird_Speaker_Scripts.docx  (edit, e.g. in Google Docs)

Run from the repo root:  python src/build_scripts.py
"""

import importlib.util
from html import escape

from docx import Document
from docx.shared import Pt, RGBColor as DocxRGB
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

spec = importlib.util.spec_from_file_location("content", "src/deck_content.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

TITLE = "Which Texas Bird Is It? Speaker Scripts"
SUB = "DATA 4380 · Mateen Jan, Tej Govindu, Alejandro Alfonso · Dr. Masoud Rostami · November 18, 2026"
HOWTO = ("For each slide: SAY is the script (also in the slide's speaker notes), WHY WE DID IT is the reasoning so you can "
         "explain it in your own words, and IF ASKED covers likely questions. Practice out loud with a timer: each person "
         "should land between 7 and 10 minutes (21 minutes minimum for the group).")
KEY = ("1,710 photos · 10 species · split 1,197 / 256 / 257 · majority guess F1 0.02 · baseline CNN validation F1 0.61 "
       "(test 0.68) · augmentation 0.61 → 0.56 · MobileNetV2 0.956 (with aug.) / 0.964 (without) · fine-tuned 0.960 · "
       "final: frozen MobileNetV2, no augmentation: test accuracy 96.1%, macro F1 0.964 · 10 test mistakes, all in lookalike pairs "
       "(5 hawks, 4 crow/grackle, 1 dove) · baseline 81 mistakes · hawks ≈ 1/3 sky in borders · Grad-CAM border share 17–34% vs. 49% of area.")


def word_count(n):
    return sum(len(x.split()) for x in m.SAY[n])


# ------------------------------------------------------------------ PDF
pdfmetrics.registerFont(TTFont("Calibri", "C:/Windows/Fonts/calibri.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Bold", "C:/Windows/Fonts/calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Italic", "C:/Windows/Fonts/calibrii.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", "C:/Windows/Fonts/georgiab.ttf"))
pdfmetrics.registerFontFamily("Calibri", normal="Calibri", bold="Calibri-Bold", italic="Calibri-Italic")

NIGHT = colors.HexColor("#142B45")
BLUE = colors.HexColor("#1F6FA8")
BROWN = colors.HexColor("#A85C20")
MUTED = colors.HexColor("#5E6B78")

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["Normal"], fontName="Calibri", fontSize=11, leading=15, spaceAfter=5)
title = ParagraphStyle("title", parent=body, fontName="Georgia-Bold", fontSize=20, leading=25, textColor=NIGHT, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=body, fontName="Georgia-Bold", fontSize=16, leading=20, textColor=NIGHT, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=body, fontName="Georgia-Bold", fontSize=12.5, leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=4)
small = ParagraphStyle("small", parent=body, fontSize=10, leading=13, textColor=MUTED)
label = lambda c: ParagraphStyle("lbl", parent=body, fontName="Calibri-Bold", fontSize=10, textColor=c, spaceBefore=4, spaceAfter=2)


def bullets(items):
    return ListFlowable([ListItem(Paragraph(i, body), leftIndent=12) for i in items], bulletType="bullet", start="•",
                        leftIndent=14, bulletFontName="Calibri")


story = [Paragraph(TITLE, title), Paragraph(SUB, small), Spacer(1, 8), Paragraph("<b>How to use this:</b> " + escape(HOWTO), body)]
rows = [["Speaker", "Part", "Slides", "Words", "Time"]]
for name, part, rng, t in m.SPEAKERS:
    rows.append([name, part, f"{rng[0]}–{rng[-1]}", f"{sum(word_count(n) for n in rng):,}", t])
tbl = Table(rows, colWidths=[1.0 * inch, 3.2 * inch, 0.8 * inch, 0.8 * inch, 1.1 * inch])
tbl.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "Calibri"), ("FONTNAME", (0, 0), (-1, 0), "Calibri-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10.5), ("BACKGROUND", (0, 0), (-1, 0), NIGHT), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D3DC")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EAF2F8")]),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story += [Spacer(1, 6), tbl, Spacer(1, 10), Paragraph("<b>Key numbers everyone should know:</b> " + escape(KEY), body),
          Paragraph("Slides 22–23 are backup slides (per-species F1, training curves) for questions.", small)]

for name, part, rng, t in m.SPEAKERS:
    story.append(PageBreak())
    story.append(Paragraph(f"{escape(name)}: {escape(part)} (slides {rng[0]}–{rng[-1]}, {escape(t)})", h1))
    for n in rng:
        story.append(Paragraph(f"Slide {n} · {escape(m.SLIDE_NAMES[n])}", h2))
        story.append(Paragraph("SAY", label(BLUE)))
        story += [Paragraph(escape(x), body) for x in m.SAY[n]]
        if n in m.HANDOFF:
            story.append(Paragraph(f"<i>Hand off: \"{escape(m.HANDOFF[n])}\"</i>", body))
        if m.WHY.get(n):
            story.append(Paragraph("WHY WE DID IT", label(BROWN)))
            story.append(bullets([escape(w) for w in m.WHY[n]]))
        if m.ASK.get(n):
            story.append(Paragraph("IF ASKED", label(MUTED)))
            story.append(bullets([f"<b>{escape(q)}</b> {escape(a)}" for q, a in m.ASK[n]]))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Calibri", 9)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.5 * inch, "Which Texas Bird Is It? · DATA 4380 · Speaker scripts")
    canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


SimpleDocTemplate("reports/WhichTexasBird_Speaker_Scripts.pdf", pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                  topMargin=0.7 * inch, bottomMargin=0.8 * inch, title=TITLE).build(story, onFirstPage=footer, onLaterPages=footer)

# ------------------------------------------------------------------ Word
doc = Document()
st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(11)
doc.add_heading(TITLE, 0)
doc.add_paragraph(SUB)
p = doc.add_paragraph()
p.add_run("How to use this: ").bold = True
p.add_run(HOWTO)
t = doc.add_table(rows=1, cols=5)
t.style = "Light Grid Accent 1"
for c, h in zip(t.rows[0].cells, ["Speaker", "Part", "Slides", "Words", "Time"]):
    c.text = h
for name, part, rng, tm in m.SPEAKERS:
    cells = t.add_row().cells
    for c, v in zip(cells, [name, part, f"{rng[0]}–{rng[-1]}", f"{sum(word_count(n) for n in rng):,}", tm]):
        c.text = v
p = doc.add_paragraph()
p.add_run("Key numbers everyone should know: ").bold = True
p.add_run(KEY)


def lab(txt, rgb):
    r = doc.add_paragraph().add_run(txt)
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = DocxRGB(*rgb)


for name, part, rng, tm in m.SPEAKERS:
    doc.add_page_break()
    doc.add_heading(f"{name}: {part} (slides {rng[0]}–{rng[-1]}, {tm})", 1)
    for n in rng:
        doc.add_heading(f"Slide {n} · {m.SLIDE_NAMES[n]}", 2)
        lab("SAY", (0x1F, 0x6F, 0xA8))
        for x in m.SAY[n]:
            doc.add_paragraph(x)
        if n in m.HANDOFF:
            doc.add_paragraph().add_run(f"Hand off: \"{m.HANDOFF[n]}\"").italic = True
        if m.WHY.get(n):
            lab("WHY WE DID IT", (0xA8, 0x5C, 0x20))
            for w in m.WHY[n]:
                doc.add_paragraph(w, style="List Bullet")
        if m.ASK.get(n):
            lab("IF ASKED", (0x5E, 0x6B, 0x78))
            for q, a in m.ASK[n]:
                para = doc.add_paragraph(style="List Bullet")
                para.add_run(q + " ").bold = True
                para.add_run(a)
doc.save("reports/WhichTexasBird_Speaker_Scripts.docx")

for name, part, rng, tm in m.SPEAKERS:
    w = sum(word_count(n) for n in rng)
    print(f"{name}: {w} words, about {w / 135:.1f} min at 135 wpm")
print("saved reports/WhichTexasBird_Speaker_Scripts.pdf and .docx")
