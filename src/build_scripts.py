"""Build the speaker scripts from src/briefing.py and src/deck_content.py:
    reports/WhichTexasBird_Speaker_Scripts.pdf   (read/print)
    reports/WhichTexasBird_Speaker_Scripts.docx  (edit, e.g. in Google Docs)

Run from the repo root:  python src/build_scripts.py
"""

import importlib.util
import re
from html import escape

from docx import Document
from docx.shared import Pt, RGBColor as DocxRGB
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = load("content", "src/deck_content.py")
bf = load("briefing", "src/briefing.py")

TITLE = "Which Texas Bird Is It? Speaker Notes"
SUB = "DATA 4380 · Mateen Jan, Tej Govindu, Alejandro Alfonso · Dr. Masoud Rostami · November 18, 2026"
HOWTO = ("Page 1–2: the big picture of the whole project. After that: each person's slides with what to SAY, what the slide "
         "MEANS in plain English, and POSSIBLE QUESTIONS. Each person talks about 5 minutes (the guidelines ask for 4–6).")


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
body = ParagraphStyle("body", parent=ss["Normal"], fontName="Calibri", fontSize=11, leading=14.5, spaceAfter=4)
title = ParagraphStyle("title", parent=body, fontName="Georgia-Bold", fontSize=20, leading=25, textColor=NIGHT, spaceAfter=4)
h1 = ParagraphStyle("h1", parent=body, fontName="Georgia-Bold", fontSize=16, leading=20, textColor=NIGHT, spaceBefore=4, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=body, fontName="Georgia-Bold", fontSize=12.5, leading=16, textColor=BLUE, spaceBefore=9, spaceAfter=3)
small = ParagraphStyle("small", parent=body, fontSize=10, leading=13, textColor=MUTED)
label = lambda c: ParagraphStyle("lbl", parent=body, fontName="Calibri-Bold", fontSize=10, textColor=c, spaceBefore=3, spaceAfter=1)
means = ParagraphStyle("means", parent=body, backColor=colors.HexColor("#EAF2F8"), borderPadding=(4, 6, 4, 6), spaceBefore=2, spaceAfter=6)


def bullets(items):
    return ListFlowable([ListItem(Paragraph(i, body), leftIndent=12) for i in items], bulletType="bullet", start="•",
                        leftIndent=14, bulletFontName="Calibri")


def grid(rows, widths, bold_row=None):
    t = Table(rows, colWidths=widths)
    st = [("FONTNAME", (0, 0), (-1, -1), "Calibri"), ("FONTNAME", (0, 0), (-1, 0), "Calibri-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 10.5), ("BACKGROUND", (0, 0), (-1, 0), NIGHT), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C8D3DC")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F7FA")]),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if bold_row:
        st += [("FONTNAME", (0, bold_row), (-1, bold_row), "Calibri-Bold"), ("BACKGROUND", (0, bold_row), (-1, bold_row), colors.HexColor("#EAF2F8"))]
    t.setStyle(TableStyle(st))
    return t


story = [Paragraph(TITLE, title), Paragraph(SUB, small), Spacer(1, 6), Paragraph(escape(HOWTO), body)]
rows = [["Who", "Part", "Slides", "Time"]]
for name, part, rng, t in m.SPEAKERS:
    rows.append([name, part, f"{rng[0]}–{rng[-1]}", t])
story += [grid(rows, [1.0 * inch, 4.2 * inch, 0.8 * inch, 1.0 * inch]), Spacer(1, 6),
          Paragraph("The big picture", h1), Paragraph(escape(bf.INTRO), small)]
for sec_title, items in bf.SECTIONS:
    story.append(Paragraph(escape(sec_title), h2))
    story.append(bullets(items))
    if sec_title.startswith("The results"):
        story += [Spacer(1, 3), grid(bf.RESULTS, [1.4 * inch, 2.1 * inch, 1.1 * inch, 0.9 * inch, 1.3 * inch], bold_row=3)]

for name, part, rng, t in m.SPEAKERS:
    story.append(PageBreak())
    story.append(Paragraph(f"{escape(name.upper())}: {escape(part)}", h1))
    story.append(Paragraph(f"Slides {rng[0]}–{rng[-1]} · {escape(t)}", small))
    for n in rng:
        block = [Paragraph(f"Slide {n} · {escape(m.SLIDE_NAMES[n])}", h2), Paragraph("SAY", label(BLUE))]
        block += [Paragraph(escape(x), body) for x in m.SAY[n]]
        if n in m.HANDOFF:
            block.append(Paragraph(f"<i>Hand off: \"{escape(m.HANDOFF[n])}\"</i>", body))
        block += [Paragraph("WHAT IT MEANS", label(BROWN)), Paragraph(escape(m.MEANS[n]), means)]
        if m.ASK.get(n):
            block.append(Paragraph("POSSIBLE QUESTIONS", label(MUTED)))
            block.append(bullets([f"<b>{escape(q)}</b> {escape(a)}" for q, a in m.ASK[n]]))
        story.append(KeepTogether(block))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Calibri", 9)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.5 * inch, "Which Texas Bird Is It? · DATA 4380 · Speaker notes")
    canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


SimpleDocTemplate("reports/WhichTexasBird_Speaker_Scripts.pdf", pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                  topMargin=0.65 * inch, bottomMargin=0.8 * inch, title=TITLE).build(story, onFirstPage=footer, onLaterPages=footer)

# ------------------------------------------------------------------ Word
doc = Document()
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(11)
doc.add_heading(TITLE, 0)
doc.add_paragraph(SUB)
doc.add_paragraph(HOWTO)


def table(rows):
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    for row in rows:
        for c, v in zip(t.add_row().cells, row):
            c.text = str(v)


def rich(par, txt):
    for i, part in enumerate(re.split(r"</?b>", txt)):
        if part:
            par.add_run(part).bold = i % 2 == 1


def lab(txt, rgb):
    r = doc.add_paragraph().add_run(txt)
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = DocxRGB(*rgb)


table([["Who", "Part", "Slides", "Time"]] + [[n, p, f"{r[0]}–{r[-1]}", t] for n, p, r, t in m.SPEAKERS])
doc.add_heading("The big picture", 1)
doc.add_paragraph(bf.INTRO)
for sec_title, items in bf.SECTIONS:
    doc.add_heading(sec_title, 2)
    for it in items:
        rich(doc.add_paragraph(style="List Bullet"), it)
    if sec_title.startswith("The results"):
        table(bf.RESULTS)
for name, part, rng, t in m.SPEAKERS:
    doc.add_page_break()
    doc.add_heading(f"{name.upper()}: {part}", 1)
    doc.add_paragraph(f"Slides {rng[0]}–{rng[-1]} · {t}")
    for n in rng:
        doc.add_heading(f"Slide {n} · {m.SLIDE_NAMES[n]}", 2)
        lab("SAY", (0x1F, 0x6F, 0xA8))
        for x in m.SAY[n]:
            doc.add_paragraph(x)
        if n in m.HANDOFF:
            doc.add_paragraph().add_run(f"Hand off: \"{m.HANDOFF[n]}\"").italic = True
        lab("WHAT IT MEANS", (0xA8, 0x5C, 0x20))
        doc.add_paragraph(m.MEANS[n])
        if m.ASK.get(n):
            lab("POSSIBLE QUESTIONS", (0x5E, 0x6B, 0x78))
            for q, a in m.ASK[n]:
                para = doc.add_paragraph(style="List Bullet")
                para.add_run(q + " ").bold = True
                para.add_run(a)
doc.save("reports/WhichTexasBird_Speaker_Scripts.docx")

for name, part, rng, tm in m.SPEAKERS:
    w = sum(word_count(n) for n in rng)
    print(f"{name}: {w} words, about {w / 135:.1f} min at 135 wpm")
print("saved reports/WhichTexasBird_Speaker_Scripts.pdf and .docx")
