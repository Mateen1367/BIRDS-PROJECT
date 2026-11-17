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

# ======================================================================= CV-guideline deck (17 slides + backup)
GREEN_ = RGBColor(0x2E, 0x7D, 0x4F)
CHAIN = ["Intro", "Data", "Preprocess", "Baseline", "Transfer", "Results"]
MAIN = {"Baseline CNN": "1. Baseline CNN", "MobileNetV2": "3b. MobileNetV2 frozen, no augmentation",
        "ResNet50": "3c. ResNet50 frozen, no augmentation"}
CR = R["class_reports"]
base_t, mob_t, res_t = (T[MAIN[k]] for k in ("Baseline CNN", "MobileNetV2", "ResNet50"))
nice = lambda sp: sp.replace("Red Tailed", "Red-tailed").replace("Red Shouldered", "Red-shouldered")


def report_table(slide, x, y, model, highlight_low=0.94, size=12, row_h=0.36):
    rep_ = CR[model]
    rows = [["Species", "Precision", "Recall", "F1"]]
    fills = {}
    for i, sp in enumerate(R["classes"], start=1):
        r_ = rep_[sp]
        rows.append([nice(sp), f"{r_['precision']:.2f}", f"{r_['recall']:.2f}", f"{r_['f1-score']:.2f}"])
        if r_["f1-score"] < highlight_low:
            fills[(i, 3)] = (ROSE, RED)
    ma = rep_["macro avg"]
    rows.append(["Macro average", f"{ma['precision']:.2f}", f"{ma['recall']:.2f}", f"{ma['f1-score']:.2f}"])
    t = table(slide, x, y, rows, col_w=[2.3, 1.0, 0.9, 0.85], row_h=row_h, size=size, highlight=len(rows) - 1, fills=fills)
    return t


def stat_cards(slide, x, y, cards, w=1.95, h=1.45):
    for i, (big, small_, col, fill) in enumerate(cards):
        x0 = x + i * (w + 0.15)
        panel(slide, x0, y, w, h, fill=fill)
        text(slide, x0 + 0.12, y + 0.12, w - 0.24, 0.75, [big], size=30, bold=True, color=col, face=HEAD, align=PP_ALIGN.CENTER, label="sc " + big)
        text(slide, x0 + 0.12, y + 0.88, w - 0.24, 0.5, [small_], size=12, color=MUTED, align=PP_ALIGN.CENTER, label="scs " + small_)


def results_slide(n, model, title, key, col, fill, gain_label, note):
    s = new_slide()
    header(s, "Results" if model != "Baseline CNN" else "Baseline", title, n, chain="Transfer" if model != "Baseline CNN" else "Baseline")
    text(s, 0.6, 1.9, 6.6, 0.35, [f"{model}: accuracy and loss during training"], size=14, bold=True, color=MUTED, label="ct")
    fit_picture(s, FIG / f"curves_{model.split()[0].lower()}.png", 0.6, 2.25, 6.6, 2.45, center=False)
    m_ = T[key]
    cards = [(f"{m_['accuracy']:.1%}", "test accuracy", col, fill), (f"{m_['loss']:.3f}", "test loss", col, fill), gain_label]
    stat_cards(s, 0.6, 4.85, cards)
    text(s, 0.6, 6.4, 6.6, 0.5, [note], size=12, italic=True, color=MUTED, label="note" + str(n))
    text(s, 7.45, 1.9, 5.3, 0.35, ["Classification report (test set, 257 photos)"], size=14, bold=True, color=MUTED, label="crt")
    report_table(s, 7.45, 2.3, model, highlight_low=0.6 if model == "Baseline CNN" else 0.94)
    notes(s, n)
    return s


# 1 Title -------------------------------------------------------------------------------------
s = new_slide(dark=True)
text(s, 0.8, 0.8, 7.0, 0.4, ["DATA 4380  ·  DATA PROBLEMS  ·  COMPUTER VISION PROJECT"], size=13, bold=True, color=SKY)
text(s, 0.8, 1.45, 6.8, 2.1, ["Which Texas Bird Is It?"], size=52, bold=True, color=WHITE, face=HEAD, label="title big")
text(s, 0.8, 3.65, 6.6, 1.0, ["Classifying 10 species from a single photo with CNNs and transfer learning"],
     size=22, color=SKY, face=HEAD, label="subtitle")
text(s, 0.8, 5.5, 6.8, 1.2, [[("Mateen Jan  ·  Tej Govindu  ·  Alejandro Alfonso", {"bold": True, "color": WHITE})],
                             "Instructor: Dr. Masoud Rostami  ·  UT Arlington  ·  November 18, 2026"], size=15, color=SKY, after=6)
for i, sp in enumerate(["Northern Cardinal", "Green Jay", "Roadrunner", "Red Tailed Hawk"]):
    px_, py_ = 8.3 + (i % 2) * 2.3, 1.0 + (i // 2) * 2.75
    picture(s, THUMB[sp], px_, py_, w=2.1, h=2.1, border=WHITE)
    text(s, px_, py_ + 2.17, 2.1, 0.35, [nice(sp)], size=12, color=SKY, italic=True, align=PP_ALIGN.CENTER, label="cap " + sp)
notes(s, 1)

# 2 Introduction ---------------------------------------------------------------------------------
s = new_slide()
header(s, "Introduction", "One photo in, one bird name out: 10 Texas species", 2, chain="Intro")
chips = [("What we classify", "Bird photos, one species per photo"), ("Classes", "10 Texas bird species"),
         ("Our approach", "A small CNN as a baseline, then 2 transfer learning models")]
for i, (k, v) in enumerate(chips):
    y0 = 1.95 + i * 1.12
    panel(s, 0.6, y0, 5.9, 0.98, fill=TINT)
    text(s, 0.85, y0 + 0.1, 5.4, 0.3, [k.upper()], size=11, bold=True, color=BLUE)
    text(s, 0.85, y0 + 0.42, 5.4, 0.5, [v], size=16, bold=True, label="chip " + k)
panel(s, 0.6, 5.4, 5.9, 1.35, fill=SAND)
text(s, 0.85, 5.48, 5.4, 1.2, [[("Why it matters: ", {"bold": True, "color": BROWN}),
                               ("bird-ID apps and citizen science (eBird, iNaturalist) turn photos into data about where birds live. A wrong ID is a bad record.", {})]],
     size=14, label="why2")
for r, (lab_, a, b, col, fill) in enumerate([("Easy", "Northern Cardinal", "Roadrunner", BLUE, TINT),
                                              ("Hard", "Red Tailed Hawk", "Red Shouldered Hawk", RED, ROSE)]):
    y0 = 1.95 + r * 2.45
    panel(s, 6.85, y0, 5.88, 2.25, fill=fill)
    text(s, 7.05, y0 + 0.12, 1.0, 0.4, [lab_.upper()], size=13, bold=True, color=col)
    for k, sp in enumerate((a, b)):
        picture(s, THUMB[sp], 7.75 + k * 2.6, y0 + 0.15, w=1.6, h=1.6)
        text(s, 7.55 + k * 2.6, y0 + 1.8, 2.0, 0.35, [nice(sp)], size=12, italic=True, color=MUTED, align=PP_ALIGN.CENTER, label="c2 " + sp)
    text(s, 9.35, y0 + 0.45, 1.0, 1.0, ["vs."], size=24, bold=True, color=col, face=HEAD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="vs")
notes(s, 2)

# 3 Dataset ---------------------------------------------------------------------------------------
s = new_slide()
header(s, "Dataset", "1,710 photos of 10 species, split 70 / 15 / 15", 3, chain="Data")
order10 = ["Northern Cardinal", "Green Jay", "Roadrunner", "Northern Mockingbird", "Mourning Dove",
           "Rock Dove", "Red Tailed Hawk", "Red Shouldered Hawk", "Crow", "Common Grackle"]
for i, sp in enumerate(order10):
    x0, y0 = 0.6 + (i % 5) * 1.62, 1.95 + (i // 5) * 2.2
    picture(s, THUMB[sp], x0, y0, w=1.45, h=1.45)
    text(s, x0 - 0.05, y0 + 1.5, 1.55, 0.6, [nice(sp), f"{int(counts[sp])} photos"], size=10.5, color=INK,
         align=PP_ALIGN.CENTER, after=0, label="ds " + sp)
segs = [("Train", 1197, BLUE, "the model learns"), ("Validation", 256, SKY, "compare models"), ("Test", 257, NIGHT, "final check, once")]
text(s, 0.6, 6.4, 8.0, 0.4, ["Source: BIRDS 525 (Piosenka), CC0 public domain · all photos 224 × 224 color · 0 broken files, 0 duplicates"],
     size=11, italic=True, color=MUTED, label="src3")
y0 = 1.95
for name_, n_, col, role in segs:
    b = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 9.0, y0, 3.73, 1.3, fill=col, radius=0.08)
    label_in(b, f"{name_}: {n_:,}\n{role}", size=17, color=WHITE if col != SKY else INK)
    y0 += 1.45
notes(s, 3)

# 4 Challenges ------------------------------------------------------------------------------------
s = new_slide()
header(s, "Dataset challenges", "Lookalike birds, few photos, and hawks shot against the sky", 4, chain="Data")
fit_picture(s, FIG / "lookalike_pairs.png", 0.6, 1.9, 6.6, 3.55, center=False)
text(s, 0.6, 5.5, 6.5, 0.4, [[("1  Lookalike pairs: ", {"bold": True, "color": RED}), ("doves, hawks, crow vs. grackle", {})]], size=14, label="c41")
text(s, 0.6, 5.95, 6.5, 0.4, [[("2  Small dataset: ", {"bold": True, "color": RED}), ("only ~120 training photos per bird", {})]], size=14, label="c42")
text(s, 0.6, 6.4, 6.5, 0.4, [[("3  Mild imbalance only: ", {"bold": True, "color": BLUE}), ("142 to 212 photos per bird", {})]], size=14, label="c43")
sk = sky.sort_values(ascending=False)
text(s, 7.5, 1.9, 5.3, 0.35, ["Share of photo border that is blue sky"], size=13, bold=True, color=MUTED, label="skyt")
bar_chart(s, 7.4, 2.25, 5.4, 3.75, [nice(c) for c in sk.index], [float(v) for v in sk.values],
          [RED if "Hawk" in c else SKY for c in sk.index], fmt="0%", size=11, axis_max=0.42, gap=40)
panel(s, 7.4, 6.05, 5.33, 0.75, fill=ROSE)
text(s, 7.6, 6.05, 5.0, 0.75, [[("4  Background: ", {"bold": True, "color": RED}),
                               ("hawks ≈ ⅓ sky. A model could learn \"sky = hawk\", so we checked later.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="surp")
notes(s, 4)

# 5 Preprocessing ---------------------------------------------------------------------------------
s = new_slide()
header(s, "Preprocessing", "Four steps to get the photos ready", 5, chain="Preprocess")
steps5 = [("1  Split", "Stratified 70 / 15 / 15\nsame share of each bird\nin every group, seed 42"),
          ("2  Resize", "224 × 224 for the\npretrained models\n128 × 128 for the baseline"),
          ("3  Normalize", "Baseline: pixels 0–255 → 0–1\nPretrained models:\ntheir own scaling"),
          ("4  Augment", "Flip, rotate, zoom, contrast\ntraining photos only\ntested: didn't help")]
x = 0.6
for i, (h_, sub) in enumerate(steps5):
    kind = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
    c = shape(s, kind, x, 1.95, 3.15, 0.85, fill=RED if i == 3 else BLUE)
    label_in(c, h_, size=17)
    text(s, x + 0.35, 2.9, 2.65, 1.0, [sub], size=12.5, color=INK, after=0, label="p5 " + h_)
    x += 3.0
text(s, 0.6, 4.0, 12.1, 0.35, ["Augmentation examples (training photos only; validation and test photos are never changed)"], size=13, bold=True, color=MUTED, label="augt")
fit_picture(s, FIG / "augmentation_examples.png", 0.6, 4.4, 12.1, 2.35)
notes(s, 5)

# 6 Baseline architecture -------------------------------------------------------------------------
s = new_slide()
header(s, "Baseline model", "Our baseline: a small CNN built and trained from scratch", 6, chain="Baseline")
blocks = [("Photo", "128×128×3"), ("Conv 32", "+ pool"), ("Conv 64", "+ pool"), ("Conv 128", "+ pool"), ("Conv 128", "+ pool"),
          ("Avg pool +\ndropout 30%", ""), ("Softmax", "10 birds")]
x = 0.6
for i, (a, b) in enumerate(blocks):
    c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 2.1, 1.5, 1.15, fill=NIGHT if i in (0, 6) else BLUE, radius=0.12)
    label_in(c, f"{a}\n{b}".strip(), size=13)
    if i < len(blocks) - 1:
        text(s, x + 1.5, 2.1, 0.27, 1.15, ["→"], size=18, bold=True, color=GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="arr")
    x += 1.77
text(s, 0.6, 3.4, 12.1, 0.4, ["Each convolution block finds patterns (edges → textures → beaks and wings); pooling shrinks the image between blocks."],
     size=14, color=MUTED, italic=True, label="cnncap")
cards6 = [("242,122", "weights, all trained"), ("Adam", "optimizer, learning rate 0.001"), ("32", "photos per batch"),
          ("30", "epochs max, early stopping")]
for i, (big, small_) in enumerate(cards6):
    x0 = 0.6 + i * 3.06
    panel(s, x0, 4.2, 2.9, 1.5, fill=SAND)
    text(s, x0 + 0.15, 4.3, 2.6, 0.7, [big], size=30, bold=True, color=BROWN, face=HEAD, align=PP_ALIGN.CENTER, label="c6 " + big)
    text(s, x0 + 0.15, 5.05, 2.6, 0.6, [small_], size=13, color=MUTED, align=PP_ALIGN.CENTER, label="c6s " + big)
text(s, 0.6, 6.0, 12.1, 0.7, ["Minimum preprocessing only: resize to 128 px and scale pixels to 0–1. Loss: cross-entropy; output: 10 probabilities that add up to 100%."],
     size=14, label="min6")
notes(s, 6)

# 7 Baseline results
results_slide(7, "Baseline CNN", "The baseline gets about 7 in 10 birds right, but mixes up lookalikes",
              MAIN["Baseline CNN"], BROWN, SAND, ("81", "mistakes out of 257", RED, ROSE),
              "Training and validation stay close (no overfitting), but accuracy is low: too few photos to learn from scratch.")

# 8 Transfer learning -----------------------------------------------------------------------------
s = new_slide()
header(s, "Transfer learning", "Two pretrained models, used for feature extraction", 8, chain="Transfer")
flow = [("Pretrained on ImageNet\n~1.3 million photos", NIGHT), ("Pretrained layers\nFROZEN (not changed)", BLUE),
        ("Old 1,000-class layer\nremoved", GRAY), ("New layer for\nour 10 birds: TRAINED", BROWN)]
x = 0.6
for i, (t_, col) in enumerate(flow):
    c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 1.95, 2.75, 1.1, fill=col, radius=0.1)
    label_in(c, t_, size=13.5, color=WHITE if col != GRAY else INK)
    if i < 3:
        text(s, x + 2.75, 1.95, 0.4, 1.1, ["→"], size=20, bold=True, color=GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, label="a8")
    x += 3.13
rows8 = [["", "MobileNetV2", "ResNet50"],
         ["Design", "Small and fast, built for phones", "Deep (50 layers), skip connections"],
         ["Pretrained weights (frozen)", "~2.3 million", "~23.6 million"],
         ["Features per photo", "1,280", "2,048"],
         ["Weights we trained", "12,810", "20,490"],
         ["Pixel scaling", "−1 to 1", "ImageNet color average subtracted"],
         ["Training time (laptop)", "~3 minutes", "~13 minutes"]]
table(s, 0.6, 3.35, rows8, col_w=[2.6, 2.9, 3.3], row_h=0.48, size=13)
panel(s, 9.65, 3.35, 3.08, 3.36, fill=ROSE)
text(s, 9.85, 3.45, 2.7, 0.4, ["Also tried"], size=15, bold=True, color=RED, face=HEAD, label="at")
text(s, 9.85, 3.9, 2.7, 2.75, ["Fine-tuning MobileNetV2 (retraining its top 30 or 60 layers): no better than frozen",
                               "Augmentation with MobileNetV2: no better",
                               "So both final models are frozen, no augmentation"], size=12.5, bullets=True, bullet_color=RED, after=6, label="atb")
notes(s, 8)

# 9-10 Transfer results
results_slide(9, "MobileNetV2", "MobileNetV2 gets 96% right, 28 points above the baseline",
              MAIN["MobileNetV2"], BLUE, TINT, (f"+{(mob_t['accuracy'] - base_t['accuracy']) * 100:.1f}", "points vs. baseline", BLUE, TINT),
              "Training and validation stay close: very little overfitting. Lowest scores: hawks and crow/grackle.")
results_slide(10, "ResNet50", "ResNet50 gets 98% right, our strongest model",
              MAIN["ResNet50"], GREEN_, RGBColor(0xE8, 0xF4, 0xEC),
              (f"+{(res_t['accuracy'] - base_t['accuracy']) * 100:.1f}", "points vs. baseline", GREEN_, RGBColor(0xE8, 0xF4, 0xEC)),
              "Training accuracy nears 100% while validation stays ~96–97%: a little overfitting, kept in check by dropout and early stopping.")

# 11 All models compared --------------------------------------------------------------------------
s = new_slide()
header(s, "Evaluation", "Both pretrained models beat our CNN by about 30 points", 11, chain="Results")
rows11 = [["Model (257 test photos)", "Accuracy", "Loss", "Precision", "Recall", "F1", "Val. F1", "Mistakes"]]
mistakes = {"1. Baseline CNN": 81, "3b. MobileNetV2 frozen, no augmentation": 10, "3c. ResNet50 frozen, no augmentation": 5}
show11 = [("Baseline CNN (from scratch)", "1. Baseline CNN"), ("Baseline CNN + augmentation", "2. CNN + augmentation"),
          ("MobileNetV2 (frozen)", "3b. MobileNetV2 frozen, no augmentation"), ("MobileNetV2, fine-tuned", "5. Fine-tuned (tuned)"),
          ("ResNet50 (frozen), best", "3c. ResNet50 frozen, no augmentation")]
for lab_, k in show11:
    m_ = T[k]
    cm_ = round((1 - m_["accuracy"]) * 257)
    rows11.append([lab_, f"{m_['accuracy']:.1%}", f"{m_['loss']:.3f}", f"{m_['precision']:.3f}", f"{m_['recall']:.3f}",
                   f"{m_['F1']:.3f}", f"{V[k]['F1']:.3f}", str(cm_)])
fills11 = {(1, j): (SAND, INK) for j in range(8)}
table(s, 0.6, 1.95, rows11, col_w=[3.55, 1.25, 1.1, 1.25, 1.1, 1.0, 1.1, 1.25], row_h=0.55, size=14, highlight=5, fills=fills11)
text(s, 0.6, 5.35, 12.1, 0.35, ["Precision, recall and F1 are averages over the 10 species. Baseline row shaded; best row highlighted."],
     size=11, italic=True, color=MUTED, label="cap11")
panel(s, 0.6, 5.8, 12.13, 0.95, fill=TINT)
text(s, 0.85, 5.8, 11.7, 0.95, [[("Validation vs. test: ", {"bold": True, "color": BLUE}),
                                 ("on validation the two pretrained models tied (F1 0.964 vs. 0.965); on the test set ResNet50 pulled ahead with half the mistakes.", {})]],
     size=14, anchor=MSO_ANCHOR.MIDDLE, label="vt11")
notes(s, 11)

# 12 Confusion matrices ---------------------------------------------------------------------------
s = new_slide()
header(s, "Confusion matrices", "The best models only mix up the lookalike pairs", 12, chain="Results")
fit_picture(s, FIG / "confusion_matrices_all.png", 0.6, 1.85, 12.13, 3.95)
cards12 = [("81", "Baseline CNN: mistakes spread everywhere (15 red-tailed hawks called red-shouldered)", BROWN, SAND),
           ("10", "MobileNetV2: all 10 inside lookalike pairs (5 hawks, 4 crow/grackle, 1 dove)", BLUE, TINT),
           ("5", "ResNet50: 2 hawks, 2 crow/grackle, 1 roadrunner called a mockingbird", GREEN_, RGBColor(0xE8, 0xF4, 0xEC))]
for i, (big, small_, col, fill) in enumerate(cards12):
    x0 = 0.6 + i * 4.1
    panel(s, x0, 5.9, 3.93, 0.95, fill=fill)
    text(s, x0 + 0.12, 5.9, 0.85, 0.95, [big], size=28, bold=True, color=col, face=HEAD, anchor=MSO_ANCHOR.MIDDLE, label="b12")
    text(s, x0 + 1.0, 5.9, 2.85, 0.95, [small_], size=11.5, anchor=MSO_ANCHOR.MIDDLE, label="s12 " + big)
notes(s, 12)

# 13 Strongest model --------------------------------------------------------------------------------
s = new_slide()
header(s, "Strongest model", "Why ResNet50 worked best, and why MobileNetV2 is close behind", 13, chain="Results")
cols13 = [("Why ResNet50 is strongest", GREEN_, RGBColor(0xE8, 0xF4, 0xEC),
           ["Much deeper network (50 layers)", "Describes each photo with 2,048 features vs. 1,280", "Catches small details: a hawk's chest, a grackle's eye",
            f"98.1% accuracy, lowest loss ({res_t['loss']:.3f}), 5 mistakes"]),
          ("Why both beat our CNN", BLUE, TINT,
           ["Already learned feathers, eyes, beaks from ~1.3 million photos", "Our CNN had only ~1,200 photos to learn from",
            "Frozen layers can't overfit our small dataset"]),
          ("The trade-off", BROWN, SAND,
           ["MobileNetV2 is ~10× smaller and ~4× faster", "Almost as accurate (96.1%)", "ResNet50 if accuracy matters most; MobileNetV2 for a phone app"])]
for i, (h_, col, fill, items) in enumerate(cols13):
    x0 = 0.6 + i * 4.1
    panel(s, x0, 1.95, 3.93, 4.8, fill=fill)
    text(s, x0 + 0.22, 2.08, 3.5, 0.75, [h_], size=17, bold=True, color=col, face=HEAD, label="h13 " + h_)
    text(s, x0 + 0.22, 2.9, 3.5, 3.75, items, size=16, bullets=True, bullet_color=col, after=12, label="i13 " + h_)
notes(s, 13)

# 14 Grad-CAM + why not perfect --------------------------------------------------------------------
s = new_slide()
header(s, "Interpretation", "The model looks at the bird, not the sky", 14, chain="Results")
fit_picture(s, FIG / "gradcam.png", 0.6, 1.8, 12.13, 3.95)
gb = R["gradcam_border_share"]
panel(s, 0.6, 5.85, 6.0, 1.0, fill=TINT)
text(s, 0.8, 5.85, 5.65, 1.0, [[("Grad-CAM (MobileNetV2): ", {"bold": True, "color": BLUE}),
                                (f"red = what mattered. The photo's outer edge is 49% of the area but gets only {min(gb.values()):.0%}–{max(gb.values()):.0%} of the heat.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="gb14")
panel(s, 6.8, 5.85, 5.93, 1.0, fill=ROSE)
text(s, 7.0, 5.85, 5.6, 1.0, [[("Why not perfect: ", {"bold": True, "color": RED}),
                              ("true lookalikes (a hawk from behind, a grackle in dull light) and a few likely mislabeled photos.", {})]],
     size=13, anchor=MSO_ANCHOR.MIDDLE, label="np14")
notes(s, 14)

# 15 Lessons learned ---------------------------------------------------------------------------------
s = new_slide()
header(s, "Lessons learned", "What this project taught us", 15)
lessons = [("1", "Transfer learning matters most", "Pretrained models beat our CNN by about 30 points. Reusing knowledge beats starting from zero."),
           ("2", "Overfitting", "We watched the train vs. validation curves. Dropout, frozen layers and early stopping kept the gap small."),
           ("3", "Slow training", "No GPU: we trained on a laptop, kept the baseline small and limited the CPU so it didn't overheat."),
           ("4", "Test one change at a time", "Augmentation and fine-tuning, which we expected to help, didn't. We only knew because we tested them separately.")]
for i, (n_, h_, b_) in enumerate(lessons):
    x0, y0 = 0.6 + (i % 2) * 6.15, 1.95 + (i // 2) * 1.85
    panel(s, x0, y0, 5.98, 1.65, fill=TINT)
    c = shape(s, MSO_SHAPE.OVAL, x0 + 0.2, y0 + 0.2, 0.55, 0.55, fill=BLUE)
    label_in(c, n_, size=15, face=HEAD)
    text(s, x0 + 0.95, y0 + 0.2, 4.8, 0.4, [h_], size=16, bold=True, color=BLUE, face=HEAD, label="lh " + h_)
    text(s, x0 + 0.95, y0 + 0.62, 4.85, 1.0, [b_], size=14, label="lb " + h_)
panel(s, 0.6, 5.75, 12.13, 1.05, fill=ROSE)
text(s, 0.85, 5.75, 11.7, 1.05, [[("Limits: ", {"bold": True, "color": RED}),
                                  ("our photos are clean and centered, so 98% here won't mean 98% on blurry backyard photos, and the model only knows these 10 birds.", {})]],
     size=15, anchor=MSO_ANCHOR.MIDDLE, label="lim15")
notes(s, 15)

# 16 References -----------------------------------------------------------------------------------
s = new_slide()
header(s, "References", "References (APA)", 16)
refs = ["Abadi, M., et al. (2015). TensorFlow: Large-scale machine learning on heterogeneous systems. https://www.tensorflow.org",
        "Cornell Lab of Ornithology. (n.d.). Merlin Bird ID [Mobile app]. https://merlin.allaboutbirds.org",
        "He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. Proceedings of IEEE CVPR, 770–778.",
        "Piosenka, G. (2023). BIRDS 525 species – Image classification [Data set]. Kaggle. Mirror: https://huggingface.co/datasets/chriamue/bird-species-dataset (CC0 1.0).",
        "Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L.-C. (2018). MobileNetV2: Inverted residuals and linear bottlenecks. Proceedings of IEEE CVPR, 4510–4520.",
        "Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. Proceedings of IEEE ICCV, 618–626.",
        "Our code and notebooks: https://github.com/Mateen1367/BIRDS-PROJECT"]
text(s, 0.6, 1.9, 12.1, 5.0, refs, size=13, after=9, label="refs")
notes(s, 16)

# 17 Questions ------------------------------------------------------------------------------------
s = new_slide(dark=True)
text(s, 0.8, 1.7, 6.8, 1.2, ["Thank you"], size=54, bold=True, color=WHITE, face=HEAD, label="ty")
text(s, 0.8, 2.95, 6.8, 0.8, ["Questions?"], size=34, color=SKY, face=HEAD, label="q")
text(s, 0.8, 5.5, 6.8, 1.0, ["Mateen Jan  ·  Tej Govindu  ·  Alejandro Alfonso", "github.com/Mateen1367/BIRDS-PROJECT"],
     size=15, color=SKY, after=6, label="qnames")
for i, sp in enumerate(["Northern Mockingbird", "Common Grackle", "Mourning Dove", "Red Shouldered Hawk"]):
    px_, py_ = 8.3 + (i % 2) * 2.3, 1.0 + (i // 2) * 2.75
    picture(s, THUMB[sp], px_, py_, w=2.1, h=2.1, border=WHITE)
    text(s, px_, py_ + 2.17, 2.1, 0.35, [nice(sp)], size=12, color=SKY, italic=True, align=PP_ALIGN.CENTER, label="qcap " + sp)
notes(s, 17)

# ---------------------------------------------------------------- backup slides
s = new_slide()
header(s, "Backup", "Fine-tuning grid (validation only): no setting beat the frozen model", 18)
rows_b = [["Unfrozen top layers", "Learning rate", "Validation F1", "Epochs run"]]
for g in sorted(R["tuning_grid"], key=lambda g: (g["unfrozen layers"], g["learning rate"])):
    rows_b.append([str(g["unfrozen layers"]), g["learning rate"].replace("e-05", "e-5"), f"{g['val F1']:.3f}", str(g["epochs"])])
rows_b.append(["Frozen (feature extraction)", "0.001 (new layer only)", f"{V['3b. MobileNetV2 frozen, no augmentation']['F1']:.3f}", "15"])
table(s, 0.6, 1.95, rows_b, col_w=[3.4, 2.8, 2.2, 2.0], row_h=0.55, size=15, highlight=len(rows_b) - 1)
text(s, 0.6, 5.5, 12.1, 0.9, ["Early stopping ended every fine-tuning run after 4 epochs: validation loss rose right away. With ~1,200 photos, unfreezing 1.5 million weights mostly memorizes."],
     size=14, color=MUTED, label="bk1")
s.notes_slide.notes_text_frame.text = "[BACKUP] Fine-tuning grid. Use if asked about tuning or fine-tuning."

s = new_slide()
header(s, "Backup", "Training curves for all three models", 19)
fit_picture(s, FIG / "training_curves.png", 0.6, 1.85, 12.1, 5.0)
s.notes_slide.notes_text_frame.text = "[BACKUP] Accuracy and loss per epoch for the baseline, MobileNetV2 and ResNet50."

out = "reports/WhichTexasBird_Presentation.pptx"
prs.save(out)
print("saved", out, "·", len(prs.slides), "slides")
print("\n".join(FIT_WARNINGS) if FIT_WARNINGS else "text fit: OK")
