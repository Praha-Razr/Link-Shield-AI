import os
import io
import html
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

# Register Unicode fonts (Nirmala UI for Indic & Latin scripts, Consolas for hashes)
FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"
MONO_FONT = "Courier"

def init_fonts():
    global FONT_NAME, FONT_NAME_BOLD, MONO_FONT
    # 1. Nirmala UI (Windows official font supporting Devanagari, Bengali, Tamil, Telugu, Latin, etc.)
    nirmala_ttc = "C:/Windows/Fonts/Nirmala.ttc"
    if os.path.exists(nirmala_ttc):
        try:
            pdfmetrics.registerFont(TTFont("Nirmala", nirmala_ttc, subfontIndex=0))
            pdfmetrics.registerFont(TTFont("Nirmala-Bold", nirmala_ttc, subfontIndex=1))
            registerFontFamily("Nirmala", normal="Nirmala", bold="Nirmala-Bold", italic="Nirmala", boldItalic="Nirmala-Bold")
            FONT_NAME = "Nirmala"
            FONT_NAME_BOLD = "Nirmala-Bold"
        except Exception:
            pass

    # 2. Consolas for clean monospace hashes
    for mono_path in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/lucon.ttf"]:
        if os.path.exists(mono_path):
            try:
                fid = "Consolas" if "consola" in mono_path else "LucidaConsole"
                pdfmetrics.registerFont(TTFont(fid, mono_path))
                MONO_FONT = fid
                break
            except Exception:
                pass

    # 3. Fallback to Arial if Nirmala not found
    if FONT_NAME == "Helvetica":
        arial_ttf = "C:/Windows/Fonts/arial.ttf"
        arial_bd = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(arial_ttf):
            try:
                pdfmetrics.registerFont(TTFont("Arial", arial_ttf))
                if os.path.exists(arial_bd):
                    pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bd))
                    registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial", boldItalic="Arial-Bold")
                    FONT_NAME = "Arial"
                    FONT_NAME_BOLD = "Arial-Bold"
                else:
                    FONT_NAME = "Arial"
                    FONT_NAME_BOLD = "Arial"
            except Exception:
                pass

init_fonts()

IST = timezone(timedelta(hours=5, minutes=30))

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

def safe_text(val: Any, max_len: Optional[int] = None) -> str:
    """Escapes user and raw text to prevent ReportLab XML markup parsing errors."""
    if val is None:
        return ""
    s = str(val).replace("\x00", "")
    if max_len and len(s) > max_len:
        s = s[:max_len] + "... [Truncated for display]"

    # If font is strictly fallback Helvetica (cannot render Unicode), safely convert
    if FONT_NAME == "Helvetica":
        s = s.encode("latin-1", "replace").decode("latin-1")

    # Wrap continuous unbroken tokens without mangling 64-character hashes
    s = wrap_unbroken_words(s, max_word_len=80)
    return html.escape(s)

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
            self.setFont(FONT_NAME_BOLD, 48)
            self.setFillColor(colors.HexColor("#CBD5E1"), alpha=0.25)
            self.translate(297, 420)
            self.rotate(45)
            self.drawCentredString(0, 0, "DEMO EVALUATION DATA")
            self.setFont(FONT_NAME_BOLD, 14)
            self.drawCentredString(0, -30, "SYNTHETIC BENCHMARK RECORD")
            self.rotate(-45)
            self.translate(-297, -420)

        # Running Footer
        footer_font = FONT_NAME if FONT_NAME in pdfmetrics.getRegisteredFontNames() else "Helvetica"
        self.setFont(footer_font, 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 32, 559, 32)

        self.drawString(
            36, 22,
            "LINKSHIELD AI - Investigation Support Report | Confidential - Law Enforcement & Cyber Cell Use"
        )
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 22, page_str)

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
        [Paragraph("LINKSHIELD AI &mdash; CYBER CRIME INVESTIGATION REPORT", header_title_style)],
        [Paragraph("Detect. Explain. Investigate. Protect.", header_sub_style)],
        [Paragraph(f"Forensic Classification: {status_html}", header_status_style)]
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
    case_id = safe_text(case_data.get("id", case_data.get("case_id", "UNKNOWN")))
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
        [Paragraph("Case Reference ID:", meta_key_style), Paragraph(f"<b>{case_id}</b>", meta_val_style)],
        [Paragraph("Incident Subject:", meta_key_style), Paragraph(subject, meta_val_style)],
        [Paragraph("Input / Category:", meta_key_style), Paragraph(f"{input_type} &nbsp;|&nbsp; {category}", meta_val_style)],
        [Paragraph("Captured Timestamp:", meta_key_style), Paragraph(cap_time_str, meta_val_style)],
        [Paragraph("Report Generated:", meta_key_style), Paragraph(gen_time_str, meta_val_style)],
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

    risk_sub_table = Table([
        [Paragraph("ASSESSED THREAT LEVEL", risk_badge_title_style)],
        [Paragraph(f"{risk_level} RISK", risk_badge_level_style)],
        [Paragraph(f"Score: {risk_score} / 100", risk_score_style)],
        [Paragraph("Rule-based explainable score", risk_sub_style)]
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

    story.append(Paragraph("<b>1. Chain of Custody & Evidence Verification</b>", sec_head_style))
    story.append(Spacer(1, 2.5))

    evidence_table = Table([
        [Paragraph(f"<b>SHA-256 Fingerprint:</b> &nbsp;<font face='{MONO_FONT}'>{sha256_hash}</font>", excerpt_style)],
        [Paragraph(f"<b>Submitted Content Excerpt:</b><br/>{safe_excerpt}", excerpt_style)]
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
    story.append(Paragraph(f"<b>2. Explainable Threat Indicators ({len(indicators)})</b>", sec_head_style))
    story.append(Spacer(1, 2.5))

    if indicators:
        ind_data = [
            [
                Paragraph("<b>Indicator Name</b>", table_th_style),
                Paragraph("<b>Points</b>", table_th_style),
                Paragraph("<b>Forensic Explanation / Why Flagged</b>", table_th_style)
            ]
        ]
        for ind in indicators:
            ind_name = safe_text(ind.get("name", "Indicator"))
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
        story.append(Paragraph("<i>No suspicious threat indicators triggered for this record.</i>", table_td_style))

    story.append(Spacer(1, 7))

    # 5. EXTRACTED NETWORK IDENTIFIERS
    identifiers = case_data.get("identifiers", [])
    story.append(Paragraph(f"<b>3. Extracted Network & Financial Identifiers ({len(identifiers)})</b>", sec_head_style))
    story.append(Spacer(1, 2.5))

    if identifiers:
        ident_data = [
            [
                Paragraph("<b>Identifier Type</b>", table_th_style),
                Paragraph("<b>Extracted Value</b>", table_th_style)
            ]
        ]
        for ident in identifiers:
            itype = safe_text(ident.get("type", "unknown")).upper()
            ival = safe_text(ident.get("value", ""))
            ident_data.append([
                Paragraph(f"<b>{itype}</b>", table_td_bold_style),
                Paragraph(ival, table_td_style)  # Uses FONT_NAME (Nirmala), NEVER Courier, so no black boxes!
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
        story.append(Paragraph("<i>No actionable phone numbers, UPI IDs, domains or wallets found.</i>", table_td_style))

    story.append(Spacer(1, 7))

    # 6. CROSS-CASE LINKAGES & INTELLIGENCE
    related_cases = case_data.get("related_cases", [])
    similarity_links = case_data.get("similarity_links", [])
    story.append(Paragraph("<b>4. Cross-Case Linkages & Campaign Intelligence</b>", sec_head_style))
    story.append(Spacer(1, 2.5))

    if not related_cases and not similarity_links:
        story.append(Paragraph("<i>No cross-case identifier linkages or near-duplicate content discovered.</i>", table_td_style))
    else:
        link_rows = [
            [
                Paragraph("<b>Linked Case</b>", table_th_style),
                Paragraph("<b>Link Type / Reason</b>", table_th_style),
                Paragraph("<b>Subject / Risk</b>", table_th_style)
            ]
        ]
        for rc in related_cases:
            rc_id = safe_text(rc.get("case_id"))
            shared_ids = safe_text(", ".join(rc.get("shared_identifiers", [])))
            rc_subj = safe_text(rc.get("subject", ""))
            rc_risk = safe_text(rc.get("risk_level", ""))
            link_rows.append([
                Paragraph(f"<b>{rc_id}</b>", table_td_bold_style),
                Paragraph(f"Shared Identifier: {shared_ids}", table_td_style),
                Paragraph(f"{rc_subj} ({rc_risk})", table_td_style)
            ])

        for sl in similarity_links:
            sl_id = safe_text(sl.get("case_id"))
            sim_pct = int(sl.get("similarity", 0) * 100)
            sl_subj = safe_text(sl.get("subject", ""))
            link_rows.append([
                Paragraph(f"<b>{sl_id}</b>", table_td_bold_style),
                Paragraph(f"Near-Duplicate Content: {sim_pct}% Match", table_td_style),
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
    story.append(Paragraph("<b>5. Investigator Notes & Police Remarks</b>", sec_head_style))
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
        story.append(Paragraph("<b>6. AI Second Opinion (Advisory)</b>", sec_head_style))
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

        op_table = Table([[Paragraph(opinion_html, notes_style)]], colWidths=[CONTENT_WIDTH])
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

    story.append(Paragraph(f"<b>{sec_rec_num}. Actionable Safety Recommendations</b>", sec_head_style))
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
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    def on_page_setup(canvas_obj, document):
        canvas_obj.is_demo_report = is_demo

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
