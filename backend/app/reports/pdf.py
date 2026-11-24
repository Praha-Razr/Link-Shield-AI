import os
import io
import html
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Register Unicode fonts: NotoSans as DEFAULT Latin font, NotoSansDevanagari for Devanagari runs
FONT_NAME = "NotoSans"
FONT_NAME_BOLD = "NotoSans-Bold"
DEV_FONT_NAME = "NotoSansDevanagari"
DEV_FONT_NAME_BOLD = "NotoSansDevanagari-Bold"
MONO_FONT = "Courier"

def init_fonts():
    global FONT_NAME, FONT_NAME_BOLD, DEV_FONT_NAME, DEV_FONT_NAME_BOLD, MONO_FONT

    fonts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fonts"))
    ns_reg = os.path.join(fonts_dir, "NotoSans-Regular.ttf")
    ns_bold = os.path.join(fonts_dir, "NotoSans-Bold.ttf")
    dev_reg = os.path.join(fonts_dir, "NotoSansDevanagari-Regular.ttf")
    dev_bold = os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf")

    # 1. Primary NotoSans (Default Latin font for English, numbers, symbols, and formatting)
    if os.path.exists(ns_reg):
        try:
            pdfmetrics.registerFont(TTFont("NotoSans", ns_reg))
            if os.path.exists(ns_bold):
                pdfmetrics.registerFont(TTFont("NotoSans-Bold", ns_bold))
                registerFontFamily("NotoSans", normal="NotoSans", bold="NotoSans-Bold", italic="NotoSans", boldItalic="NotoSans-Bold")
                FONT_NAME = "NotoSans"
                FONT_NAME_BOLD = "NotoSans-Bold"
            else:
                registerFontFamily("NotoSans", normal="NotoSans", bold="NotoSans", italic="NotoSans", boldItalic="NotoSans")
                FONT_NAME = "NotoSans"
                FONT_NAME_BOLD = "NotoSans"
        except Exception:
            FONT_NAME = "Helvetica"
            FONT_NAME_BOLD = "Helvetica-Bold"
    else:
        FONT_NAME = "Helvetica"
        FONT_NAME_BOLD = "Helvetica-Bold"

    # 2. Bundled Noto Sans Devanagari (Hindi script typography)
    if os.path.exists(dev_reg):
        try:
            pdfmetrics.registerFont(TTFont("NotoSansDevanagari", dev_reg))
            if os.path.exists(dev_bold):
                pdfmetrics.registerFont(TTFont("NotoSansDevanagari-Bold", dev_bold))
                registerFontFamily("NotoSansDevanagari", normal="NotoSansDevanagari", bold="NotoSansDevanagari-Bold", italic="NotoSansDevanagari", boldItalic="NotoSansDevanagari-Bold")
                DEV_FONT_NAME = "NotoSansDevanagari"
                DEV_FONT_NAME_BOLD = "NotoSansDevanagari-Bold"
            else:
                registerFontFamily("NotoSansDevanagari", normal="NotoSansDevanagari", bold="NotoSansDevanagari", italic="NotoSansDevanagari", boldItalic="NotoSansDevanagari")
                DEV_FONT_NAME = "NotoSansDevanagari"
                DEV_FONT_NAME_BOLD = "NotoSansDevanagari"
        except Exception:
            pass

    # 3. Monospace fonts for clean monospace hashes (Linux + Windows font paths)
    mono_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/lucon.ttf"
    ]
    for mono_path in mono_candidates:
        if os.path.exists(mono_path):
            try:
                fid = "Consolas" if "consola" in mono_path.lower() else "MonoFont"
                pdfmetrics.registerFont(TTFont(fid, mono_path))
                MONO_FONT = fid
                break
            except Exception:
                pass

init_fonts()

IST = timezone(timedelta(hours=5, minutes=30))

# Matches contiguous Devanagari character sequences (U+0900-U+097F including dandas, plus U+A8E0-U+A8FF)
DEVANAGARI_RUN_PATTERN = re.compile(
    r'([\u0900-\u097F\uA8E0-\uA8FF]+(?:\s+[\u0900-\u097F\uA8E0-\uA8FF]+)*)'
)

def wrap_devanagari(text: str, is_bold: bool = False) -> str:
    """
    Wraps only Devanagari runs (U+0900-U+097F, danda characters, and Devanagari extended)
    in <font name="NotoSansDevanagari">...</font> or bold variant.
    Keeps English letters, numbers, punctuation, hashes, and URLs in the default Latin font (NotoSans).
    Respects inline <b> / <strong> tags to select the bold font variant automatically.
    """
    if not text:
        return ""

    # Split on bold tags to accurately preserve bold styling across runs
    parts = re.split(r'(<b>|</b>|<strong>|</strong>)', text, flags=re.IGNORECASE)
    result = []
    in_bold = is_bold
    for part in parts:
        low = part.lower()
        if low in ('<b>', '<strong>'):
            in_bold = True
            result.append(part)
        elif low in ('</b>', '</strong>'):
            in_bold = is_bold
            result.append(part)
        else:
            dev_font = DEV_FONT_NAME_BOLD if in_bold else DEV_FONT_NAME
            wrapped = DEVANAGARI_RUN_PATTERN.sub(rf'<font name="{dev_font}">\1</font>', part)
            result.append(wrapped)
    return "".join(result)

def wrap_unbroken_words(text: str, max_word_len: int = 80) -> str:
    """Break continuous strings longer than max_word_len to prevent table cell overflow without mangling 64-char hashes."""
    if not text:
        return ""
    words = text.split(" ")
    out = []
    for w in words:
        if len(w) > max_word_len:
            chunks = [w[i:i+max_word_len] for i in range(0, len(w), max_word_len)]
            out.append(" ".join(chunks))
        else:
            out.append(w)
    return " ".join(out)

def safe_text(val: Any, max_len: Optional[int] = None, is_bold: bool = False) -> str:
    """
    Escapes user and raw text to prevent ReportLab XML markup parsing errors,
    breaks unbroken continuous strings, and wraps Devanagari runs in NotoSansDevanagari.
    """
    if val is None:
        return ""
    s = str(val).replace("\x00", "")
    if max_len and len(s) > max_len:
        s = s[:max_len] + "... [Truncated for display]"

    # Wrap continuous unbroken tokens without mangling 64-character hashes
    s = wrap_unbroken_words(s, max_word_len=80)
    # HTML escape first so <, >, &, " don't break XML
    s = html.escape(s)
    # Wrap Devanagari runs with font tag AFTER html.escape
    return wrap_devanagari(s, is_bold=is_bold)

def canvas_draw_mixed_string(canv, x: float, y: float, text: str, font_size: float = 7.5, is_bold: bool = False, align: str = "left"):
    """
    Draws text directly on canvas choosing the font per string or run (NotoSans for Latin/numbers/symbols,
    NotoSansDevanagari for Devanagari), since canvas drawing cannot use HTML markup tags.
    """
    latin_font = FONT_NAME_BOLD if is_bold else FONT_NAME
    dev_font = DEV_FONT_NAME_BOLD if is_bold else DEV_FONT_NAME

    registered = pdfmetrics.getRegisteredFontNames()
    if latin_font not in registered:
        latin_font = "Helvetica-Bold" if is_bold else "Helvetica"
    if dev_font not in registered:
        dev_font = latin_font

    # If no Devanagari present, fast single-call draw
    if not any('\u0900' <= ch <= '\u097F' or '\uA8E0' <= ch <= '\uA8FF' for ch in text):
        canv.setFont(latin_font, font_size)
        if align == "right":
            canv.drawRightString(x, y, text)
        elif align == "center":
            canv.drawCentredString(x, y, text)
        else:
            canv.drawString(x, y, text)
        return

    # Split into runs of Devanagari vs Latin
    runs = []
    current_run = []
    current_is_dev = None
    for ch in text:
        is_dev = ('\u0900' <= ch <= '\u097F' or '\uA8E0' <= ch <= '\uA8FF')
        if current_is_dev is None or is_dev == current_is_dev:
            current_run.append(ch)
            current_is_dev = is_dev
        else:
            runs.append(("".join(current_run), current_is_dev))
            current_run = [ch]
            current_is_dev = is_dev
    if current_run:
        runs.append(("".join(current_run), current_is_dev))

    total_width = 0
    run_widths = []
    for run_text, is_dev in runs:
        fn = dev_font if is_dev else latin_font
        w = pdfmetrics.stringWidth(run_text, fn, font_size)
        run_widths.append(w)
        total_width += w

    cur_x = x
    if align == "right":
        cur_x = x - total_width
    elif align == "center":
        cur_x = x - (total_width / 2.0)

    for (run_text, is_dev), w in zip(runs, run_widths):
        fn = dev_font if is_dev else latin_font
        canv.setFont(fn, font_size)
        canv.drawString(cur_x, y, run_text)
        cur_x += w

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count, watermark, and footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()

        # Watermark for Demo Data
        is_demo = getattr(self, "is_demo_report", False)
        if is_demo:
            self.setFillColor(colors.HexColor("#CBD5E1"), alpha=0.25)
            self.translate(297, 420)
            self.rotate(45)
            canvas_draw_mixed_string(self, 0, 0, "DEMO EVALUATION DATA", font_size=48, is_bold=True, align="center")
            canvas_draw_mixed_string(self, 0, -30, "SYNTHETIC BENCHMARK RECORD", font_size=14, is_bold=True, align="center")
            self.rotate(-45)
            self.translate(-297, -420)

        # Running Footer
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 32, 559, 32)

        canvas_draw_mixed_string(
            self, 36, 22,
            "LINKSHIELD AI - Investigation Support Report | Confidential - Law Enforcement & Cyber Cell Use",
            font_size=7.5, is_bold=False, align="left"
        )
        page_str = f"Page {self._pageNumber} of {page_count}"
        canvas_draw_mixed_string(self, 559, 22, page_str, font_size=7.5, is_bold=False, align="right")

        self.restoreState()

def generate_case_pdf_report(case_data: Dict[str, Any]) -> bytes:
    """
    Generates a forensic intelligence dossier for a cybercrime investigation case.
    Engineered with exact typography leading and TrueType Unicode fonts (Nirmala UI)
    to eliminate font misalignments, line overlays, and non-ASCII character errors.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=42
    )

    CONTENT_WIDTH = 523  # A4 width (595.27) - 72

    # Dedicated paragraph styles with exact matching leading (never causes overlaid lines!)
    header_title_style = ParagraphStyle(
        "HeaderTitle",
        fontName=FONT_NAME_BOLD,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#FFFFFF")
    )
    header_sub_style = ParagraphStyle(
        "HeaderSub",
        fontName=FONT_NAME_BOLD,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#38BDF8")
    )
    header_status_style = ParagraphStyle(
        "HeaderStatus",
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#94A3B8")
    )

    meta_key_style = ParagraphStyle(
        "MetaKey",
        fontName=FONT_NAME_BOLD,
        fontSize=7.5,
        leading=11,
        textColor=colors.HexColor("#475569")
    )
    meta_val_style = ParagraphStyle(
        "MetaVal",
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    risk_badge_title_style = ParagraphStyle(
        "RiskBadgeTitle",
        fontName=FONT_NAME_BOLD,
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#64748B"),
        alignment=1
    )
    risk_sub_style = ParagraphStyle(
        "RiskSub",
        fontName=FONT_NAME,
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#64748B"),
        alignment=1
    )

    sec_head_style = ParagraphStyle(
        "SecHead",
        fontName=FONT_NAME_BOLD,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )

    table_th_style = ParagraphStyle(
        "TableTH",
        fontName=FONT_NAME_BOLD,
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )
    table_td_style = ParagraphStyle(
        "TableTD",
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#334155")
    )
    table_td_bold_style = ParagraphStyle(
        "TableTDBold",
        fontName=FONT_NAME_BOLD,
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )

    excerpt_style = ParagraphStyle(
        "ExcerptStyle",
        fontName=FONT_NAME,
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1E293B")
    )

    rec_style = ParagraphStyle(
        "RecStyle",
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#1E293B")
    )
    notes_style = ParagraphStyle(
        "NotesStyle",
        fontName=FONT_NAME,
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#334155")
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerStyle",
        fontName=FONT_NAME,
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#64748B")
    )

    story = []

    # 1. HEADER BANNER
    is_demo = case_data.get("is_demo", False)
    status_html = "<font color='#F87171'><b>[DEMO EVALUATION DATA]</b></font>" if is_demo else "<font color='#38BDF8'><b>[OFFICIAL INVESTIGATION DOSSIER]</b></font>"

    header_cells = [
        [Paragraph(wrap_devanagari("LINKSHIELD AI &mdash; CYBER CRIME INVESTIGATION REPORT", is_bold=True), header_title_style)],
        [Paragraph(wrap_devanagari("Detect. Explain. Investigate. Protect.", is_bold=True), header_sub_style)],
        [Paragraph(wrap_devanagari(f"Forensic Classification: {status_html}"), header_status_style)]
    ]
    header_table = Table(header_cells, colWidths=[CONTENT_WIDTH])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 7))

    # 2. CASE METADATA & RISK BADGE
    case_id = safe_text(case_data.get("id", case_data.get("case_id", "UNKNOWN")), is_bold=True)
    subject = safe_text(case_data.get("subject", "Unspecified Incident"))
    input_type = safe_text(case_data.get("input_type", "message")).upper()
    category = safe_text(case_data.get("category", "general")).replace("_", " ").upper()
    risk_level = str(case_data.get("risk_level", "LOW")).upper()
    risk_score = case_data.get("risk_score", 0)

    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST)
    gen_time_str = f"{now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC / {now_ist.strftime('%Y-%m-%d %H:%M:%S')} IST"

    created_at = case_data.get("created_at")
    if isinstance(created_at, datetime):
        cap_utc = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
        cap_ist = cap_utc.astimezone(IST)
        cap_time_str = f"{cap_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC ({cap_ist.strftime('%Y-%m-%d %H:%M')} IST)"
    elif isinstance(created_at, str):
        cap_time_str = safe_text(created_at)
    else:
        cap_time_str = "Recorded at submission"

    if risk_level == "HIGH":
        risk_color = colors.HexColor("#DC2626")
        risk_bg = colors.HexColor("#FEF2F2")
        risk_border = colors.HexColor("#F87171")
    elif risk_level == "MEDIUM":
        risk_color = colors.HexColor("#D97706")
        risk_bg = colors.HexColor("#FFFBEB")
        risk_border = colors.HexColor("#FBBF24")
    else:
        risk_color = colors.HexColor("#059669")
        risk_bg = colors.HexColor("#ECFDF5")
        risk_border = colors.HexColor("#34D399")

    # Clean 2-column key-value pairs for metadata
    meta_sub_table = Table([
        [Paragraph(wrap_devanagari("Case Reference ID:", is_bold=True), meta_key_style), Paragraph(f"<b>{case_id}</b>", meta_val_style)],
        [Paragraph(wrap_devanagari("Incident Subject:", is_bold=True), meta_key_style), Paragraph(subject, meta_val_style)],
        [Paragraph(wrap_devanagari("Input / Category:", is_bold=True), meta_key_style), Paragraph(f"{input_type} &nbsp;|&nbsp; {category}", meta_val_style)],
        [Paragraph(wrap_devanagari("Captured Timestamp:", is_bold=True), meta_key_style), Paragraph(cap_time_str, meta_val_style)],
        [Paragraph(wrap_devanagari("Report Generated:", is_bold=True), meta_key_style), Paragraph(gen_time_str, meta_val_style)],
    ], colWidths=[105, 275])
    meta_sub_table.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    risk_badge_level_style = ParagraphStyle(
        "RiskBadgeLevel",
        fontName=FONT_NAME_BOLD,
        fontSize=13,
        leading=16,
        textColor=risk_color,
        alignment=1
    )
    risk_score_style = ParagraphStyle(
        "RiskScoreStyle",
        fontName=FONT_NAME_BOLD,
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        alignment=1
    )

    risk_badge_title = wrap_devanagari("ASSESSED THREAT LEVEL", is_bold=True)
    risk_badge_level = wrap_devanagari(f"{risk_level} RISK", is_bold=True)
    risk_sub_text = wrap_devanagari("Rule-based explainable score")

    risk_sub_table = Table([
        [Paragraph(risk_badge_title, risk_badge_title_style)],
        [Paragraph(risk_badge_level, risk_badge_level_style)],
        [Paragraph(f"Score: {risk_score} / 100", risk_score_style)],
        [Paragraph(risk_sub_text, risk_sub_style)]
    ], colWidths=[130])
    risk_sub_table.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    top_meta_table = Table([
        [meta_sub_table, risk_sub_table]
    ], colWidths=[385, 138])
    top_meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
        ("BACKGROUND", (1, 0), (1, 0), risk_bg),
        ("BOX", (0, 0), (0, 0), 1, colors.HexColor("#E2E8F0")),
        ("BOX", (1, 0), (1, 0), 1.5, risk_border),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(top_meta_table)
    story.append(Spacer(1, 7))

    # 3. EVIDENCE & SUBMITTED EXCERPT
    sha256_hash = safe_text(case_data.get("content_sha256", "Not recorded"))
    raw_content = str(case_data.get("raw_content") or "")
    safe_excerpt = safe_text(raw_content, max_len=1200)
    if len(raw_content) > 1200:
        safe_excerpt += "... [Truncated for display]"

    story.append(Paragraph(wrap_devanagari("<b>1. Chain of Custody & Evidence Verification</b>", is_bold=True), sec_head_style))
    story.append(Spacer(1, 2.5))

    evidence_table = Table([
        [Paragraph(f"<b>SHA-256 Fingerprint:</b> &nbsp;<font face='{MONO_FONT}'>{sha256_hash}</font>", excerpt_style)],
        [Paragraph(wrap_devanagari(f"<b>Submitted Content Excerpt:</b><br/>{safe_excerpt}"), excerpt_style)]
    ], colWidths=[CONTENT_WIDTH])
    evidence_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(evidence_table)
    story.append(Spacer(1, 7))

    # 4. EXPLAINABLE THREAT INDICATORS
    indicators = case_data.get("indicators", [])
    story.append(Paragraph(wrap_devanagari(f"<b>2. Explainable Threat Indicators ({len(indicators)})</b>", is_bold=True), sec_head_style))
    story.append(Spacer(1, 2.5))

    if indicators:
        ind_data = [
            [
                Paragraph(wrap_devanagari("<b>Indicator Name</b>", is_bold=True), table_th_style),
                Paragraph(wrap_devanagari("<b>Points</b>", is_bold=True), table_th_style),
                Paragraph(wrap_devanagari("<b>Forensic Explanation / Why Flagged</b>", is_bold=True), table_th_style)
            ]
        ]
        for ind in indicators:
            ind_name = safe_text(ind.get("name", "Indicator"), is_bold=True)
            ind_pts = f"+{ind.get('points', 0)}"
            ind_exp = safe_text(ind.get("explanation", ""))
            ind_data.append([
                Paragraph(ind_name, table_td_bold_style),
                Paragraph(f"<b>{ind_pts}</b>", table_td_bold_style),
                Paragraph(ind_exp, table_td_style)
            ])

        ind_table = Table(ind_data, colWidths=[140, 45, 338], repeatRows=1)
        ind_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(ind_table)
    else:
        story.append(Paragraph(wrap_devanagari("<i>No suspicious threat indicators triggered for this record.</i>"), table_td_style))

    story.append(Spacer(1, 7))

    # 5. EXTRACTED NETWORK IDENTIFIERS
    identifiers = case_data.get("identifiers", [])
    story.append(Paragraph(wrap_devanagari(f"<b>3. Extracted Network & Financial Identifiers ({len(identifiers)})</b>", is_bold=True), sec_head_style))
    story.append(Spacer(1, 2.5))

    if identifiers:
        ident_data = [
            [
                Paragraph(wrap_devanagari("<b>Identifier Type</b>", is_bold=True), table_th_style),
                Paragraph(wrap_devanagari("<b>Extracted Value</b>", is_bold=True), table_th_style)
            ]
        ]
        for ident in identifiers:
            itype = safe_text(ident.get("type", "unknown"), is_bold=True).upper()
            ival = safe_text(ident.get("value", ""))
            ident_data.append([
                Paragraph(f"<b>{itype}</b>", table_td_bold_style),
                Paragraph(ival, table_td_style)
            ])

        ident_table = Table(ident_data, colWidths=[140, 383])
        ident_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(ident_table)
    else:
        story.append(Paragraph(wrap_devanagari("<i>No actionable phone numbers, UPI IDs, domains or wallets found.</i>"), table_td_style))

    story.append(Spacer(1, 7))

    # 6. CROSS-CASE LINKAGES & INTELLIGENCE
    related_cases = case_data.get("related_cases", [])
    similarity_links = case_data.get("similarity_links", [])
    story.append(Paragraph(wrap_devanagari("<b>4. Cross-Case Linkages & Campaign Intelligence</b>", is_bold=True), sec_head_style))
    story.append(Spacer(1, 2.5))

    if not related_cases and not similarity_links:
        story.append(Paragraph(wrap_devanagari("<i>No cross-case identifier linkages or near-duplicate content discovered.</i>"), table_td_style))
    else:
        link_rows = [
            [
                Paragraph(wrap_devanagari("<b>Linked Case</b>", is_bold=True), table_th_style),
                Paragraph(wrap_devanagari("<b>Link Type / Reason</b>", is_bold=True), table_th_style),
                Paragraph(wrap_devanagari("<b>Subject / Risk</b>", is_bold=True), table_th_style)
            ]
        ]
        for rc in related_cases:
            rc_id = safe_text(rc.get("case_id"), is_bold=True)
            shared_ids = safe_text(", ".join(rc.get("shared_identifiers", [])))
            rc_subj = safe_text(rc.get("subject", ""))
            rc_risk = safe_text(rc.get("risk_level", ""))
            link_rows.append([
                Paragraph(f"<b>{rc_id}</b>", table_td_bold_style),
                Paragraph(wrap_devanagari(f"Shared Identifier: {shared_ids}"), table_td_style),
                Paragraph(wrap_devanagari(f"{rc_subj} ({rc_risk})"), table_td_style)
            ])

        for sl in similarity_links:
            sl_id = safe_text(sl.get("case_id"), is_bold=True)
            sim_pct = int(sl.get("similarity", 0) * 100)
            sl_subj = safe_text(sl.get("subject", ""))
            link_rows.append([
                Paragraph(f"<b>{sl_id}</b>", table_td_bold_style),
                Paragraph(wrap_devanagari(f"Near-Duplicate Content: {sim_pct}% Match"), table_td_style),
                Paragraph(sl_subj, table_td_style)
            ])

        links_table = Table(link_rows, colWidths=[100, 223, 200], repeatRows=1)
        links_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(links_table)

    story.append(Spacer(1, 7))

    # 7. INVESTIGATOR NOTES
    notes_raw = case_data.get("investigator_notes")
    notes = safe_text(notes_raw if notes_raw else "No official investigator notes recorded for this case.", max_len=1500)
    story.append(Paragraph(wrap_devanagari("<b>5. Investigator Notes & Police Remarks</b>", is_bold=True), sec_head_style))
    story.append(Spacer(1, 2.5))

    notes_table = Table([[Paragraph(notes, notes_style)]], colWidths=[CONTENT_WIDTH])
    notes_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(notes_table)
    story.append(Spacer(1, 7))

    # AI SECOND OPINION (Advisory)
    ai_op = case_data.get("ai_second_opinion")
    if isinstance(ai_op, str):
        try:
            ai_op = json.loads(ai_op)
        except Exception:
            ai_op = None

    sec_rec_num = 6
    if ai_op and isinstance(ai_op, dict) and ai_op.get("status"):
        sec_rec_num = 7
        story.append(Paragraph(wrap_devanagari("<b>6. AI Second Opinion (Advisory)</b>", is_bold=True), sec_head_style))
        story.append(Spacer(1, 2.5))

        status = ai_op.get("status", "ok")
        if status == "ok":
            scam_like = ai_op.get("scam_likelihood", "low").upper()
            conf = int(ai_op.get("confidence", 0) * 100)
            reasons = ai_op.get("reasons", [])
            cat = ai_op.get("category") or "General"
            brand = ai_op.get("impersonated_brand")
            brand_str = f" | Brand: <b>{safe_text(brand)}</b>" if brand else ""
            reasons_html = "".join([f"&bull;&nbsp; {safe_text(r)}<br/>" for r in reasons]) if reasons else "No specific anomaly reasons reported."

            opinion_html = (
                f"<b>Assessed Likelihood:</b> {scam_like} (Confidence: {conf}%) | Category: <b>{safe_text(cat)}</b>{brand_str}<br/>"
                f"<b>Forensic AI Reasoning:</b><br/>{reasons_html}"
                f"<i>Note: {safe_text(ai_op.get('disclaimer', 'AI opinion, verify manually'))}</i>"
            )
        elif status == "skipped":
            reasons_list = ai_op.get("reasons") or ["Verified genuine official domain"]
            opinion_html = f"<b>Status:</b> Skipped | <i>{safe_text(reasons_list[0])}</i>"
        else:
            opinion_html = f"<b>Status:</b> {safe_text(ai_op.get('error', 'AI second opinion unavailable'))}"

        op_table = Table([[Paragraph(wrap_devanagari(opinion_html), notes_style)]], colWidths=[CONTENT_WIDTH])
        op_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(op_table)
        story.append(Spacer(1, 7))

    # 8. ACTIONABLE SAFETY RECOMMENDATIONS
    recommendations = case_data.get("safety_recommendations", [])
    if not recommendations:
        from app.risk.engine import get_safety_recommendations
        recommendations = get_safety_recommendations(risk_level)

    story.append(Paragraph(wrap_devanagari(f"<b>{sec_rec_num}. Actionable Safety Recommendations</b>", is_bold=True), sec_head_style))
    story.append(Spacer(1, 2.5))

    rec_items = "".join([f"&bull;&nbsp; {safe_text(r)}<br/>" for r in recommendations])
    rec_table = Table([[Paragraph(rec_items, rec_style)]], colWidths=[CONTENT_WIDTH])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 7))

    # 9. STATUTORY DISCLAIMER
    disclaimer_text = (
        "<b>STATUTORY DISCLAIMER:</b> Automated analysis for investigation support. "
        "Findings must be verified by a human investigator. "
        "Detection scores reflect pattern matching against known fraud indicators and do not constitute legal proof. "
        "Generated by LINKSHIELD AI &mdash; Detect. Explain. Investigate. Protect."
    )
    story.append(Paragraph(wrap_devanagari(disclaimer_text), disclaimer_style))

    def on_page_setup(canvas_obj, document):
        canvas_obj.is_demo_report = is_demo

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
