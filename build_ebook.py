# -*- coding: utf-8 -*-
"""
Ebook generator - Automation Skills Portfolio series
Applied AI: AI-Driven Edge Vision Integration
Author: Sipho Lucky Sibanda
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Oblique", FD + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("Cond-Bold", FD + "DejaVuSansCondensed-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Cond", FD + "DejaVuSansCondensed.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold", FD + "DejaVuSansMono-Bold.ttf"))

# ---------------------------------------------------------------------------
# Palette - violet/cyan "edge AI" identity for this project
# ---------------------------------------------------------------------------
BASE      = colors.HexColor("#0C0A16")
BASE2     = colors.HexColor("#141225")
BASE_LINE = colors.HexColor("#2A2645")
VIOLETACC = colors.HexColor("#B79CFF")
VIOLETACC_LT = colors.HexColor("#EAE0FF")
DEEPVIOLET = colors.HexColor("#5B3FA8")
TEAL      = colors.HexColor("#2FBE96")
AMBER     = colors.HexColor("#F5A623")
RED       = colors.HexColor("#E0503E")
CYAN      = colors.HexColor("#2FB8C4")
INK       = colors.HexColor("#211C3D")
MUTED     = colors.HexColor("#6E6494")
MUTED_LT  = colors.HexColor("#D5CBF5")
PANEL     = colors.HexColor("#F1EDFB")
ROWBAND   = colors.HexColor("#F8F5FD")
GRIDLINE  = colors.HexColor("#DED4F5")

PAGE_W, PAGE_H = A4
MARGIN_L, MARGIN_R = 22 * mm, 20 * mm
MARGIN_TOP, MARGIN_BOT = 26 * mm, 24 * mm
AVAIL_W = PAGE_W - MARGIN_L - MARGIN_R

DOC_TITLE = "AI-DRIVEN EDGE VISION INTEGRATION"
AUTHOR = "Sipho Lucky Sibanda"
OUTFILE = "/home/claude/ai-vision-sorting/ebook/AI_Vision_Technical_Manual.pdf"

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
body = ParagraphStyle("body", fontName="Sans", fontSize=10.2, leading=15,
                       textColor=INK, spaceAfter=8, alignment=TA_JUSTIFY)
body_l = ParagraphStyle("body_l", parent=body, alignment=TA_LEFT)
lead = ParagraphStyle("lead", parent=body, fontSize=12.5, leading=18, textColor=DEEPVIOLET,
                       spaceAfter=10)
kicker = ParagraphStyle("kicker", fontName="Mono", fontSize=8.5, leading=11,
                         textColor=DEEPVIOLET, spaceAfter=2)
h1 = ParagraphStyle("h1", fontName="Cond-Bold", fontSize=19, leading=22,
                     textColor=colors.HexColor("#3A2A70"), spaceAfter=2)
h2 = ParagraphStyle("h2", fontName="Cond-Bold", fontSize=13.5, leading=16,
                     textColor=colors.HexColor("#3A2A70"), spaceBefore=14, spaceAfter=6)
h3 = ParagraphStyle("h3", fontName="Sans-Bold", fontSize=10.6, leading=13,
                     textColor=colors.HexColor("#3A2A70"), spaceBefore=8, spaceAfter=4)
caption = ParagraphStyle("caption", fontName="Sans-Oblique", fontSize=8.3, leading=11,
                          textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=10)
bullet = ParagraphStyle("bullet", parent=body, alignment=TA_LEFT, leftIndent=12,
                         bulletIndent=0, spaceAfter=5)
chip_num = ParagraphStyle("chip_num", fontName="Cond-Bold", fontSize=17, leading=20,
                           textColor=colors.white, alignment=TA_CENTER)
toc_entry = ParagraphStyle("toc_entry", fontName="Sans", fontSize=10.5, leading=16,
                            textColor=INK)
toc_num = ParagraphStyle("toc_num", fontName="Mono-Bold", fontSize=10.5, leading=16,
                          textColor=DEEPVIOLET)
cell_hdr = ParagraphStyle("cell_hdr", fontName="Sans-Bold", fontSize=8.6, leading=11,
                           textColor=colors.white)
cell_txt = ParagraphStyle("cell_txt", fontName="Sans", fontSize=8.6, leading=12,
                           textColor=INK)
code_style = ParagraphStyle("code", fontName="Mono", fontSize=7.4, leading=10.8,
                             textColor=VIOLETACC_LT)
log_style = ParagraphStyle("logstyle", fontName="Mono", fontSize=7.6, leading=11.4,
                            textColor=colors.HexColor("#8CF5D0"))
callout_title = lambda c: ParagraphStyle("ct", fontName="Sans-Bold", fontSize=9.6,
                                          leading=12, textColor=c, spaceAfter=3)
callout_body = ParagraphStyle("cb", fontName="Sans", fontSize=9.4, leading=13.4,
                               textColor=INK)

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def P(text, style=body):
    return Paragraph(text, style)

def chapter_head(num, title, kicker_text="AI EDGE VISION"):
    chip = Table([[Paragraph(str(num).zfill(2), chip_num)]],
                 colWidths=[17 * mm], rowHeights=[17 * mm])
    chip.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DEEPVIOLET),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    title_block = [P(kicker_text, kicker), P(title, h1)]
    row = Table([[chip, title_block]], colWidths=[22 * mm, AVAIL_W - 22 * mm])
    row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    rule = HRFlowable(width="100%", thickness=1.3, color=VIOLETACC, spaceBefore=8, spaceAfter=16)
    return [row, rule]

def subhead(text):
    return P(text, h2)

def bullets(items):
    out = []
    for it in items:
        out.append(P("&#8226;&nbsp;&nbsp;" + it, bullet))
    return out

def code_block(code_text, cap=None, style=code_style):
    lines = code_text.strip("\n").split("\n")
    esc_lines = []
    for ln in lines:
        stripped = ln.lstrip(" ")
        n = len(ln) - len(stripped)
        esc_lines.append("&nbsp;" * n + esc(stripped) if stripped else "&nbsp;")
    para = Paragraph("<br/>".join(esc_lines), style)
    cell = Table([[para]], colWidths=[AVAIL_W])
    cell.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BASE2),
        ("BOX", (0, 0), (-1, -1), 0.75, BASE_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    out = [cell]
    if cap:
        out.append(P(cap, caption))
    else:
        out.append(Spacer(1, 10))
    return out

def data_table(headers, rows, col_widths=None):
    data = [[Paragraph(h, cell_hdr) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), cell_txt) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3A2A70")),
        ("GRID", (0, 0), (-1, -1), 0.5, GRIDLINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ROWBAND))
    t.setStyle(TableStyle(style))
    return t

def callout(title, text, kind="info"):
    color = {"info": CYAN, "warning": AMBER, "critical": RED, "ok": TEAL}[kind]
    label = {"info": "NOTE", "warning": "ENGINEERING NOTE", "critical": "HONEST LIMITATION",
             "ok": "VERIFIED"}[kind]
    content = [P("%s &mdash; %s" % (label, title), callout_title(color)), P(text, callout_body)]
    inner = Table([[content]], colWidths=[AVAIL_W - 16])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    outer = Table([["", inner]], colWidths=[5, AVAIL_W - 5])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("BACKGROUND", (1, 0), (1, 0), PANEL),
        ("LEFTPADDING", (1, 0), (1, 0), 12),
        ("RIGHTPADDING", (1, 0), (1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return [outer, Spacer(1, 10)]

def full_image(path, cap, max_h_mm=95):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    ratio = ih / float(iw)
    w = AVAIL_W
    h = w * ratio
    max_h = max_h_mm * mm
    if h > max_h:
        h = max_h
        w = h / ratio
    img = Image(path, width=w, height=h)
    img.hAlign = "CENTER"
    return [img, P(cap, caption)]


# ---------------------------------------------------------------------------
# Page backgrounds
# ---------------------------------------------------------------------------
def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(BASE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setStrokeColor(BASE_LINE)
    c.setLineWidth(0.4)
    step = 12 * mm
    x = 0
    while x < PAGE_W:
        c.line(x, 0, x, PAGE_H); x += step
    y = 0
    while y < PAGE_H:
        c.line(0, y, PAGE_W, y); y += step

    c.setStrokeColor(VIOLETACC)
    c.setLineWidth(1.1)
    c.rect(10 * mm, 10 * mm, PAGE_W - 20 * mm, PAGE_H - 20 * mm, fill=0, stroke=1)

    # Decorative neural-net glyph, bottom right
    import math
    ox, oy = PAGE_W - 62 * mm, 40 * mm
    layer1 = [(0, 8), (0, 20)]
    layer2 = [(14, 2), (14, 14), (14, 26)]
    layer3 = [(28, 8), (28, 20)]
    def dot(px, py, color, r=1.3*mm):
        c.setFillColor(color)
        c.circle(ox + px*mm, oy + py*mm, r, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#3A3564"))
    c.setLineWidth(0.6)
    for a in layer1:
        for b in layer2:
            c.line(ox+a[0]*mm, oy+a[1]*mm, ox+b[0]*mm, oy+b[1]*mm)
    for a in layer2:
        for b in layer3:
            c.line(ox+a[0]*mm, oy+a[1]*mm, ox+b[0]*mm, oy+b[1]*mm)
    for p in layer1: dot(p[0], p[1], VIOLETACC)
    for p in layer2: dot(p[0], p[1], VIOLETACC)
    for p in layer3: dot(p[0], p[1], CYAN)
    c.setFillColor(VIOLETACC)
    c.setFont("Mono-Bold", 7)
    c.drawCentredString(ox+14*mm, oy - 10*mm, "TinyMLP")

    c.setFillColor(VIOLETACC)
    c.setFont("Mono", 10.5)
    c.drawString(24 * mm, PAGE_H - 42 * mm, "AUTOMATION SKILLS PORTFOLIO   ·   APPLIED AI")

    c.setFillColor(colors.white)
    c.setFont("Cond-Bold", 24)
    for i, line in enumerate(["AI-DRIVEN EDGE VISION", "INTEGRATION"]):
        c.drawString(24 * mm, PAGE_H - 62 * mm - i * 11.5 * mm, line)

    c.setFont("Cond", 13.5)
    c.setFillColor(MUTED_LT)
    c.drawString(24 * mm, PAGE_H - 90 * mm, "PLC-Controlled Neural Network Sorting Matrix")

    c.setStrokeColor(BASE_LINE)
    c.setLineWidth(0.8)
    c.line(24 * mm, 46 * mm, PAGE_W - 24 * mm, 46 * mm)

    c.setFont("Mono", 9.5)
    c.setFillColor(CYAN)
    c.drawString(24 * mm, 38 * mm, "TECHNICAL PROJECT MANUAL  ·  REV. A")
    c.setFont("Sans-Bold", 13)
    c.setFillColor(colors.white)
    c.drawString(24 * mm, 31 * mm, "By " + AUTHOR)
    c.setFont("Sans", 8.6)
    c.setFillColor(MUTED_LT)
    c.drawString(24 * mm, 25.5 * mm, "PLC: Siemens S7-1500 (SCL)  +  Python edge service (numpy, pymodbus)")
    c.drawString(24 * mm, 21 * mm, "Includes a genuinely executed integration test  ·  Not for production deployment")
    c.restoreState()

def draw_body(c, doc):
    c.saveState()
    c.setFillColor(BASE)
    c.rect(0, PAGE_H - 15 * mm, PAGE_W, 15 * mm, fill=1, stroke=0)
    c.setFillColor(VIOLETACC)
    c.setFont("Mono", 7.6)
    c.drawString(MARGIN_L, PAGE_H - 9.5 * mm, DOC_TITLE)
    c.setFillColor(colors.white)
    c.setFont("Sans", 7.4)
    c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 9.5 * mm, "By " + AUTHOR)
    c.setStrokeColor(VIOLETACC)
    c.setLineWidth(0.8)
    c.line(0, PAGE_H - 15 * mm, PAGE_W, PAGE_H - 15 * mm)

    c.setFillColor(MUTED)
    c.setFont("Mono", 7.8)
    c.drawString(MARGIN_L, 13 * mm, "AI-SORTING-MATRIX")
    c.drawCentredString(PAGE_W / 2, 13 * mm, "Page %d" % c.getPageNumber())
    c.drawRightString(PAGE_W - MARGIN_R, 13 * mm, "Simulation + Real Working Demo")
    c.setStrokeColor(VIOLETACC)
    c.setLineWidth(1)
    c.line(PAGE_W - MARGIN_R, 17 * mm, PAGE_W - MARGIN_R, 21 * mm)
    c.line(PAGE_W - MARGIN_R - 4 * mm, 17 * mm, PAGE_W - MARGIN_R, 17 * mm)
    c.restoreState()


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
story = [PageBreak()]

# ---- Document control / disclaimer ------------------------------------------------
story += chapter_head("i", "Document Control &amp; Disclaimer", "FRONT MATTER")
story.append(P(
    "This document is a self-authored technical project manual produced as part of a "
    "personal engineering portfolio. It describes the design and validation of an "
    "AI-driven edge vision integration: a Python edge service running a genuinely trained "
    "neural network, communicating with PLC-side sorting logic over Modbus TCP, built to "
    "demonstrate industrial edge AI integration, protocol-level engineering, and "
    "trust/fail-safe design for automation and applied AI engineering roles.", body))
story.append(P(
    "Unlike the other simulation-only projects in this portfolio series, the Python side "
    "of this project is genuinely functional and was actually executed to produce the test "
    "evidence in Chapter 7. The PLC-side Structured Text logic remains validated in "
    "simulation only, and neither side has been tested against real manufacturing "
    "hardware or a real camera.", body))

story += callout(
    "A real, working demo - with real limits",
    "The neural network genuinely trains and genuinely classifies synthetic data at "
    "94.4% held-out accuracy. It is not a production machine-vision system: it has never "
    "seen a real photograph, and the PLC-side logic has never driven a real actuator. "
    "Both facts are stated plainly rather than left for a reader to discover.", "critical")

data = [
    ["Document Title", "AI-Driven Edge Vision Integration \u2014 Technical Manual"],
    ["Author", AUTHOR],
    ["Revision", "A"],
    ["Document Type", "Portfolio Technical Manual (Python side genuinely executed)"],
    ["Target Platform", "Siemens S7-1500 (SCL) + Python 3 edge service"],
    ["Related Repository", "ai-vision-sorting"],
    ["Series", "Automation Skills Portfolio \u2014 Applied Artificial Intelligence"],
]
t = Table(data, colWidths=[45 * mm, AVAIL_W - 45 * mm])
t.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "Sans-Bold"), ("FONTNAME", (1, 0), (1, -1), "Sans"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.4), ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#3A2A70")),
    ("TEXTCOLOR", (1, 0), (1, -1), INK),
    ("GRID", (0, 0), (-1, -1), 0.4, GRIDLINE),
    ("BACKGROUND", (0, 0), (0, -1), PANEL),
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
]))
story.append(t)
story.append(PageBreak())

# ---- Contents ------------------------------------------------------------
story += chapter_head("ii", "Contents", "FRONT MATTER")
toc = [
    ("01", "Industry Context: Edge AI in Manufacturing"),
    ("02", "System Architecture &amp; Integration Overview"),
    ("03", "The Neural Network: Honest Scope &amp; Design"),
    ("04", "I/O List &amp; Modbus Register Map"),
    ("05", "Control Philosophy: Why the PLC Doesn't Trust the AI"),
    ("06", "PLC Logic Walkthrough"),
    ("07", "The Genuinely Executed Integration Test"),
    ("08", "HMI Design &amp; the Conveyor Visualisation"),
    ("09", "Testing, Commissioning &amp; FAT Procedures"),
    ("10", "Limitations, Real-World Deltas &amp; Future Work"),
    ("A", "Appendix A &mdash; I/O Quick Reference"),
    ("B", "Appendix B &mdash; Full Structured Text Listing"),
    ("C", "Appendix C &mdash; Key Python Listings"),
    ("D", "Appendix D &mdash; Glossary"),
    ("&mdash;", "About the Author"),
]
rows = []
for num, title in toc:
    rows.append([P(num, toc_num), P(title, toc_entry)])
tt = Table(rows, colWidths=[14 * mm, AVAIL_W - 14 * mm])
tt.setStyle(TableStyle([
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LINEBELOW", (0, 0), (-1, -2), 0.4, GRIDLINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
]))
story.append(tt)
story.append(PageBreak())

# ---- Executive Summary ----------------------------------------------------
story += chapter_head("iii", "Executive Summary", "FRONT MATTER")
story.append(P(
    "This is the third deliberate discipline shift in the wider automation portfolio, and "
    "the first to genuinely span two languages and two runtimes: IEC 61131-3 Structured "
    "Text on the PLC side, and real, executable Python on the edge AI side. A standard "
    "industrial PLC cannot run a neural network - but it doesn't need to. It needs to talk "
    "to something that can, receive a trustworthy answer, and act on it physically and "
    "safely.", lead))
story.append(P(
    "The Python side trains a small, honest neural network from scratch (hand-written "
    "numpy backpropagation, no framework) on synthetic surface-defect data, reaching "
    "94.4% held-out test accuracy. It then runs as a genuine Modbus TCP client, polling a "
    "PLC-hosted register map for new items and writing back a defect verdict and confidence "
    "score for each one - the real \"Python-to-PLC handshake\" this project is named for.", body))
story.append(P(
    "The PLC-side logic, <b>FB_AI_SortingMatrix</b>, is where the engineering judgement "
    "actually lives: it tracks each item's physical position on the conveyor against its "
    "eventual AI result, applies a <i>second, stricter</i> confidence threshold on top of "
    "the model's own decision boundary, and watches an AI heartbeat so a dead edge service "
    "never gets treated as a silent \"all clear\". Every uncertain, late, or missing result "
    "routes to a human reviewer, never a guess.", body))
story.append(P(
    "Chapter 7 is unique to this project in the portfolio: because the Python side "
    "genuinely runs, it was genuinely tested end-to-end, including a run where the AI "
    "service was forcibly killed mid-stream to prove the watchdog actually catches it. The "
    "logs reproduced there are real console output, not a hypothetical description of "
    "expected behaviour.", body))
story.append(PageBreak())

# ---- Chapter 1: Industry context -------------------------------------------
story += chapter_head(1, "Industry Context: Edge AI in Manufacturing")
story.append(P(
    "Machine-vision defect detection has moved from expensive, purpose-built vision "
    "systems toward general-purpose <b>edge AI</b>: commodity PCs or industrial edge "
    "computers running trained models close to the production line, communicating results "
    "to the plant's existing control systems over standard industrial protocols. This "
    "project's architecture - a Python service on an edge PC, a PLC as the protocol's "
    "\"server of record\", Modbus TCP in between - mirrors that real pattern directly.", body))
story.append(subhead("Why Modbus TCP, and why the PLC is the server"))
story.append(P(
    "Modbus TCP remains one of the most common protocols for exactly this kind of "
    "integration: it's simple, well-understood, and supported natively by most industrial "
    "PLCs, including the Siemens S7-1500 referenced throughout this portfolio via its "
    "MB_SERVER instruction. Making the PLC the Modbus <i>server</i> (rather than the "
    "Python service) keeps the deterministic, safety-relevant controller as the trusted "
    "keeper of the register map, with the edge AI service as a client writing data into a "
    "structure the PLC defines and owns.", body))
story.append(subhead("Human-in-the-loop AI is not a fallback - it's the design"))
story.append(P(
    "A recurring theme in real industrial AI deployments is treating the model's output as "
    "a strong recommendation rather than an unquestionable verdict, particularly during "
    "commissioning and for genuinely ambiguous cases. This project treats that not as an "
    "afterthought but as the central design decision on the PLC side - see Chapter 5.", body))
story += callout(
    "Edge, not cloud",
    "Running inference on an edge PC rather than sending images to a cloud service avoids "
    "network latency and dependency on external connectivity for a production-line "
    "decision that needs to happen in a fixed time window - relevant here since the "
    "conveyor's transit-time budget (Chapter 5) is measured in single-digit seconds.", "info")
story.append(PageBreak())

# ---- Chapter 2: Architecture ----------------------------------------------
story += chapter_head(2, "System Architecture &amp; Integration Overview")
story.append(P(
    "A camera at the inspection point feeds the edge AI service; the edge service and the "
    "PLC exchange data over Modbus TCP on a compact seven-register map; the PLC drives a "
    "three-position diverter based on its own fail-safe evaluation of the AI's verdict.", body))
story += full_image("../images/architecture_diagram.png",
    "Figure 2.1 &mdash; Integration architecture. The dashed connection from the test "
    "harness shows where python/plc_simulator.py substitutes for the real PLC during "
    "development and testing.", max_h_mm=100)
story.append(subhead("Control hierarchy"))
story += bullets([
    "<b>Field layer</b> &mdash; a camera at the inspection point, two conveyor photoeyes, "
    "and a three-position sorting diverter.",
    "<b>Edge AI layer</b> &mdash; a Python service (<code>ai_sorting_service.py</code>) "
    "running the trained TinyMLP and acting as a Modbus TCP client.",
    "<b>Control layer</b> &mdash; the PLC (<code>FB_AI_SortingMatrix</code>), acting as "
    "the Modbus TCP server and the sole authority on what actually happens to each item.",
])
story.append(subhead("Why a hand-written test-harness server, not a library"))
story.append(P(
    "<code>plc_simulator.py</code> implements just enough of the Modbus TCP wire protocol "
    "(function codes 3, 6, and 16) by hand, rather than depending on a third-party server "
    "library. This was a pragmatic call made mid-project when a widely-used library's "
    "server API turned out to have changed significantly across versions in ways "
    "that would have made the test harness fragile - documented honestly in the module's "
    "own docstring rather than hidden.", body))
story.append(PageBreak())

# ---- Chapter 3: The Neural Network -----------------------------------------
story += chapter_head(3, "The Neural Network: Honest Scope &amp; Design")
story.append(P(
    "The model is deliberately small and fully inspectable: five hand-engineered features "
    "(mean, standard deviation, maximum deviation, and two gradient-energy measures) feed "
    "an 8-unit ReLU hidden layer, feeding a 2-class softmax output. Every line of the "
    "forward and backward pass is hand-written numpy in <code>vision_model.py</code> - no "
    "framework, nothing hidden.", body))
story.append(data_table(
    ["Property", "Value"],
    [
        ["Architecture", "5 inputs -> 8 hidden (ReLU) -> 2 outputs (softmax)"],
        ["Training data", "800 synthetic patches (200 ok, 600 defective across 3 defect types)"],
        ["Training method", "Manual gradient descent, 400 epochs, cross-entropy loss"],
        ["Held-out test accuracy", "94.4% (160 samples never seen during training)"],
        ["Framework dependencies", "None - numpy only"],
    ],
    col_widths=[54 * mm, AVAIL_W - 54 * mm]))
story.append(Spacer(1, 8))
story += callout(
    "Why synthetic data, and why that's stated up front",
    "Real machine-vision training data (thousands of labelled real photographs, covering "
    "real lighting and surface variation) is out of scope for a portfolio project. "
    "Procedurally generated patches with injected scratch/dent/discoloration signatures, "
    "at deliberately varied severity, let the model face genuinely ambiguous cases (hence "
    "a realistic accuracy figure, not a suspicious 100%) while remaining fully "
    "reproducible from a single script anyone can re-run.", "critical")
story.append(subhead("What the type label is, and isn't"))
story.append(P(
    "Only the binary defect/ok decision comes from the trained network. The defect "
    "<i>type</i> name shown alongside it (Scratch, Dent, Discoloration) comes from a "
    "separate, simple heuristic based on which injected signature the features most "
    "resemble - not a second trained classifier. This distinction is kept visible in the "
    "code and in this manual rather than implied to be more sophisticated than it is.", body))
story.append(PageBreak())

# ---- Chapter 4: I/O List ----------------------------------------------------
story += chapter_head(4, "I/O List &amp; Modbus Register Map")
story.append(P(
    "This project has two I/O surfaces: conventional field I/O, and a Modbus TCP holding "
    "register map shared with the Python edge service (see also "
    "<b>docs/IO_List.md</b> and Appendix A).", body))
story.append(subhead("Physical I/O"))
story.append(data_table(
    ["Tag", "Description", "Signal"],
    [
        ["DI_ItemPresent_InspectionPoint", "Photoeye at the camera station", "Digital"],
        ["DI_ItemPresent_DiverterPoint", "Photoeye just before the diverter", "Digital"],
        ["DO_DiverterArm_Position", "0=PASS, 1=REJECT, 2=MANUAL", "3-position"],
        ["DI_System_Enable", "Master enable", "Digital"],
    ],
    col_widths=[70 * mm, 66 * mm, AVAIL_W - 70 * mm - 66 * mm]))
story.append(Spacer(1, 10))
story.append(subhead("Modbus holding register map"))
story.append(data_table(
    ["Addr", "Name", "Written By", "Purpose"],
    [
        ["HR0", "Item_Trigger_Counter", "PLC", "New item detected"],
        ["HR1", "Item_ID_Ack", "AI service", "Which item this result is for"],
        ["HR2", "Defect_Detected", "AI service", "0/1"],
        ["HR3", "Confidence_Pct_x10", "AI service", "0-1000"],
        ["HR4", "Defect_Class_ID", "AI service", "0-3"],
        ["HR5", "AI_Heartbeat", "AI service", "Watchdog input"],
        ["HR6", "AI_Result_Ready", "AI sets / PLC clears", "Handshake flag"],
    ],
    col_widths=[16 * mm, 50 * mm, 40 * mm, AVAIL_W - 16 * mm - 50 * mm - 40 * mm]))
story.append(PageBreak())


# ---- Chapter 5: Control Philosophy -----------------------------------------
story += chapter_head(5, "Control Philosophy: Why the PLC Doesn't Trust the AI")
story.append(P(
    "Three ideas define the PLC-side design, and all three exist because a neural "
    "network's confidence score is a statistical property of the model, not a guarantee "
    "about the physical world.", body))
story.append(subhead("5.1 &nbsp; A second, stricter confidence threshold"))
story.append(P(
    "The Python model already applies its own 50% decision boundary to call something a "
    "defect at all. The PLC applies a completely separate pair of thresholds on top: below "
    "90% confidence, the verdict - whatever it is - routes to a human reviewer instead of "
    "being acted on directly. A PLC acting on a 51%-confidence classification is not "
    "meaningfully different from acting on a coin flip, and the PLC logic treats it that "
    "way.", body))
story.append(subhead("5.2 &nbsp; Tracking by identity, not by arrival order"))
story.append(P(
    "Multiple items can be in transit on the conveyor simultaneously. The PLC's tracking "
    "queue matches each incoming AI result to its own item by <code>Item_ID_Ack</code>, "
    "not by assuming results arrive in the same order items were detected - a real "
    "production line, and a real network, offer no such guarantee.", body))
story.append(subhead("5.3 &nbsp; The AI heartbeat is not the same thing as the AI being right"))
story.append(P(
    "A heartbeat only proves the Python process is still running its loop - it says "
    "nothing about whether its verdicts are correct. This project keeps those as two "
    "separate concerns deliberately: the heartbeat watchdog (Chapter 6.3) catches a dead "
    "or hung service; the confidence thresholds (5.1) are a completely independent defence "
    "against a <i>live but uncertain</i> service. Neither one substitutes for the other.", body))
story += callout(
    "Every uncertain path leads to the same place, on purpose",
    "No result received in time, an offline AI heartbeat, and a confidence score in the "
    "60-90% band all produce exactly the same outcome: manual review. That's not laziness "
    "in the design - a system with a different fallback for every flavour of uncertainty "
    "is harder to reason about and easier to get subtly wrong than one with a single, "
    "well-tested safe default.", "ok")
story.append(PageBreak())

# ---- Chapter 6: PLC Logic Walkthrough --------------------------------------
story += chapter_head(6, "PLC Logic Walkthrough")
story.append(P(
    "This chapter walks through <b>FB_AI_SortingMatrix</b> section by section. The full "
    "listing is reproduced in Appendix B.", body))

story.append(subhead("6.1 &nbsp; Pushing a new item into the tracking queue"))
story += code_block(
"""IF DI_System_Enable AND DI_ItemPresent_InspectionPoint AND (NOT Prev_InspectionSensor) THEN
    HR0_ItemTriggerCounter := HR0_ItemTriggerCounter + 1;
    FOR i := 0 TO QueueDepth - 1 DO
        IF (NOT Queue[i].Active) AND (NOT FreeSlotFound) THEN
            Queue[i].Active := TRUE;
            Queue[i].ItemID := HR0_ItemTriggerCounter;
            Queue[i].TransitTimer(IN := TRUE, PT := TransitDelay_PT);
            FreeSlotFound := TRUE;
        END_IF
    END_FOR
    IF NOT FreeSlotFound THEN Alarm_QueueFull := TRUE; END_IF
END_IF""", "Listing 6.1 &mdash; Each detected item claims the first free tracking slot.")

story.append(subhead("6.2 &nbsp; Matching a result to its item by ID"))
story += code_block(
"""IF HR6_AIResultReady THEN
    FOR i := 0 TO QueueDepth - 1 DO
        IF Queue[i].Active AND (Queue[i].ItemID = HR1_ItemIDAck) AND (NOT Queue[i].ResultReceived) THEN
            Queue[i].ResultReceived := TRUE;
            Queue[i].Defect_Detected := HR2_DefectDetected;
            Queue[i].Confidence_Pct := INT_TO_REAL(HR3_ConfidencePctX10) / 10.0;
            Queue[i].Defect_Class_ID := HR4_DefectClassID;
        END_IF
    END_FOR
    HR6_Clear_Ack := TRUE;
END_IF""", "Listing 6.2 &mdash; Results are matched by Item_ID, never by queue position.")

story.append(subhead("6.3 &nbsp; The heartbeat watchdog"))
story += code_block(
"""IF HR5_AIHeartbeat <> Prev_AIHeartbeat THEN
    T_HeartbeatWatch(IN := FALSE);
    Alarm_AI_Offline := FALSE;
ELSE
    T_HeartbeatWatch(IN := TRUE, PT := HeartbeatTimeout_PT);
    IF T_HeartbeatWatch.Q THEN
        Alarm_AI_Offline := TRUE;
    END_IF
END_IF
Prev_AIHeartbeat := HR5_AIHeartbeat;""", "Listing 6.3 &mdash; A frozen heartbeat for 2 seconds declares the AI offline.")

story.append(subhead("6.4 &nbsp; The routing decision"))
story.append(P(
    "This is where Chapter 5's philosophy becomes a fixed, auditable order of checks - "
    "every uncertain condition is evaluated before the AI's actual verdict is even "
    "considered.", body))
story += code_block(
"""IF (NOT Queue[i].ResultReceived) OR Alarm_AI_Offline THEN
    CurrentRoute := ROUTE_MANUAL_REVIEW;
ELSIF Queue[i].Confidence_Pct < LowConfidence_Pct THEN
    CurrentRoute := ROUTE_MANUAL_REVIEW;
ELSIF Queue[i].Confidence_Pct < HighConfidence_Pct THEN
    CurrentRoute := ROUTE_MANUAL_REVIEW;
ELSIF Queue[i].Defect_Detected THEN
    CurrentRoute := ROUTE_REJECT;
ELSE
    CurrentRoute := ROUTE_PASS;
END_IF""", "Listing 6.4 &mdash; Uncertainty is checked first; the AI's verdict is the last thing evaluated.")
story.append(PageBreak())

# ---- Chapter 7: Genuinely Executed Test ------------------------------------
story += chapter_head(7, "The Genuinely Executed Integration Test")
story.append(P(
    "Every other project in this portfolio can only be validated in simulation - there's "
    "no real ship, aircraft, or building to test against. This project's Python side "
    "genuinely runs, so it was genuinely tested: <code>plc_simulator.py</code> and "
    "<code>ai_sorting_service.py</code> were run as two independent OS processes, talking "
    "real Modbus TCP over localhost.", body))
story.append(subhead("7.1 &nbsp; Normal operation - real captured output"))
story += code_block(
"""[AI  ] Loaded trained model_weights.npz
[AI  ] Connected to PLC Modbus TCP server at 127.0.0.1:5020
[AI  ] Item #001 inferred: PASS  confidence=66.9%  class=None
[AI  ] Item #002 inferred: PASS  confidence=92.4%  class=None
[AI  ] Item #004 inferred: FAIL  confidence=79.0%  class=Dent

[PLC ] Item #001 detected at inspection point (HR0 Item_Trigger_Counter -> 1)
[PLC ] Result for item #001: PASS  (confidence 66.9%, class=None)
[PLC ] Item #004 detected at inspection point (HR0 Item_Trigger_Counter -> 4)
[PLC ] Result for item #004: FAIL  (confidence 79.0%, class=Dent)""", None, style=log_style)
story.append(P(
    "Item #001 (66.9%) and item #004 (79.0%) both landed inside the 60-90% uncertain band "
    "from Chapter 5.1. The simplified consumer logic inside the test harness just logs "
    "whatever it receives, but the real PLC logic in <code>AI_SortingMatrix.st</code> would "
    "route both of these specific, really-produced results to manual review rather than "
    "act on the raw verdict.", body))
story.append(subhead("7.2 &nbsp; The watchdog, tested against a real crash"))
story.append(P(
    "The AI service process was killed with <code>SIGKILL</code> mid-run - not a forced "
    "input value, an actual terminated process - while the PLC simulator kept running.", body))
story += code_block(
"""[AI  ] Item #001 inferred: FAIL  confidence=53.4%  class=Dent
[AI  ] Item #002 inferred: FAIL  confidence=87.0%  class=Dent
                                    <-- process killed here -->

[PLC ] Item #003 detected at inspection point (HR0 Item_Trigger_Counter -> 3)
[PLC ] *** AI_Heartbeat stale for >2.0s - declaring AI OFFLINE,
       routing all items to MANUAL REVIEW ***
[PLC ] Item #004 detected at inspection point (HR0 Item_Trigger_Counter -> 4)
[PLC ] Item #005 detected at inspection point (HR0 Item_Trigger_Counter -> 5)""", None, style=log_style)
story += callout(
    "What this actually proves, and what it doesn't",
    "This confirms the watchdog timing and detection logic work against a real dead "
    "process, on this machine, in this test harness. It does not validate the PLC-side "
    "Structured Text itself, which has only been exercised in simulation (Chapter 9) - the "
    "two are complementary evidence, not substitutes for each other.", "ok")
story.append(PageBreak())


# ---- Chapter 8: HMI ---------------------------------------------------------
story += chapter_head(8, "HMI Design &amp; the Conveyor Visualisation")
story.append(P(
    "The HMI mockup (<b>hmi/index.html</b> in the repository) shows items moving along a "
    "conveyor, being labelled live at the camera station, and a diverter arm swinging to "
    "route each one to its bin - matching, deliberately, exactly what a line operator "
    "watching this station would expect to see.", body))
story += full_image("../images/hmi-dashboard.png",
    "Figure 8.1 &mdash; Items in transit showing live classification labels (\"PASS\", "
    "\"FAIL 75%\", \"FAIL 78%\"), the neural-network glyph at the camera station, and "
    "the diverter arm mid-swing.", max_h_mm=110)
story.append(subhead("Design decisions"))
story += bullets([
    "<b>Violet/cyan \"edge AI\" palette</b> &mdash; a fourth distinct visual identity in "
    "this portfolio, chosen to read as technology/data-driven rather than purely "
    "industrial, appropriate for a station where a neural network genuinely makes the "
    "first call.",
    "<b>The confidence percentage is always shown, never hidden</b> &mdash; a \"FAIL\" "
    "label alone would misrepresent what the system actually knows; showing \"FAIL "
    "(AI Defect Detected: 78% Confidence)\" is honest about the uncertainty the PLC logic "
    "is built around.",
    "<b>A scripted AI-offline event</b> &mdash; the demo genuinely switches the heartbeat "
    "indicator and status pill mid-loop, so the fail-safe behaviour from Chapter 5 is "
    "something a viewer sees happen, not just a claim in the documentation.",
    "<b>Date.now()/setInterval over performance.now()/requestAnimationFrame</b> &mdash; "
    "applied proactively this time, based directly on the compatibility lessons learned "
    "building the first four HMIs in this portfolio, rather than discovered as a bug "
    "after the fact.",
])
story.append(PageBreak())

# ---- Chapter 9: Testing -----------------------------------------------------
story += chapter_head(9, "Testing, Commissioning &amp; FAT Procedures")
story.append(P(
    "The PLC-side function block was validated against ten simulated test cases, and the "
    "Python side was additionally validated by the genuinely executed runs in Chapter 7. "
    "The full procedure is in <b>docs/Testing_Procedures.md</b>; the simulated-side matrix "
    "is reproduced below.", body))
story.append(data_table(
    ["#", "Test Case", "Expected Result"],
    [
        ["1", "New item enters tracking queue", "Trigger counter increments; a slot activates"],
        ["2", "High-confidence PASS", "Diverter position 0; pass counter increments"],
        ["3", "High-confidence REJECT", "Diverter position 1; reject counter increments"],
        ["4", "Uncertain-band confidence (defect)", "Routes to manual despite a defect verdict"],
        ["5", "Low confidence (no defect)", "Routes to manual despite a clear verdict"],
        ["6", "No result received in time", "Routes to manual; does not wait indefinitely"],
        ["7", "AI heartbeat watchdog trips", "Alarm_AI_Offline TRUE; all items route to manual"],
        ["8", "Watchdog recovers", "Alarm clears; normal routing resumes"],
        ["9", "Result matched by ID, not order", "Correctly matched even out of sequence"],
        ["10", "Queue full", "Alarm_QueueFull TRUE"],
    ],
    col_widths=[10 * mm, 66 * mm, AVAIL_W - 10 * mm - 66 * mm]))
story.append(Spacer(1, 10))
story += callout(
    "Reproduce it yourself",
    "cd python && python3 train_model.py && python3 plc_simulator.py 30 & "
    "python3 ai_sorting_service.py 10 &mdash; the full commands are in the README and "
    "docs/Testing_Procedures.md.", "info")
story.append(PageBreak())

# ---- Chapter 10: Limitations -------------------------------------------------
story += chapter_head(10, "Limitations, Real-World Deltas &amp; Future Work")
story.append(P(
    "Naming the gap between a working demonstration and a production system is part of "
    "the engineering, consistent with every other project in this portfolio - if anything "
    "more important here, since it would be easy to let \"it actually runs\" overstate how "
    "close this is to production-ready.", body))
story.append(subhead("What a real deployment would add"))
story += bullets([
    "<b>Real training data</b> &mdash; thousands of labelled real photographs covering "
    "actual lighting, surface, and camera variation, replacing this project's synthetic "
    "patches.",
    "<b>A real camera and lighting rig</b> &mdash; machine-vision lighting design is its "
    "own discipline; inconsistent lighting alone can defeat a well-trained model.",
    "<b>Redundant edge hardware</b> &mdash; a single edge PC is a single point of failure; "
    "a production line would need a hot-standby or a documented safe-stop procedure for "
    "extended AI outages, not just an indefinite manual-review mode.",
    "<b>A PLC-side implementation actually tested against real Modbus TCP</b> &mdash; "
    "Chapter 7's real test proves the Python side and the wire protocol; "
    "AI_SortingMatrix.st itself still needs its own PLCSIM/hardware validation pass.",
])
story.append(subhead("10.1 &nbsp; Hazard &amp; safeguard register (HAZOP-style)"))
story.append(data_table(
    ["Hazard", "Cause", "Safeguard in This Design"],
    [
        ["Good item rejected / bad item passed", "Model error on a genuinely hard case",
         "Confidence thresholds route ambiguous cases to a human rather than trusting a single score"],
        ["Sorting on stale data", "AI service hung but still writing old register values",
         "Heartbeat watchdog, independent of the result registers themselves"],
        ["Item mismatch under load", "High item rate outpacing the tracking queue",
         "Alarm_QueueFull - named as a real limit rather than silently dropping items"],
        ["Undetected model drift over time", "Real production surfaces change over months",
         "Named gap - no drift-monitoring is implemented in this portfolio scope"],
    ],
    col_widths=[48 * mm, 50 * mm, AVAIL_W - 48 * mm - 50 * mm]))
story.append(Spacer(1, 8))
story.append(subhead("Where this project could go next"))
story += bullets([
    "Replace the synthetic dataset with a small real, labelled image set and a proper "
    "convolutional feature extractor.",
    "Add a second edge PC and a documented failover/voting scheme, rather than a single "
    "point of AI failure.",
    "Extend the genuinely-executed test suite to include simulated network latency and "
    "packet loss, not just a clean crash.",
])
story.append(PageBreak())


# ---- Appendix A: I/O Quick Reference ---------------------------------------
story += chapter_head("A", "Appendix A &mdash; I/O Quick Reference", "APPENDIX")
story.append(data_table(
    ["Tag / Register", "Dir.", "Type", "Notes"],
    [
        ["DI_ItemPresent_InspectionPoint", "IN", "BOOL", "Photoeye"],
        ["DI_ItemPresent_DiverterPoint", "IN", "BOOL", "Cross-check"],
        ["DI_System_Enable", "IN", "BOOL", "Master enable"],
        ["HR1_ItemIDAck", "IN", "INT", "From AI service"],
        ["HR2_DefectDetected", "IN", "BOOL", "From AI service"],
        ["HR3_ConfidencePctX10", "IN", "INT", "0-1000"],
        ["HR4_DefectClassID", "IN", "INT", "0-3"],
        ["HR5_AIHeartbeat", "IN", "INT", "Watchdog input"],
        ["HR6_AIResultReady", "IN", "BOOL", "Handshake flag"],
        ["HR0_ItemTriggerCounter", "OUT", "INT", "To AI service"],
        ["HR6_Clear_Ack", "OUT", "BOOL", "Consumption pulse"],
        ["DO_DiverterArm_Position", "OUT", "INT", "0/1/2"],
        ["Alarm_AI_Offline", "OUT", "BOOL", "Heartbeat stale"],
        ["Alarm_TrackingMismatch", "OUT", "BOOL", "Timing cross-check"],
        ["Alarm_QueueFull", "OUT", "BOOL", "Depth-5 limit"],
        ["SystemStatus", "OUT", "STRING", "HMI display"],
    ],
    col_widths=[62 * mm, 14 * mm, 22 * mm, AVAIL_W - 62 * mm - 14 * mm - 22 * mm]))
story.append(PageBreak())

# ---- Appendix B: Full ST Listing -------------------------------------------
story += chapter_head("B", "Appendix B &mdash; Full Structured Text Listing", "APPENDIX")
story.append(P("Complete, unedited listing of <b>src/AI_SortingMatrix.st</b>.", body))

story += code_block(
"""(*
====================================================================================
  PROJECT   : AI-Driven Edge Vision Integration
              PLC-Controlled Neural Network Sorting Matrix
  MODULE    : FB_AI_SortingMatrix
  PLATFORM  : IEC 61131-3 Structured Text (Siemens SCL / CODESYS-portable)
  AUTHOR    : Sipho Lucky Sibanda
  See Chapter 5 for the confidence-threshold and watchdog philosophy,
  and Chapter 7 for the genuinely executed Python-side integration test.
====================================================================================
*)

TYPE E_SortRoute : (ROUTE_NONE, ROUTE_PASS, ROUTE_REJECT, ROUTE_MANUAL_REVIEW); END_TYPE

TYPE ST_TrackedItem :
STRUCT
    Active : BOOL;               ItemID : INT;
    ResultReceived : BOOL;
    Defect_Detected : BOOL;        Confidence_Pct : REAL;
    Defect_Class_ID : INT;
    TransitTimer : TON;
END_STRUCT
END_TYPE

FUNCTION_BLOCK FB_AI_SortingMatrix
VAR_INPUT
    DI_ItemPresent_InspectionPoint : BOOL;
    DI_ItemPresent_DiverterPoint : BOOL;
    HR1_ItemIDAck : INT;              HR2_DefectDetected : BOOL;
    HR3_ConfidencePctX10 : INT;         HR4_DefectClassID : INT;
    HR5_AIHeartbeat : INT;                HR6_AIResultReady : BOOL;
    DI_System_Enable : BOOL;
END_VAR

VAR_OUTPUT
    HR0_ItemTriggerCounter : INT := 0;      HR6_Clear_Ack : BOOL := FALSE;
    DO_DiverterArm_Position : INT := 0;
    Alarm_AI_Offline : BOOL := FALSE;
    Alarm_TrackingMismatch : BOOL := FALSE;
    Alarm_QueueFull : BOOL := FALSE;
    ItemsSorted_Pass : DINT := 0;      ItemsSorted_Reject : DINT := 0;
    ItemsSorted_ManualReview : DINT := 0;
    SystemStatus : STRING[24] := 'STANDBY';
END_VAR

VAR
    HighConfidence_Pct : REAL := 90.0;    LowConfidence_Pct : REAL := 60.0;
    TransitDelay_PT : TIME := T#8S;         HeartbeatTimeout_PT : TIME := T#2S;
    Queue : ARRAY[0..4] OF ST_TrackedItem;
    QueueDepth : INT := 5;    i : INT;    FreeSlotFound : BOOL;
    Prev_InspectionSensor : BOOL;    Prev_AIHeartbeat : INT;
    T_HeartbeatWatch : TON;
    HeadIdx : INT;    CurrentRoute : E_SortRoute;
END_VAR""")

story += code_block(
"""// 1. NEW ITEM DETECTION
IF DI_System_Enable AND DI_ItemPresent_InspectionPoint AND (NOT Prev_InspectionSensor) THEN
    HR0_ItemTriggerCounter := HR0_ItemTriggerCounter + 1;
    FreeSlotFound := FALSE;
    FOR i := 0 TO QueueDepth - 1 DO
        IF (NOT Queue[i].Active) AND (NOT FreeSlotFound) THEN
            Queue[i].Active := TRUE;
            Queue[i].ItemID := HR0_ItemTriggerCounter;
            Queue[i].ResultReceived := FALSE;
            Queue[i].TransitTimer(IN := TRUE, PT := TransitDelay_PT);
            FreeSlotFound := TRUE;
        END_IF
    END_FOR
    IF NOT FreeSlotFound THEN Alarm_QueueFull := TRUE; END_IF
END_IF
Prev_InspectionSensor := DI_ItemPresent_InspectionPoint;

// 2. MATCH INCOMING AI RESULTS TO A TRACKED ITEM
HR6_Clear_Ack := FALSE;
IF HR6_AIResultReady THEN
    FOR i := 0 TO QueueDepth - 1 DO
        IF Queue[i].Active AND (Queue[i].ItemID = HR1_ItemIDAck) AND (NOT Queue[i].ResultReceived) THEN
            Queue[i].ResultReceived := TRUE;
            Queue[i].Defect_Detected := HR2_DefectDetected;
            Queue[i].Confidence_Pct := INT_TO_REAL(HR3_ConfidencePctX10) / 10.0;
            Queue[i].Defect_Class_ID := HR4_DefectClassID;
        END_IF
    END_FOR
    HR6_Clear_Ack := TRUE;
END_IF

// 3. AI HEARTBEAT WATCHDOG
IF HR5_AIHeartbeat <> Prev_AIHeartbeat THEN
    T_HeartbeatWatch(IN := FALSE);
    Alarm_AI_Offline := FALSE;
ELSE
    T_HeartbeatWatch(IN := TRUE, PT := HeartbeatTimeout_PT);
    IF T_HeartbeatWatch.Q THEN Alarm_AI_Offline := TRUE; END_IF
END_IF
Prev_AIHeartbeat := HR5_AIHeartbeat;""")

story += code_block(
"""// 4. QUEUE HEAD ARRIVAL AND ROUTING DECISION
FOR i := 0 TO QueueDepth - 1 DO
    Queue[i].TransitTimer(IN := Queue[i].Active, PT := TransitDelay_PT);
    IF Queue[i].Active AND Queue[i].TransitTimer.Q THEN
        IF (NOT Queue[i].ResultReceived) OR Alarm_AI_Offline THEN
            CurrentRoute := ROUTE_MANUAL_REVIEW;
        ELSIF Queue[i].Confidence_Pct < LowConfidence_Pct THEN
            CurrentRoute := ROUTE_MANUAL_REVIEW;
        ELSIF Queue[i].Confidence_Pct < HighConfidence_Pct THEN
            CurrentRoute := ROUTE_MANUAL_REVIEW;
        ELSIF Queue[i].Defect_Detected THEN
            CurrentRoute := ROUTE_REJECT;
        ELSE
            CurrentRoute := ROUTE_PASS;
        END_IF

        CASE CurrentRoute OF
            ROUTE_PASS:           DO_DiverterArm_Position := 0; ItemsSorted_Pass := ItemsSorted_Pass + 1;
            ROUTE_REJECT:         DO_DiverterArm_Position := 1; ItemsSorted_Reject := ItemsSorted_Reject + 1;
            ROUTE_MANUAL_REVIEW:  DO_DiverterArm_Position := 2; ItemsSorted_ManualReview := ItemsSorted_ManualReview + 1;
            ELSE ;
        END_CASE

        Alarm_TrackingMismatch := Alarm_TrackingMismatch
                                    OR (Queue[i].TransitTimer.Q AND (NOT DI_ItemPresent_DiverterPoint));
        Queue[i].Active := FALSE;
        Queue[i].TransitTimer(IN := FALSE);
    END_IF
END_FOR

// 5. STATUS TEXT
IF NOT DI_System_Enable THEN SystemStatus := 'STANDBY';
ELSIF Alarm_AI_Offline THEN SystemStatus := 'AI OFFLINE - MANUAL ONLY';
ELSIF Alarm_QueueFull THEN SystemStatus := 'QUEUE FULL';
ELSE SystemStatus := 'SORTING ACTIVE';
END_IF

END_FUNCTION_BLOCK""", "Listing B.1 &mdash; Complete FB_AI_SortingMatrix source.")
story.append(PageBreak())

# ---- Appendix C: Key Python Listings ---------------------------------------
story += chapter_head("C", "Appendix C &mdash; Key Python Listings", "APPENDIX")
story.append(P(
    "Selected excerpts from the genuinely functional Python side. Full source is in "
    "<b>python/</b> in the repository.", body))
story.append(subhead("C.1 &nbsp; The TinyMLP forward and training step"))
story += code_block(
"""class TinyMLP:
    def __init__(self, n_in=5, n_hidden=8, n_out=2, seed=42):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, 0.5, size=(n_in, n_hidden))
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.normal(0, 0.5, size=(n_hidden, n_out))
        self.b2 = np.zeros(n_out)

    def forward(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = np.maximum(0, z1)  # ReLU
        z2 = a1 @ self.W2 + self.b2
        z2 = z2 - np.max(z2, axis=-1, keepdims=True)
        exp = np.exp(z2)
        probs = exp / np.sum(exp, axis=-1, keepdims=True)
        return probs, (X, z1, a1)

    def train_step(self, X, y_onehot, lr=0.05):
        probs, (X_in, z1, a1) = self.forward(X)
        n = X.shape[0]
        dz2 = (probs - y_onehot) / n
        dW2 = a1.T @ dz2
        da1 = dz2 @ self.W2.T
        dz1 = da1 * (z1 > 0)
        dW1 = X_in.T @ dz1
        self.W1 -= lr * dW1;  self.W2 -= lr * dW2
        loss = -np.mean(np.sum(y_onehot * np.log(probs + 1e-9), axis=1))
        return loss""", "Listing C.1 &mdash; From vision_model.py - hand-written forward pass and backprop.")

story.append(subhead("C.2 &nbsp; The Modbus TCP client polling loop"))
story += code_block(
"""while True:
    heartbeat = (heartbeat + 1) % 65536
    client.write_register(HR_AI_HEARTBEAT, heartbeat, device_id=1)

    rr = client.read_holding_registers(HR_ITEM_TRIGGER, count=1, device_id=1)
    current_counter = rr.registers[0]

    if current_counter != last_seen_counter and current_counter != 0:
        item_id = current_counter
        last_seen_counter = current_counter

        defect_detected, confidence, defect_class = run_inference(
            model, mu, sigma, rng, defect_type_truth
        )
        client.write_registers(HR_ITEM_ID_ACK,
            [item_id, 1 if defect_detected else 0,
             int(round(confidence * 1000)), class_id], device_id=1)
        client.write_register(HR_AI_RESULT_READY, 1, device_id=1)

    time.sleep(POLL_INTERVAL_S)""", "Listing C.2 &mdash; From ai_sorting_service.py - the real Python-to-PLC handshake loop.")
story.append(PageBreak())

# ---- Appendix D: Glossary --------------------------------------------------
story += chapter_head("D", "Appendix D &mdash; Glossary", "APPENDIX")
story.append(data_table(
    ["Term", "Meaning"],
    [
        ["Edge AI", "Running inference on hardware physically close to the process, not in the cloud"],
        ["MLP", "Multi-Layer Perceptron &mdash; the basic feedforward neural network architecture used here"],
        ["Modbus TCP", "A widely-used industrial protocol for exchanging register data over Ethernet"],
        ["Holding register", "A 16-bit read/write memory location in the Modbus data model"],
        ["Heartbeat", "A value one system increments continuously so another can detect if it stops"],
        ["Confidence threshold", "A minimum model certainty required before acting on its output automatically"],
        ["Watchdog", "Logic that detects the absence of an expected periodic signal and reacts safely"],
        ["Softmax", "A function converting raw network outputs into a valid probability distribution"],
        ["ReLU", "Rectified Linear Unit &mdash; a common neural network activation function"],
        ["FIFO / tracking queue", "A structure that preserves the order/identity of items as they move through a process"],
    ],
    col_widths=[38 * mm, AVAIL_W - 38 * mm]))
story.append(PageBreak())

# ---- About the Author -------------------------------------------------------
story += chapter_head("&mdash;", "About the Author", "CLOSING")
story.append(P(
    "<b>Sipho Lucky Sibanda</b> is an automation and controls engineer building a "
    "multi-disciplinary portfolio spanning marine systems, avionics, architectural "
    "technology, applied AI, and industrial automation. This manual documents the third "
    "deliberate discipline shift in that portfolio, and the first to include a genuinely "
    "executable, tested integration alongside the PLC-side Structured Text &mdash; "
    "following the same documentation standard as every other project in the series: full "
    "logic, I/O documentation, a live HMI, functional test procedures, and an honest "
    "account of what separates a strong demonstration from a certifiable production "
    "system.", lead))
story.append(P("Repository: <b>ai-vision-sorting</b>", body))
story.append(Spacer(1, 20))
story.append(HRFlowable(width="40%", thickness=1, color=VIOLETACC))
story.append(Spacer(1, 6))
story.append(P("End of document.", caption))

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
doc = SimpleDocTemplate(
    OUTFILE, pagesize=A4,
    leftMargin=MARGIN_L, rightMargin=MARGIN_R,
    topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOT,
    title="AI-Driven Edge Vision Integration - Technical Manual",
    author=AUTHOR,
)
doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_body)
print("Built:", OUTFILE)
