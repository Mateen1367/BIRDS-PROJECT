"""Build the presentation deck: reports/WhichTexasBird_Presentation.pptx

Numbers come from reports/results.json (notebook 2) and data/processed/splits.csv (notebook 1).
Speaker notes come from src/deck_content.py.
Design: "field guide": night-sky navy, sky blue = final model, roadrunner brown = baseline,
cardinal red = lookalikes / mistakes, Georgia headings, Calibri body.

Run from the repo root:  python src/build_deck.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

spec = importlib.util.spec_from_file_location("content", "src/deck_content.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

R = json.load(open("reports/results.json"))
DF = pd.read_csv("data/processed/splits.csv")
FIG = Path("reports/figures")
THUMBS = FIG / "deck"
THUMBS.mkdir(exist_ok=True)

# ---------------------------------------------------------------- palette & fonts
NIGHT = RGBColor(0x14, 0x2B, 0x45)    # dark slides, table headers
BLUE = RGBColor(0x1F, 0x6F, 0xA8)     # final model / primary
SKY = RGBColor(0x8C, 0xB8, 0xD8)      # light blue (text on dark, secondary bars)
BROWN = RGBColor(0xC2, 0x6E, 0x2B)    # baseline (roadrunner brown)
RED = RGBColor(0xB2, 0x22, 0x34)      # cardinal red: lookalikes, mistakes, "didn't help"
INK = RGBColor(0x1D, 0x27, 0x33)
MUTED = RGBColor(0x5E, 0x6B, 0x78)
GRAY = RGBColor(0xB8, 0xC2, 0xCC)
TINT = RGBColor(0xEA, 0xF2, 0xF8)     # blue panel
SAND = RGBColor(0xF6, 0xEF, 0xE3)     # warm panel
ROSE = RGBColor(0xF9, 0xE6, 0xE8)     # red-tinted panel
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEAD = "Georgia"
NL = chr(10)
BODY = "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]

# ---------------------------------------------------------------- text-fit checker
_fonts, FIT_WARNINGS = {}, []
FONT_FILES = {("Calibri", False): "calibri.ttf", ("Calibri", True): "calibrib.ttf",
              ("Georgia", False): "georgia.ttf", ("Georgia", True): "georgiab.ttf"}


def _font(size, bold, face):
    key = (round(size), bold, face)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype("C:/Windows/Fonts/" + FONT_FILES[(face, bold)], round(size * 4))
    return _fonts[key]


def _lines(t, size, bold, face, width_pt):
    f, n = _font(size, bold, face), 0
    for para in t.split("\n"):
        line = ""
        n += 1
        for w in para.split(" "):
            trial = (line + " " + w).strip()
            if f.getlength(trial) / 4 > width_pt and line:
                n += 1
                line = w
            else:
                line = trial
    return n


def check_fit(label, paras, w, h, after=0, face=BODY):
    used = sum(_lines(t, s, b, face, w * 72) * s * 1.2 + after for t, s, b in paras)
    if used > h * 72 + 1:
        FIT_WARNINGS.append(f"{label}: needs {used / 72:.2f}in, box is {h:.2f}in")


# ---------------------------------------------------------------- helpers
def new_slide(dark=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NIGHT if dark else WHITE
    return s


def text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, after=4, label="", italic=False, bullets=False, face=BODY, bullet_color=BLUE):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    fit = []
    paras = [q for p in paras for q in (p.split(NL) if isinstance(p, str) else [p])]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.space_after = Pt(after)
        runs = [(p, {})] if isinstance(p, str) else list(p)
        if bullets:
            runs = [("•  ", {"color": bullet_color, "bold": True})] + runs
        full, psize, pbold = "", size, bold
        for t, o in runs:
            r = para.add_run()
            r.text = t
            r.font.name = o.get("face", face)
            r.font.size = Pt(o.get("size", size))
            r.font.bold = o.get("bold", bold)
            r.font.italic = o.get("italic", italic)
            r.font.color.rgb = o.get("color", color)
            full += t
            psize = max(psize, o.get("size", size))
            pbold = pbold or o.get("bold", bold)
        fit.append((full, psize, pbold))
    check_fit(label or (fit[0][0][:30] if fit else "text"), fit, w, h, after=after, face=face)
    return tb


def shape(slide, kind, x, y, w, h, fill=TINT, line=None, radius=None, lw=1.5):
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius is not None:
        shp.adjustments[0] = radius
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def panel(slide, x, y, w, h, fill=TINT, **kw):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, radius=0.06, **kw)


def label_in(shp, txt, size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER, face=BODY):
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, line in enumerate(txt.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = face, Pt(size), bold, color
    w = shp.width / 914400 - 0.16
    check_fit("in-shape " + txt[:20], [(l, size, bold) for l in txt.split("\n")], w, shp.height / 914400, face=face)
    return shp


def picture(slide, path, x, y, w=None, h=None, border=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)
    if border:
        pic.line.color.rgb = border
        pic.line.width = Pt(3)
    return pic


def fit_picture(slide, path, x, y, max_w, max_h, center=True):
    """Largest size that fits the box, keeping the aspect ratio."""
    iw, ih = Image.open(path).size
    scale = min(max_w / iw, max_h / ih)
    w, h = iw * scale, ih * scale
    if center:
        x += (max_w - w) / 2
    return picture(slide, path, x, y, w=w, h=h)


CHAIN = ["Data", "Min. prep", "Baseline", "Improve", "Models", "Evaluate"]


def header(slide, section, title, num, chain=None):
    """Section tag + full-sentence takeaway title + page number + workflow tracker."""
    tag_w = 0.45 + 0.1 * len(section)
    tag = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 0.6, 0.38, tag_w, 0.36, fill=NIGHT, radius=0.5)
    label_in(tag, section.upper(), size=11)
    if chain:
        widths = [0.34 + 0.075 * len(c) for c in CHAIN]
        x = 12.73 - sum(widths) - 0.2 * (len(CHAIN) - 1)
        for c, w in zip(CHAIN, widths):
            on = c == chain
            p = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, 0.4, w, 0.32, fill=BLUE if on else TINT, radius=0.5)
            label_in(p, c, size=10, color=WHITE if on else MUTED, bold=on)
            if c != CHAIN[-1]:
                text(slide, x + w + 0.02, 0.4, 0.16, 0.32, ["›"], size=12, color=GRAY, bold=True,
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="chev")
            x += w + 0.2
    text(slide, 0.6, 0.88, 12.1, 0.95, [title], size=26, bold=True, color=INK, face=HEAD, label="title:" + title)
    c = shape(slide, MSO_SHAPE.OVAL, 12.38, 6.95, 0.36, 0.36, fill=TINT)
    label_in(c, str(num), size=10, color=BLUE)


def notes(slide, n):
    lines = [f"[{spk.upper()}, slide {n}: {C.SLIDE_NAMES[n]}]" for spk, _, rng, _ in C.SPEAKERS if n in rng]
    lines += C.SAY[n]
    if n in C.HANDOFF:
        lines.append(f"(Hand off: \"{C.HANDOFF[n]}\")")
    slide.notes_slide.notes_text_frame.text = "\n".join(lines)


def style_chart(chart, size=12):
    chart.font.name = BODY
    chart.font.size = Pt(size)
    chart.font.color.rgb = INK


def show_every_label(chart):
    ax = chart.category_axis._element
    for old in ax.findall(qn("c:tickLblSkip")):
        ax.remove(old)
    skip = ax.makeelement(qn("c:tickLblSkip"), {"val": "1"})
    anchor = ax.find(qn("c:noMultiLvlLbl"))
    if anchor is not None:
        anchor.addprevious(skip)
    else:
        ax.append(skip)


def bar_chart(slide, x, y, w, h, cats, vals, colors, fmt="0", horizontal=True, size=12, axis_max=None, gap=55):
    # one series per color (others blank) + overlap 100 so PowerPoint Online draws the intended colors
    groups = []
    for c in colors:
        if str(c) not in [str(g) for g in groups]:
            groups.append(c)
    cd = CategoryChartData()
    cd.categories = cats
    for gi, g in enumerate(groups):
        cd.add_series(f"group {gi + 1}", [v if str(c) == str(g) else None for v, c in zip(vals, colors)])
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    chart = slide.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    style_chart(chart, size)
    chart.has_title = False
    chart.has_legend = False
    plot = chart.plots[0]
    plot.gap_width = gap
    plot.overlap = 100
    plot.vary_by_categories = False
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(size)
    dl.font.bold = True
    dl.font.color.rgb = INK
    for ser, g in zip(plot.series, groups):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = g
        ser.invert_if_negative = False
    show_every_label(chart)
    va = chart.value_axis
    va.has_major_gridlines = False
    va.visible = False
    va.minimum_scale = 0
    if axis_max:
        va.maximum_scale = axis_max
    ca = chart.category_axis
    ca.tick_labels.font.size = Pt(size)
    ca.format.line.color.rgb = GRAY
    if horizontal:
        ca.reverse_order = True
    return chart


def cluster_chart(slide, x, y, w, h, cats, series, fmt="0.00", size=12, axis_max=1.1):
    cd = CategoryChartData()
    cd.categories = cats
    for name, vals, _ in series:
        cd.add_series(name, vals)
    chart = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    style_chart(chart, size)
    chart.has_title = False
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    plot = chart.plots[0]
    plot.gap_width = 60
    plot.overlap = -10
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(size - 1)
    for ser, (_, _, col) in zip(plot.series, series):
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = col
    show_every_label(chart)
    va = chart.value_axis
    va.has_major_gridlines = False
    va.visible = False
    va.minimum_scale, va.maximum_scale = 0, axis_max
    ca = chart.category_axis
    ca.reverse_order = True
    ca.format.line.color.rgb = GRAY
    return chart


def table(slide, x, y, rows, col_w, row_h=0.42, size=13, highlight=None, header_fill=NIGHT, fills=None, bold_first=True):
    t = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                               Inches(sum(col_w)), Inches(row_h * len(rows))).table
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            fg = INK
            if i == 0:
                cell.fill.fore_color.rgb = header_fill
                fg = WHITE
            elif fills and (i, j) in fills:
                cell.fill.fore_color.rgb, fg = fills[(i, j)]
            elif highlight is not None and i == highlight:
                cell.fill.fore_color.rgb = TINT
            else:
                cell.fill.fore_color.rgb = WHITE if i % 2 else RGBColor(0xF5, 0xF7, 0xF9)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            r = p.add_run()
            r.text = str(val)
            r.font.name, r.font.size, r.font.color.rgb = BODY, Pt(size), fg
            r.font.bold = i == 0 or (bold_first and j == 0) or (highlight is not None and i == highlight)
            check_fit(f"table r{i}c{j} {str(val)[:15]}", [(str(val), size, r.font.bold)], col_w[j] - 0.16, row_h, after=0)
    return t


# ---------------------------------------------------------------- thumbnails (CC0 dataset photos)
PICKS = {"Northern Cardinal": 5, "Green Jay": 1, "Roadrunner": 5, "Red Tailed Hawk": 3, "Red Shouldered Hawk": 4,
         "Crow": 4, "Common Grackle": 3, "Northern Mockingbird": 3, "Mourning Dove": 3, "Rock Dove": 3}
THUMB = {}
for sp, k in PICKS.items():
    src = DF[(DF.species == sp) & (DF.split == "train")].path.iloc[k].replace("../", "")
    out = THUMBS / (sp.lower().replace(" ", "_") + ".jpg")
    Image.open(src).convert("RGB").save(out, quality=92)
    THUMB[sp] = out

V, T = R["validation"], R["test"]
STEPS = ["0. Majority guess", "1. Baseline CNN", "2. CNN + augmentation", "3. MobileNetV2 frozen",
         "3b. MobileNetV2 frozen, no augmentation", "4. Fine-tuned (default)", "5. Fine-tuned (tuned)"]
FINAL = R["final_model"]
f2 = lambda v: f"{v:.2f}"
f3 = lambda v: f"{v:.3f}"
counts = DF.species.value_counts()
sky = DF.groupby("species").sky_border.mean()

# ======================================================================= MATEEN 1-7
# 1 Title
s = new_slide(dark=True)
text(s, 0.8, 0.8, 7.0, 0.4, ["DATA 4380  ·  DATA PROBLEMS  ·  COMPUTER VISION PROJECT"], size=13, bold=True, color=SKY)
text(s, 0.8, 1.45, 6.8, 2.1, ["Which Texas Bird Is It?"], size=52, bold=True, color=WHITE, face=HEAD, label="title big")
text(s, 0.8, 3.65, 6.6, 1.0, ["Classifying 10 species from a single photo with convolutional neural networks"],
     size=22, color=SKY, face=HEAD, label="subtitle")
text(s, 0.8, 5.5, 6.8, 1.2, [[("Mateen Jan  ·  Tej Govindu  ·  Alejandro Alfonso", {"bold": True, "color": WHITE})],
                             "Instructor: Dr. Masoud Rostami  ·  UT Arlington  ·  November 18, 2026"], size=15, color=SKY, after=6)
for i, sp in enumerate(["Northern Cardinal", "Green Jay", "Roadrunner", "Red Tailed Hawk"]):
    px_, py_ = 8.3 + (i % 2) * 2.3, 1.0 + (i // 2) * 2.75
    picture(s, THUMB[sp], px_, py_, w=2.1, h=2.1, border=WHITE)
    text(s, px_, py_ + 2.17, 2.1, 0.35, [sp.replace("Red Tailed", "Red-tailed")], size=12, color=SKY, italic=True,
         align=PP_ALIGN.CENTER, label="cap " + sp)
notes(s, 1)

# 2 Background
s = new_slide()
header(s, "Background", "Some Texas birds are easy to tell apart; others fool even people", 2)
pairs2 = [("Easy", "Northern Cardinal", "Roadrunner", BLUE, TINT), ("Hard", "Red Tailed Hawk", "Red Shouldered Hawk", RED, ROSE)]
for r, (lab, a, b, col, fill) in enumerate(pairs2):
    y0 = 1.95 + r * 2.45
    panel(s, 0.6, y0, 6.0, 2.25, fill=fill)
    text(s, 0.8, y0 + 0.12, 1.1, 0.4, [lab.upper()], size=13, bold=True, color=col)
    for k, sp in enumerate((a, b)):
        picture(s, THUMB[sp], 1.35 + k * 2.75, y0 + 0.15, w=1.6, h=1.6)
        text(s, 1.15 + k * 2.75, y0 + 1.8, 2.0, 0.35, [sp.replace("Red Tailed", "Red-tailed").replace("Red Shouldered", "Red-shouldered")],
             size=12, italic=True, color=MUTED, align=PP_ALIGN.CENTER, label="cap2 " + sp)
    text(s, 2.95, y0 + 0.45, 1.15, 1.0, ["vs."], size=26, bold=True, color=col, face=HEAD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="vs")
boxes = [("The problem", "Given one photo, name the species, including birds that look nearly alike."),
         ("Why it matters", "Bird-ID apps and citizen science (eBird, iNaturalist) turn photos into data ecologists use. A wrong ID is a bad record."),
         ("Who benefits", "Beginner birders and students, citizen-science projects, researchers sorting large photo sets."),
         ("Why we chose it", "Visual and fun, uses this unit's CNNs and transfer learning, and lookalikes make it a real challenge.")]
for i, (h_, b_) in enumerate(boxes):
    y0 = 1.95 + i * 1.22
    shape(s, MSO_SHAPE.RECTANGLE, 6.95, y0, 0.08, 1.05, fill=RED if i == 0 else BLUE)
    text(s, 7.2, y0, 5.5, 0.35, [h_], size=16, bold=True, color=INK, face=HEAD, label="bh " + h_)
    text(s, 7.2, y0 + 0.36, 5.5, 0.75, [b_], size=14, color=INK, label="bb " + h_)
notes(s, 2)

# 3 Previous work
s = new_slide()
header(s, "Previous work", "Earlier work told us to use a pretrained model, and to check what it looks at", 3)
rows = [["", "Merlin Photo ID\n(Cornell Lab)", "CUB-200-2011\n(Wah et al., 2011)", "BIRDS 525 projects\n(e.g., EfficientNet-B2)", "Shortcut learning\n(Geirhos et al., 2020)"],
        ["What / data", "Bird-ID app; millions of eBird photos", "Benchmark: 200 lookalike species, 11,788 photos", "Our dataset, all 525 species", "Review of models that 'cheat'"],
        ["Method", "Deep CNN + location and date", "Original baselines, later deep CNNs", "Fine-tuned ImageNet model", "Wolf vs. husky model used snow"],
        ["Found", "Right bird in top 3 ~90% of the time", "Baselines only 10–17%; fine-grained is hard", "~99% on clean, centered photos", "High scores can come from background"],
        ["How ours compares", "Same task, 10 species, photo only", "Same lookalike problem, smaller scale", "Smaller, faster MobileNetV2", "We check with Grad-CAM heatmaps"]]
t = table(s, 0.6, 1.95, rows, col_w=[1.85, 2.57, 2.57, 2.57, 2.57], row_h=0.9, size=14)
for j in range(1, 5):
    c = t.cell(4, j)
    c.fill.solid()
    c.fill.fore_color.rgb = SAND
text(s, 0.6, 6.55, 12.1, 0.35, ["Sources: Cornell Lab of Ornithology (n.d.); Wah et al. (2011); Piosenka (2023); Geirhos et al. (2020); Ribeiro et al. (2016). Full list on slide 20."],
     size=11, color=MUTED, italic=True, label="src3")
notes(s, 3)

# 4 Problem & objectives
s = new_slide()
header(s, "Problem statement", "Our question: can a CNN name the bird, even when species look alike?", 4)
q = panel(s, 0.6, 1.95, 12.13, 0.95, fill=NIGHT)
label_in(q, "\"Can a convolutional neural network identify 10 common Texas bird species from a single photo,\nand does it struggle most with birds that look alike?\"",
         size=18, bold=False, face=HEAD)
chips = [("Target", "Species (10 classes)"), ("Task", "Multi-class classification"),
         ("Unit", "One photo, 224 × 224"), ("Main metric", "Macro F1")]
x = 0.6
for k, v in chips:
    panel(s, x, 3.1, 2.95, 0.95, fill=TINT)
    text(s, x + 0.2, 3.18, 2.6, 0.3, [k.upper()], size=11, bold=True, color=BLUE)
    text(s, x + 0.2, 3.5, 2.65, 0.5, [v], size=16, bold=True, label="chip " + k)
    x += 3.06
objs = ["Build a baseline before improving anything", "Improve one step at a time; report what each step does, even if it doesn't help",
        "Evaluate the final model once, on held-out test photos", "Find where mistakes happen and what the model looks at"]
for i, o in enumerate(objs):
    cx = 0.6 + i * 3.06
    c = shape(s, MSO_SHAPE.OVAL, cx, 4.35, 0.6, 0.6, fill=BLUE)
    label_in(c, str(i + 1), size=16, face=HEAD)
    text(s, cx + 0.72, 4.3, 2.2, 1.25, [o], size=14, label="obj" + str(i))
panel(s, 0.6, 5.85, 12.13, 0.75, fill=SAND)
text(s, 0.85, 5.85, 11.7, 0.75, [[("Success means: ", {"bold": True, "color": BROWN}),
                                  ("clearly beating the baseline, and being able to explain the mistakes the model still makes.", {})]],
     size=16, anchor=MSO_ANCHOR.MIDDLE, label="success")
notes(s, 4)

# 5 Dataset
s = new_slide()
header(s, "Data understanding", "1,710 photos of 10 species: clean, balanced, nothing missing", 5, chain="Data")
order = counts.sort_values(ascending=False)
bar_chart(s, 0.5, 1.95, 6.6, 4.75, [c for c in order.index], [int(v) for v in order.values], [BLUE] * len(order),
          fmt="0", size=12, axis_max=260, gap=40)
text(s, 0.6, 6.68, 6.4, 0.3, ["Photos per species (all splits). Largest ÷ smallest = 1.49"], size=11, color=MUTED, italic=True, label="cap5")
facts = [("Source", "BIRDS 525 (Piosenka), CC0 public domain; Hugging Face mirror"),
         ("Rows", "1,710 photos (one row = one photo)"),
         ("Features", "Pixels: 224 × 224 × 3 colors ≈ 150,000 numbers, all numeric"),
         ("Target", "Species label, 10 classes"),
         ("Missing", "None: every file opened, every photo labeled")]
y0 = 1.95
for k, v in facts:
    text(s, 7.4, y0, 1.3, 0.55, [k.upper()], size=11, bold=True, color=BLUE, label="fk " + k)
    text(s, 8.65, y0, 4.1, 0.55, [v], size=14, label="fv " + k)
    y0 += 0.58
panel(s, 7.4, 4.95, 5.33, 1.75, fill=SAND)
text(s, 7.6, 5.03, 5.0, 0.35, ["Quality checks"], size=15, bold=True, color=BROWN, face=HEAD)
text(s, 7.6, 5.42, 5.0, 1.25, ["0 broken files · 0 exact duplicates",
                               "22 outliers (1.3%): very dark, bright or high-contrast. Inspected: real photos (night sky, snow), so kept"],
     size=13, bullets=True, bullet_color=BROWN, label="qc")
notes(s, 5)

# 6 EDA
s = new_slide()
header(s, "EDA", "Two findings shaped our plan: lookalike pairs, and hawks shot against sky", 6, chain="Data")
fit_picture(s, FIG / "lookalike_pairs.png", 0.6, 1.9, 6.6, 3.6, center=False)
text(s, 0.6, 5.55, 6.5, 0.6, [[("Expected: ", {"bold": True, "color": RED}),
                               ("most mistakes will fall inside these three pairs.", {})]], size=14, label="exp6")
sk = sky.sort_values(ascending=False)
bar_chart(s, 7.4, 2.25, 5.4, 3.75, [c for c in sk.index], [float(v) for v in sk.values],
          [RED if "Hawk" in c else SKY for c in sk.index], fmt="0%", size=11, axis_max=0.42, gap=40)
text(s, 7.5, 1.9, 5.3, 0.35, ["Share of photo border that is blue sky"], size=13, bold=True, color=MUTED, label="skyt")
panel(s, 7.4, 6.05, 5.33, 0.75, fill=ROSE)
text(s, 7.6, 6.05, 5.0, 0.75, [[("Surprise: ", {"bold": True, "color": RED}),
                               ("hawks ≈ ⅓ sky. Risk of learning \"sky = hawk\" → we check with Grad-CAM later.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="surp")
panel(s, 0.6, 6.2, 6.5, 0.6, fill=SAND)
text(s, 0.8, 6.2, 6.2, 0.6, [[("Expected but didn't find: ", {"bold": True, "color": BROWN}),
                              ("duplicates or broken files in web-collected data.", {})]], size=13, anchor=MSO_ANCHOR.MIDDLE, label="nofind")
notes(s, 6)

# 7 Minimum preprocessing
s = new_slide()
header(s, "Minimum preprocessing", "Before the baseline, only what it couldn't run without", 7, chain="Min. prep")
steps7 = [("Quality checks", "broken, duplicate,\noutlier photos"), ("Stratified split", "70 / 15 / 15,\nseed 42"),
          ("Resize", "128 px for the\nfrom-scratch CNN"), ("Scale pixels", "0–255 → 0–1")]
x = 0.6
for i, (h_, sub) in enumerate(steps7):
    kind = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
    c = shape(s, kind, x, 1.95, 3.15, 0.95, fill=BLUE)
    label_in(c, h_, size=16)
    text(s, x + 0.35, 2.98, 2.6, 0.6, [sub], size=13, color=MUTED, italic=True, label="s7 " + h_)
    x += 3.0
tot = 1710
segs = [("Train", 1197, BLUE, "teaches the model"), ("Validation", 256, SKY, "chooses between models"), ("Test", 257, NIGHT, "used once, at the end")]
x, W = 0.6, 7.2
text(s, 0.6, 3.85, 7.2, 0.35, ["Our split (the original test set had only 5 photos per species)"], size=14, bold=True, label="splt")
for name, n, col, role in segs:
    w = W * n / tot
    b = shape(s, MSO_SHAPE.RECTANGLE, x, 4.3, w, 0.8, fill=col)
    label_in(b, f"{name}\n{n:,}" if w > 1.2 else f"{n}", size=14, color=WHITE if col != SKY else INK)
    x += w
for i, (name, n, col, role) in enumerate(segs):
    lx = 0.6 + i * 2.45
    shape(s, MSO_SHAPE.RECTANGLE, lx, 5.27, 0.22, 0.22, fill=col)
    text(s, lx + 0.32, 5.2, 2.1, 0.55, [[(name + ": ", {"bold": True}), (role, {})]], size=12, color=INK, label="role " + name)
text(s, 0.6, 5.85, 7.2, 0.9, ["Stratified: every species keeps the same share in each split (~25 test photos per bird). No photo appears in two splits."],
     size=13, label="strat")
panel(s, 8.15, 3.85, 4.58, 2.9, fill=SAND)
text(s, 8.35, 3.95, 4.2, 0.35, ["Held back for later (slides 9–10)"], size=15, bold=True, color=BROWN, face=HEAD, label="hb")
text(s, 8.35, 4.4, 4.2, 2.3, ["Data augmentation", "Full 224 px + ImageNet pixel scaling (−1…1)", "Pretrained features",
                              ], size=14, bullets=True, bullet_color=BROWN, label="hbl")
text(s, 8.35, 5.85, 4.2, 0.8, ["So each step's effect can be measured on its own."], size=13, italic=True, color=MUTED, label="hbl2")
notes(s, 7)

# ======================================================================= TEJ 8-13
# 8 Baseline
s = new_slide()
header(s, "Baseline", "Our baseline CNN gets 61%: far above guessing, but 4 in 10 birds wrong", 8, chain="Baseline")
blocks = [("Photo", "128×128×3"), ("Conv 32", "+ pool"), ("Conv 64", "+ pool"), ("Conv 128", "+ pool"), ("Conv 128", "+ pool"),
          ("Avg + dropout", "30%"), ("Softmax", "10 birds")]
x = 0.6
for i, (a, b) in enumerate(blocks):
    col = NIGHT if i in (0, 6) else BLUE
    c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 2.0, 1.5, 1.0, fill=col, radius=0.12)
    label_in(c, f"{a}\n{b}", size=13)
    if i < len(blocks) - 1:
        text(s, x + 1.5, 2.0, 0.27, 1.0, ["→"], size=18, bold=True, color=GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="arr")
    x += 1.77
text(s, 0.6, 3.1, 12.1, 0.4, ["Simple CNN: filters find edges → textures → beaks and wings; pooling shrinks the image between blocks. 242,122 weights, trained from scratch."],
     size=13, color=MUTED, italic=True, label="cnncap")
cards = [("Majority guess", "always \"Red-tailed Hawk\"", V["0. Majority guess"]["F1"], GRAY, "12.5% accuracy"),
         ("Baseline CNN", "minimum preprocessing only", V["1. Baseline CNN"]["F1"], BROWN, "60.9% accuracy")]
for i, (h_, sub, val, col, acc) in enumerate(cards):
    x0 = 0.6 + i * 3.4
    panel(s, x0, 3.75, 3.2, 2.95, fill=SAND if i else RGBColor(0xF1, 0xF3, 0xF5))
    text(s, x0 + 0.2, 3.85, 2.9, 0.35, [h_], size=16, bold=True, face=HEAD, label="c8 " + h_)
    text(s, x0 + 0.2, 4.22, 2.9, 0.35, [sub], size=12, italic=True, color=MUTED, label="c8s " + h_)
    text(s, x0 + 0.2, 4.6, 2.9, 1.0, [f2(val)], size=48, bold=True, color=col, face=HEAD, label="c8v " + h_)
    text(s, x0 + 0.2, 5.65, 2.9, 0.9, ["validation macro F1", acc], size=13, color=MUTED, label="c8a " + h_)
panel(s, 7.55, 3.75, 5.18, 2.95, fill=TINT)
text(s, 7.75, 3.85, 4.8, 0.35, ["Why macro F1?"], size=16, bold=True, color=BLUE, face=HEAD)
text(s, 7.75, 4.3, 4.8, 2.35, ["F1 balances precision and recall for each species", "Macro = average over all 10 species equally",
                               "A model can't score well by ignoring one bird",
                               "CNN assumes: nearby pixels are related; a pattern means the same anywhere"],
     size=14, bullets=True, label="why8")
notes(s, 8)

# 9 Augmentation
s = new_slide()
header(s, "Additional preprocessing", "Data augmentation did not help, for either model", 9, chain="Improve")
fit_picture(s, FIG / "augmentation_examples.png", 0.6, 1.9, 12.1, 2.25)
text(s, 0.6, 4.2, 12.1, 0.35, ["Training photos only: random flip · rotation ±36° · zoom ±10% · contrast ±20%. Validation and test photos are never changed."],
     size=13, color=MUTED, italic=True, align=PP_ALIGN.CENTER, label="augcap")
res9 = [("Simple CNN", V["1. Baseline CNN"]["F1"], V["2. CNN + augmentation"]["F1"]),
        ("MobileNetV2 (slide 10)", V["3b. MobileNetV2 frozen, no augmentation"]["F1"], V["3. MobileNetV2 frozen"]["F1"])]
for i, (h_, without, with_) in enumerate(res9):
    x0 = 0.6 + i * 4.25
    panel(s, x0, 4.75, 4.05, 1.95, fill=ROSE)
    text(s, x0 + 0.2, 4.83, 3.7, 0.35, [h_], size=15, bold=True, face=HEAD, label="r9 " + h_)
    text(s, x0 + 0.2, 5.25, 1.7, 0.35, ["without"], size=12, color=MUTED, label="wo")
    text(s, x0 + 2.05, 5.25, 1.7, 0.35, ["with augmentation"], size=12, color=MUTED, label="wi")
    text(s, x0 + 0.2, 5.6, 1.7, 0.8, [f3(without)], size=34, bold=True, color=BLUE, face=HEAD, label="wov")
    text(s, x0 + 2.05, 5.6, 1.8, 0.8, [f3(with_)], size=34, bold=True, color=RED, face=HEAD, label="wiv")
text(s, 0.6, 6.72, 8.2, 0.3, ["Validation macro F1"], size=11, color=MUTED, italic=True, label="v9")
panel(s, 9.15, 4.75, 3.58, 1.95, fill=SAND)
text(s, 9.35, 4.83, 3.2, 1.85, [[("Why? ", {"bold": True, "color": BROWN}),
                                ("~120 photos per bird; random changes make learning from scratch harder. Photos are already clean and centered.", {})]],
     size=13, label="why9")
notes(s, 9)

# 10 Transfer learning as feature engineering
s = new_slide()
header(s, "Feature engineering", "Swapping in pretrained features took F1 from 0.61 to 0.96", 10, chain="Improve")
lanes = [("From scratch (baseline)", ["~1,200 of our photos", "learn features\nfrom scratch", "242,122 weights\ntrained"], V["1. Baseline CNN"]["F1"], BROWN, SAND),
         ("Transfer learning", ["~1.3 million\nImageNet photos", "MobileNetV2 features\n(frozen)", "new 10-bird layer:\n12,810 weights trained"],
          V["3b. MobileNetV2 frozen, no augmentation"]["F1"], BLUE, TINT)]
for r, (name, boxes_, val, col, fill) in enumerate(lanes):
    y0 = 2.0 + r * 2.05
    panel(s, 0.6, y0, 12.13, 1.8, fill=fill)
    text(s, 0.8, y0 + 0.1, 3.0, 0.35, [name], size=15, bold=True, color=col, face=HEAD, label="lane " + name)
    x = 0.8
    for i, b in enumerate(boxes_):
        c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y0 + 0.55, 2.55, 1.05, fill=WHITE, line=col, radius=0.12, lw=1.25)
        label_in(c, b, size=13, color=INK, bold=False)
        text(s, x + 2.55, y0 + 0.55, 0.4, 1.05, ["→"], size=20, bold=True, color=col, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="a10")
        x += 2.95
    text(s, 9.75, y0 + 0.3, 2.8, 0.9, [f2(val)], size=44, bold=True, color=col, face=HEAD, align=PP_ALIGN.CENTER, label="v10")
    text(s, 9.75, y0 + 1.2, 2.8, 0.35, ["validation macro F1"], size=12, color=MUTED, align=PP_ALIGN.CENTER, label="v10c")
text(s, 0.6, 6.2, 12.1, 0.7, ["Images have no hand-made columns: the CNN learns its own features. Our feature decision was where they come from. Same photos, split and metric; only the features changed."],
     size=14, color=INK, label="fe10")
notes(s, 10)

# 11 Model selection
s = new_slide()
header(s, "Model selection", "Two model families, each with a clear reason to be there", 11, chain="Models")
rows = [["", "Why we chose it", "Strengths", "Limitations", "Preprocessing"],
        ["Simple CNN", "Standard first model for images; honest baseline", "Transparent; small; trains from scratch", "Needs far more data than ~120 photos/bird", "128 px, pixels 0–1"],
        ["MobileNetV2, frozen", "Small, fast pretrained CNN built for phones", "Strong features from little data; ~4 min on a laptop", "Assumes ImageNet features transfer; inherits its biases", "224 px, pixels −1…1"],
        ["MobileNetV2, fine-tuned", "Let top layers adapt to our 10 birds", "More flexible", "1.5M trainable weights → overfits small data", "Same, very small learning rate"]]
table(s, 0.6, 1.95, rows, col_w=[2.25, 2.55, 2.55, 2.75, 2.03], row_h=0.95, size=14)
panel(s, 0.6, 5.95, 12.13, 0.8, fill=SAND)
text(s, 0.85, 5.95, 11.7, 0.8, [[("Why not logistic regression or random forest? ", {"bold": True, "color": BROWN}),
                                 ("On raw pixels they treat 49,152 pixels as unrelated columns and ignore the image's 2-D structure.", {})]],
     size=14, anchor=MSO_ANCHOR.MIDDLE, label="whynot")
notes(s, 11)

# 12 Model improvement ladder
s = new_slide()
header(s, "Model improvement", "Every step changes one thing; only transfer learning moved the needle", 12, chain="Improve")
lab12 = ["Majority\nguess", "Baseline\nCNN", "CNN +\naugmentation", "MobileNetV2\n+ augmentation", "MobileNetV2\n(no aug.) FINAL", "Fine-tuned\n(default)", "Fine-tuned\n(tuned)"]
cols12 = [GRAY, BROWN, RED, SKY, BLUE, SKY, SKY]
bar_chart(s, 0.5, 1.9, 8.4, 4.9, lab12, [float(V[k]["F1"]) for k in STEPS], cols12, fmt="0.000", horizontal=False,
          size=12, axis_max=1.1, gap=45)
text(s, 0.6, 6.78, 8.2, 0.3, ["Validation macro F1 · dark blue = final model · red = a step that made things worse"], size=11, color=MUTED, italic=True, label="cap12")
call = [("Helped", "Pretrained MobileNetV2 features: 0.608 → 0.956", BLUE, TINT),
        ("Didn't help", "Augmentation (both models) and fine-tuning", RED, ROSE),
        ("Surprise", "Fine-tuning stopped after ~4 epochs: validation loss rose right away. 1.5M weights + 1,200 photos = memorizing", BROWN, SAND)]
y0 = 1.95
for h_, b_, col, fill in call:
    hh = 1.55 if h_ == "Surprise" else 1.25
    panel(s, 9.15, y0, 3.58, hh, fill=fill)
    text(s, 9.35, y0 + 0.08, 3.2, 0.35, [h_], size=15, bold=True, color=col, face=HEAD, label="ch " + h_)
    text(s, 9.35, y0 + 0.45, 3.2, hh - 0.5, [b_], size=13, label="cb " + h_)
    y0 += hh + 0.2
notes(s, 12)

# 13 Tuning
s = new_slide()
header(s, "Hyperparameter tuning", "Tuning on validation picked the default settings: no gain", 13, chain="Models")
grid = {(g["unfrozen layers"], g["learning rate"]): g["val F1"] for g in R["tuning_grid"]}
best = max(grid.values())
text(s, 0.6, 1.95, 6.0, 0.4, ["Grid search: 2 × 2 = 4 runs, validation macro F1"], size=15, bold=True, label="g13")
text(s, 2.35, 2.45, 4.4, 0.35, ["Learning rate"], size=13, color=MUTED, align=PP_ALIGN.CENTER, label="lr")
for j, lr in enumerate(["1e-05", "3e-05"]):
    text(s, 2.35 + j * 2.2, 2.8, 2.1, 0.35, [lr.replace("e-05", "e-5")], size=14, bold=True, align=PP_ALIGN.CENTER, label="lrv")
for i, nl in enumerate([30, 60]):
    text(s, 0.6, 3.25 + i * 1.35, 1.65, 1.2, [f"Top {nl}\nlayers"], size=14, bold=True, anchor=MSO_ANCHOR.MIDDLE, label="nl")
    for j, lr in enumerate(["1e-05", "3e-05"]):
        v = grid[(nl, lr)]
        isbest = abs(v - best) < 1e-9
        c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 2.35 + j * 2.2, 3.25 + i * 1.35, 2.1, 1.2,
                  fill=BLUE if isbest else (TINT if lr == "1e-05" else ROSE), radius=0.08)
        label_in(c, f"{v:.3f}" + ("\nbest = default" if isbest else ""), size=20 if not isbest else 18,
                 color=WHITE if isbest else INK, face=HEAD)
text(s, 0.6, 5.95, 6.0, 0.8, ["Each run starts from the same frozen model and is scored on validation only. The test set never chose anything."],
     size=13, color=MUTED, italic=True, label="fair13")
why13 = [("Unfrozen layers (30 vs. 60)", "More layers = more flexibility, but more risk of overfitting ~1,200 photos"),
         ("Learning rate (1e-5 vs. 3e-5)", "Too high wrecks the pretrained weights; too low barely changes them")]
y0 = 1.95
for h_, b_ in why13:
    panel(s, 7.2, y0, 5.53, 1.15, fill=TINT)
    text(s, 7.4, y0 + 0.08, 5.1, 0.35, [h_], size=15, bold=True, color=BLUE, face=HEAD, label="w13 " + h_)
    text(s, 7.4, y0 + 0.45, 5.1, 0.65, [b_], size=13, label="w13b " + h_)
    y0 += 1.3
panel(s, 7.2, 4.65, 5.53, 2.1, fill=SAND)
text(s, 7.4, 4.73, 5.1, 0.35, ["Before vs. after tuning"], size=15, bold=True, color=BROWN, face=HEAD)
text(s, 7.4, 5.15, 5.1, 1.55, [f"Default (30 layers, 1e-5): {grid[(30, '1e-05')]:.3f}",
                              f"Best of grid: {best:.3f}, the same setting",
                              "Higher learning rate hurt: 0.931–0.939",
                              f"Still below the frozen model ({V['3b. MobileNetV2 frozen, no augmentation']['F1']:.3f})"],
     size=13, bullets=True, bullet_color=BROWN, label="ba13")
notes(s, 13)

# ======================================================================= ALEJANDRO 14-21
# 14 Comparison
s = new_slide()
header(s, "Evaluation", "On 257 unseen test photos, the final model is right 96% of the time", 14, chain="Evaluate")
names14 = {"0. Majority guess": "Majority guess", "1. Baseline CNN": "Baseline CNN", "2. CNN + augmentation": "CNN + augmentation",
           "3. MobileNetV2 frozen": "MobileNetV2 + augmentation", "3b. MobileNetV2 frozen, no augmentation": "MobileNetV2, no aug. (FINAL)",
           "4. Fine-tuned (default)": "Fine-tuned (default)", "5. Fine-tuned (tuned)": "Fine-tuned (tuned)"}
rows = [["Model (test set)", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "Val. F1"]]
for k in STEPS:
    m = T[k]
    rows.append([names14[k], f"{m['accuracy']:.1%}", f3(m["precision"]), f3(m["recall"]), f3(m["F1"]), f3(m["ROC-AUC"]), f3(V[k]["F1"])])
hl = STEPS.index(FINAL) + 1
fills = {(2, j): (SAND, INK) for j in range(7)}
table(s, 0.6, 1.95, rows, col_w=[3.3, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35], row_h=0.5, size=14, highlight=hl, fills=fills)
text(s, 0.6, 6.0, 7.9, 0.3, ["Precision, recall, F1, ROC-AUC = macro averages over the 10 species. Baseline row shaded."], size=11, color=MUTED, italic=True, label="cap14")
panel(s, 0.6, 6.32, 12.13, 0.6, fill=TINT)
text(s, 0.85, 6.32, 11.7, 0.6, [[("Chosen on validation, before this table: ", {"bold": True, "color": BLUE}),
                                 ("highest validation F1; ties (≤ 0.005) go to the simpler model. The final model was best and simplest.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="rule14")
notes(s, 14)

# 15 Errors
s = new_slide()
header(s, "Interpretation", "All 10 mistakes are between lookalike species, just as we expected", 15, chain="Evaluate")
fit_picture(s, FIG / "confusion_matrix.png", 0.4, 1.8, 6.1, 5.2, center=False)
er = R["errors"]
stats15 = [("10", "mistakes out of 257 test photos", RED), ("10 / 10", "inside a lookalike pair:\n5 hawks · 4 crow/grackle · 1 dove", RED),
           ("81", "baseline mistakes, 49 outside the pairs", BROWN)]
y0 = 1.95
for big, small, col in stats15:
    text(s, 6.75, y0, 1.75, 0.7, [big], size=30, bold=True, color=col, face=HEAD, label="b15")
    text(s, 8.55, y0 + 0.05, 4.2, 0.75, [small], size=13, label="s15")
    y0 += 0.82
fit_picture(s, FIG / "mistakes.png", 6.75, 4.45, 5.98, 2.0, center=False)
text(s, 6.75, 6.5, 5.98, 0.45, ["7 of 10 mistakes had confidence under 65%: the model is usually unsure when wrong."],
     size=12, italic=True, color=MUTED, label="conf15")
notes(s, 15)

# 16 Grad-CAM
s = new_slide()
header(s, "Interpretation", "The model looks at the bird, not the sky", 16, chain="Evaluate")
fit_picture(s, FIG / "gradcam.png", 0.6, 1.8, 12.13, 3.95)
gb = R["gradcam_border_share"]
panel(s, 0.6, 5.85, 7.6, 1.0, fill=TINT)
text(s, 0.8, 5.85, 7.25, 1.0, [[("Across all 257 test photos: ", {"bold": True, "color": BLUE}),
                                (f"the outer frame is 49% of each image but gets only {min(gb.values()):.0%}–{max(gb.values()):.0%} of the heatmap. "
                                 f"Hawks: {gb['Red Tailed Hawk']:.0%} and {gb['Red Shouldered Hawk']:.0%}.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="gb16")
panel(s, 8.4, 5.85, 4.33, 1.0, fill=ROSE)
text(s, 8.6, 5.85, 4.0, 1.0, [[("Exception: ", {"bold": True, "color": RED}),
                              ("the rock dove (far right) looks like a different pigeon: possible label error.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="exc16")
notes(s, 16)

# 17 Key findings
s = new_slide()
header(s, "Key findings", "Yes: a pretrained CNN names these birds, and fails only on true lookalikes", 17)
kf = [("1", "Baseline", "Simple CNN: macro F1 0.61, far above guessing (0.02), but 4 in 10 birds wrong."),
      ("2", "What helped", "Transfer learning gave essentially the whole gain (0.61 → 0.96). Augmentation and fine-tuning didn't help."),
      ("3", "Final model", "Frozen MobileNetV2: 96.1% test accuracy, macro F1 0.964."),
      ("4", "Mistakes", "All 10 errors are between lookalikes, and the model looks at the bird, not the sky.")]
for i, (n, h_, b_) in enumerate(kf):
    x0, y0 = 0.6 + (i % 2) * 6.15, 1.95 + (i // 2) * 1.85
    panel(s, x0, y0, 5.98, 1.65, fill=TINT)
    c = shape(s, MSO_SHAPE.OVAL, x0 + 0.2, y0 + 0.2, 0.55, 0.55, fill=BLUE)
    label_in(c, n, size=15, face=HEAD)
    text(s, x0 + 0.95, y0 + 0.2, 4.8, 0.4, [h_], size=16, bold=True, color=BLUE, face=HEAD, label="kf " + h_)
    text(s, x0 + 0.95, y0 + 0.62, 4.85, 1.0, [b_], size=14, label="kfb " + h_)
panel(s, 0.6, 5.75, 12.13, 1.05, fill=NIGHT)
text(s, 0.85, 5.75, 11.7, 1.05, [[("The insight: ", {"bold": True, "color": SKY}),
                                  ("with small data, reusing what a big model already learned beat everything we tuned ourselves.", {"color": WHITE})]],
     size=17, anchor=MSO_ANCHOR.MIDDLE, face=HEAD, label="insight")
notes(s, 17)

# 18 Limitations
s = new_slide()
header(s, "Limitations", "96% here does not mean 96% in a Texas backyard", 18)
lim = [("Clean, web-sourced photos", "Cropped and centered; real backyard or trail-camera photos are blurrier and farther away."),
       ("Only 10 species", "The model always picks one of the 10. Show it a penguin and it names a Texas bird."),
       ("Label noise", "A few photos look mislabeled (a 'mourning dove' with a collared dove's neck ring)."),
       ("Small test set, one split", "~25 photos per species: one photo moves a species' score by ~4 points."),
       ("Inherited bias", "MobileNetV2 brings ImageNet's biases; Grad-CAM shows where it looks, not why.")]
for i, (h_, b_) in enumerate(lim):
    y0 = 1.95 + i * 0.97
    shape(s, MSO_SHAPE.RECTANGLE, 0.6, y0, 0.08, 0.82, fill=RED)
    text(s, 0.9, y0, 3.6, 0.82, [h_], size=16, bold=True, face=HEAD, anchor=MSO_ANCHOR.MIDDLE, label="lh " + h_)
    text(s, 4.6, y0, 8.1, 0.82, [b_], size=15, anchor=MSO_ANCHOR.MIDDLE, label="lb " + h_)
notes(s, 18)

# 19 Conclusion
s = new_slide()
header(s, "Conclusion", "A small pretrained model was enough; the hard part is the lookalikes", 19)
panel(s, 0.6, 1.95, 6.2, 4.85, fill=TINT)
text(s, 0.85, 2.05, 5.8, 0.4, ["Summary"], size=17, bold=True, color=BLUE, face=HEAD)
text(s, 0.85, 2.5, 5.8, 2.0, ["Question: can a CNN tell 10 Texas birds apart from one photo?",
                              "Final model: frozen MobileNetV2, 96.1% on test vs. 68.5% for our baseline",
                              "Only mistakes: genuine lookalikes",
                              "In practice: useful for beginners and citizen science, if it says \"not sure\" when unsure"],
     size=14, bullets=True, label="sum19")
text(s, 0.85, 4.75, 5.8, 0.4, ["Future work"], size=17, bold=True, color=BLUE, face=HEAD)
text(s, 0.85, 5.2, 5.8, 1.55, ["Test on real Texas backyard photos", "More species + an \"unknown bird\" option",
                              "Add location and date, like Merlin"], size=14, bullets=True, label="fw19")
panel(s, 7.05, 1.95, 5.68, 4.85, fill=SAND)
text(s, 7.3, 2.05, 5.2, 0.4, ["What we learned"], size=17, bold=True, color=BROWN, face=HEAD)
text(s, 7.3, 2.55, 5.2, 4.2, ["Bigger isn't automatically better: the simplest transfer-learning model won.",
                              "Steps we were sure would help (augmentation, fine-tuning) didn't. Testing one change at a time is how we found out.",
                              "A high score isn't enough: we had to check what the model was looking at."],
     size=15, bullets=True, bullet_color=BROWN, after=10, label="learn19")
notes(s, 19)

# 20 References
s = new_slide()
header(s, "References", "References (APA)", 20)
refs = ["Abadi, M., et al. (2015). TensorFlow: Large-scale machine learning on heterogeneous systems. https://www.tensorflow.org",
        "Cornell Lab of Ornithology. (n.d.). Merlin Bird ID [Mobile app]. https://merlin.allaboutbirds.org",
        "Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut learning in deep neural networks. Nature Machine Intelligence, 2(11), 665–673.",
        "Piosenka, G. (2023). BIRDS 525 species – Image classification [Data set]. Kaggle. Mirror: https://huggingface.co/datasets/chriamue/bird-species-dataset (CC0 1.0).",
        "Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). \"Why should I trust you?\": Explaining the predictions of any classifier. Proceedings of ACM SIGKDD, 1135–1144.",
        "Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L.-C. (2018). MobileNetV2: Inverted residuals and linear bottlenecks. Proceedings of IEEE CVPR, 4510–4520.",
        "Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. Proceedings of IEEE ICCV, 618–626.",
        "Wah, C., Branson, S., Welinder, P., Perona, P., & Belongie, S. (2011). The Caltech-UCSD Birds-200-2011 dataset (Tech. Rep. CNS-TR-2011-001). California Institute of Technology.",
        "Our code and notebooks: https://github.com/Mateen1367/BIRDS-PROJECT"]
text(s, 0.6, 1.9, 12.1, 5.0, refs, size=12, after=7, label="refs")
notes(s, 20)

# 21 Questions
s = new_slide(dark=True)
text(s, 0.8, 1.7, 6.8, 1.2, ["Thank you"], size=54, bold=True, color=WHITE, face=HEAD, label="ty")
text(s, 0.8, 2.95, 6.8, 0.8, ["Questions?"], size=34, color=SKY, face=HEAD, label="q")
text(s, 0.8, 5.5, 6.8, 1.0, ["Mateen Jan  ·  Tej Govindu  ·  Alejandro Alfonso", "github.com/Mateen1367/BIRDS-PROJECT"],
     size=15, color=SKY, after=6, label="qnames")
for i, sp in enumerate(["Northern Mockingbird", "Common Grackle", "Mourning Dove", "Red Shouldered Hawk"]):
    px_, py_ = 8.3 + (i % 2) * 2.3, 1.0 + (i // 2) * 2.75
    picture(s, THUMB[sp], px_, py_, w=2.1, h=2.1, border=WHITE)
    text(s, px_, py_ + 2.17, 2.1, 0.35, [sp.replace("Red Shouldered", "Red-shouldered")], size=12, color=SKY, italic=True,
         align=PP_ALIGN.CENTER, label="qcap " + sp)
notes(s, 21)

# ---------------------------------------------------------------- backup slides
s = new_slide()
header(s, "Backup", "Every species improved; the hawks and black birds stay hardest", 22)
pc = R["per_class_test_f1"]
order = sorted(pc, key=lambda k: pc[k]["final F1"])
cluster_chart(s, 0.6, 1.9, 12.1, 5.0, order, [("Baseline CNN", [pc[k]["baseline F1"] for k in order], BROWN),
                                             ("Final model", [pc[k]["final F1"] for k in order], BLUE)])
s.notes_slide.notes_text_frame.text = "[BACKUP] Per-species test F1, baseline vs. final model. Use if asked which birds are hardest."

s = new_slide()
header(s, "Backup", "Training curves: the from-scratch CNNs were still learning at the epoch limit", 23)
fit_picture(s, FIG / "training_curves.png", 0.6, 1.9, 12.1, 4.9)
s.notes_slide.notes_text_frame.text = "[BACKUP] Train vs. validation accuracy per epoch. Use if asked about overfitting or why augmentation hurt."

out = "reports/WhichTexasBird_Presentation.pptx"
prs.save(out)
print("saved", out, "·", len(prs.slides), "slides")
print("\n".join(FIT_WARNINGS) if FIT_WARNINGS else "text fit: OK")
