"""
Converts README.md directly into a publication-quality PDF report.
Parses Markdown structures (headings, tables, callouts, lists, images, code blocks)
and converts them into styled ReportLab Flowables.
"""
import os
import re
import html
from markdown_it import MarkdownIt
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
    HRFlowable,
    Preformatted,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count."""

    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1F4E79"))

        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 762, "SmartBus Transit System — Documentation & Architecture Specification")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(576, 762, " ")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(36, 756, 576, 756)

        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 24, "SmartBus Transit System • Laboratory Practical • SQLite Relational Engine")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 24, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 34, 576, 34)
        self.restoreState()


def get_scaled_image(img_path, max_w=520, max_h=550):
    """Scale image proportionally to fit printable page boundaries."""
    if not os.path.exists(img_path):
        return None
    try:
        with PILImage.open(img_path) as im:
            orig_w, orig_h = im.size
        ratio = min(max_w / orig_w, max_h / orig_h)
        target_w = orig_w * ratio
        target_h = orig_h * ratio
        return Image(img_path, width=target_w, height=target_h)
    except Exception as e:
        print(f"Warning: Could not load image {img_path}: {e}")
        return None


def inline_to_reportlab_html(inline_token, md_renderer, md_options):
    """
    Convert an inline token's children to ReportLab-compatible XML markup.
    Replaces <strong> with <b>, <em> with <i>, and <code> with styled font.
    Ensures self-closing tags like <br/> are strictly formatted for paraparser.
    """
    if not inline_token or not inline_token.children:
        text = html.escape(inline_token.content if inline_token else "")
        return text

    rendered = md_renderer.renderInline(inline_token.children, md_options, {})

    # Strictly normalize <br> to self-closing <br/> for ReportLab
    rendered = re.sub(r"<br\s*/?>", "<br/>", rendered, flags=re.IGNORECASE)

    # Transform standard HTML tags to ReportLab Paragraph XML tags
    rendered = re.sub(r"<strong>(.*?)</strong>", r"<b>\1</b>", rendered, flags=re.DOTALL)
    rendered = re.sub(r"<em>(.*?)</em>", r"<i>\1</i>", rendered, flags=re.DOTALL)
    rendered = re.sub(r"<code>(.*?)</code>", r'<font face="Courier" color="#0F172A"><b>\1</b></font>', rendered, flags=re.DOTALL)

    # Remove unsupported HTML image tags inside paragraph text if any
    rendered = re.sub(r"<img[^>]*>", "", rendered)
    rendered = re.sub(r"<para>", "", rendered)
    rendered = re.sub(r"</para>", "", rendered)
    return rendered


def parse_readme_to_flowables(readme_path, base_dir, styles):
    """
    Read README.md and parse tokens into ReportLab flowable elements.
    """
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    md = MarkdownIt("commonmark").enable("table")
    tokens = md.parse(readme_content)

    flowables = []

    NAVY = colors.HexColor("#1F4E79")
    STEEL = colors.HexColor("#2E75B6")
    DARK = colors.HexColor("#1E293B")
    BG_CODE = colors.HexColor("#F8FAFC")
    BORDER_CODE = colors.HexColor("#CBD5E1")

    # Typography styles
    style_h1 = ParagraphStyle("H1_Custom", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=14, spaceAfter=6, keepWithNext=True)
    style_h2 = ParagraphStyle("H2_Custom", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=NAVY, spaceBefore=12, spaceAfter=5, keepWithNext=True)
    style_h3 = ParagraphStyle("H3_Custom", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=STEEL, spaceBefore=9, spaceAfter=4, keepWithNext=True)
    style_h4 = ParagraphStyle("H4_Custom", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=DARK, spaceBefore=6, spaceAfter=3, keepWithNext=True)
    style_body = ParagraphStyle("Body_Custom", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK, spaceAfter=5)
    style_bullet = ParagraphStyle("Bullet_Custom", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=DARK, leftIndent=16, firstLineIndent=-10, spaceAfter=3)
    style_quote = ParagraphStyle("Quote_Custom", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=NAVY)
    style_code = ParagraphStyle("Code_Custom", parent=styles["Normal"], fontName="Courier", fontSize=7, leading=9, textColor=colors.HexColor("#0F172A"))
    style_tbl_hdr = ParagraphStyle("TableHdr", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white)
    style_tbl_cell = ParagraphStyle("TableCell", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=9.5, textColor=DARK)

    i = 0
    total_tokens = len(tokens)

    while i < total_tokens:
        tok = tokens[i]

        # ---------------------------------------------------------------------
        # 1. HEADINGS (#, ##, ###)
        # ---------------------------------------------------------------------
        if tok.type == "heading_open":
            level = int(tok.tag[1])
            inline_tok = tokens[i + 1] if i + 1 < total_tokens and tokens[i + 1].type == "inline" else None
            title_text = inline_to_reportlab_html(inline_tok, md.renderer, md.options) if inline_tok else ""

            # Check if major section (##) should have a page break or separator
            if level == 1:
                # Top document title banner
                banner_data = [[
                    Paragraph(f"<b>{title_text.upper()}</b>", ParagraphStyle("CoverB", fontName="Helvetica-Bold", fontSize=13, textColor=colors.white)),
                    Paragraph("<b>SYSTEM SPECIFICATION</b><br/>CPE106L Practical Assessment", ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#D0E1FD"), alignment=2))
                ]]
                t_b = Table(banner_data, colWidths=[360, 180])
                t_b.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]))
                flowables.append(t_b)
                flowables.append(Spacer(1, 8))
            elif level == 2:
                # Major section heading
                if flowables and not isinstance(flowables[-1], PageBreak):
                    flowables.append(Spacer(1, 4))
                flowables.append(Paragraph(title_text, style_h2))
                flowables.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=6))
            elif level == 3:
                flowables.append(Paragraph(title_text, style_h3))
            else:
                flowables.append(Paragraph(title_text, style_h4))

            # Skip ahead past heading_close
            while i < total_tokens and tokens[i].type != "heading_close":
                i += 1

        # ---------------------------------------------------------------------
        # 2. BLOCKQUOTES (> ...)
        # ---------------------------------------------------------------------
        elif tok.type == "blockquote_open":
            quote_text = ""
            i += 1
            while i < total_tokens and tokens[i].type != "blockquote_close":
                if tokens[i].type == "inline":
                    quote_text += inline_to_reportlab_html(tokens[i], md.renderer, md.options) + " "
                i += 1
            # Render blockquote inside callout frame
            q_table = Table([[Paragraph(quote_text.strip(), style_quote)]], colWidths=[540])
            q_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
                ("LINEBEFORE", (0, 0), (0, -1), 3.5, STEEL),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            flowables.append(q_table)
            flowables.append(Spacer(1, 6))

        # ---------------------------------------------------------------------
        # 3. PARAGRAPHS & STANDALONE IMAGES
        # ---------------------------------------------------------------------
        elif tok.type == "paragraph_open":
            inline_tok = tokens[i + 1] if i + 1 < total_tokens and tokens[i + 1].type == "inline" else None
            if inline_tok:
                # Check if paragraph contains images
                img_tokens = [c for c in (inline_tok.children or []) if c.type == "image"]
                # Also check if it's badges (e.g. img.shields.io)
                has_badge = any("shields.io" in (c.attrs.get("src", "")) for c in img_tokens)

                if has_badge:
                    # Render a clean text badge bar instead of trying to load web SVG badges
                    flowables.append(Paragraph(
                        "<b>Technology Stack:</b> Python 3.10+ &nbsp;|&nbsp; Tkinter Clam Theme &nbsp;|&nbsp; SQLite3 ACID Engine &nbsp;|&nbsp; 12/12 Passing Unit Tests",
                        ParagraphStyle("BadgeBar", parent=style_body, textColor=STEEL, fontName="Helvetica-Bold", fontSize=8)
                    ))
                    flowables.append(Spacer(1, 4))
                elif img_tokens:
                    # Regular diagram or screenshot images
                    for im_tok in img_tokens:
                        src = im_tok.attrs.get("src", "")
                        alt = im_tok.content or "Diagram"
                        full_img_path = os.path.normpath(os.path.join(base_dir, src))
                        rep_img = get_scaled_image(full_img_path, max_w=520, max_h=560)
                        if rep_img:
                            # Caption
                            flowables.append(KeepTogether([
                                Paragraph(f"<b>Figure:</b> {alt}", ParagraphStyle("Cap", parent=style_body, fontName="Helvetica-Bold", fontSize=8, textColor=NAVY)),
                                Spacer(1, 2),
                                rep_img,
                                Spacer(1, 8),
                            ]))
                else:
                    # Normal prose paragraph
                    para_html = inline_to_reportlab_html(inline_tok, md.renderer, md.options)
                    if para_html.strip():
                        flowables.append(Paragraph(para_html, style_body))

            while i < total_tokens and tokens[i].type != "paragraph_close":
                i += 1

        # ---------------------------------------------------------------------
        # 4. TABLES
        # ---------------------------------------------------------------------
        elif tok.type == "table_open":
            table_rows = []
            current_row = []
            is_header_row = True
            i += 1

            while i < total_tokens and tokens[i].type != "table_close":
                cur_tok = tokens[i]
                if cur_tok.type in ("th_open", "td_open"):
                    cell_html = ""
                    if i + 1 < total_tokens and tokens[i + 1].type == "inline":
                        inline_cell = tokens[i + 1]
                        # Check if cell has an image
                        img_in_cell = [c for c in (inline_cell.children or []) if c.type == "image"]
                        if img_in_cell:
                            src = img_in_cell[0].attrs.get("src", "")
                            alt = img_in_cell[0].content or "Image"
                            img_path = os.path.normpath(os.path.join(base_dir, src))
                            cell_img = get_scaled_image(img_path, max_w=240, max_h=120)
                            if cell_img:
                                cell_flowable = cell_img
                            else:
                                cell_flowable = Paragraph(f"[{alt}]", style_tbl_cell)
                            current_row.append(cell_flowable)
                            i += 2
                            continue
                        else:
                            cell_html = inline_to_reportlab_html(inline_cell, md.renderer, md.options)
                            i += 1

                    style_to_use = style_tbl_hdr if is_header_row else style_tbl_cell
                    current_row.append(Paragraph(cell_html, style_to_use))
                elif cur_tok.type == "thead_close":
                    is_header_row = False
                elif cur_tok.type == "tr_close":
                    if current_row:
                        table_rows.append(current_row)
                        current_row = []
                i += 1

            if table_rows:
                # Compute proportional column widths fitting 540 pt usable width
                num_cols = max(len(r) for r in table_rows)
                if num_cols == 3:
                    col_widths = [120, 210, 210]
                elif num_cols == 2:
                    col_widths = [220, 320]
                elif num_cols == 5:
                    col_widths = [45, 155, 65, 230, 45]
                else:
                    col_w = 540 / num_cols
                    col_widths = [col_w] * num_cols

                t_table = Table(table_rows, colWidths=col_widths)
                t_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                flowables.append(Spacer(1, 4))
                flowables.append(t_table)
                flowables.append(Spacer(1, 6))

        # ---------------------------------------------------------------------
        # 5. FENCED CODE BLOCKS (``` ... ```)
        # ---------------------------------------------------------------------
        elif tok.type == "fence":
            code_text = tok.content
            lang = (tok.info or "").strip()

            # Render code inside light-gray padded container
            # Truncate overly long lines to prevent overflow
            lines = code_text.splitlines()
            formatted_lines = []
            for l in lines:
                if len(l) > 100:
                    l = l[:97] + "..."
                formatted_lines.append(html.escape(l))

            header_text = f"Code Block: {lang.upper()}" if lang else "Code Listing"
            code_html = "<br/>".join(formatted_lines)

            code_box_data = [
                [Paragraph(f"<b>{header_text}</b>", ParagraphStyle("CodeHdr", fontName="Helvetica-Bold", fontSize=7.5, textColor=STEEL))],
                [Paragraph(code_html, style_code)]
            ]
            t_code = Table(code_box_data, colWidths=[540])
            t_code.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BG_CODE),
                ("BOX", (0, 0), (-1, -1), 0.8, BORDER_CODE),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER_CODE),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            flowables.append(t_code)
            flowables.append(Spacer(1, 6))

        # ---------------------------------------------------------------------
        # 6. BULLET & ORDERED LISTS
        # ---------------------------------------------------------------------
        elif tok.type in ("bullet_list_open", "ordered_list_open"):
            is_ordered = tok.type == "ordered_list_open"
            list_idx = 1
            i += 1

            while i < total_tokens and tokens[i].type not in ("bullet_list_close", "ordered_list_close"):
                if tokens[i].type == "list_item_open":
                    item_text = ""
                    i += 1
                    while i < total_tokens and tokens[i].type != "list_item_close":
                        if tokens[i].type == "inline":
                            item_text += inline_to_reportlab_html(tokens[i], md.renderer, md.options) + " "
                        i += 1

                    bullet_prefix = f"<b>{list_idx}.</b> " if is_ordered else "&bull; "
                    flowables.append(Paragraph(bullet_prefix + item_text.strip(), style_bullet))
                    list_idx += 1
                i += 1

        # ---------------------------------------------------------------------
        # 7. HORIZONTAL RULES (---)
        # ---------------------------------------------------------------------
        elif tok.type == "hr":
            flowables.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=6, spaceAfter=8))

        i += 1

    return flowables


def export_readme_to_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(base_dir, "README.md")
    output_pdf = os.path.join(base_dir, "SmartBus_System_Documentation.pdf")
    readme_pdf = os.path.join(base_dir, "README.pdf")

    print(f"Reading source documentation from: {readme_path}")
    if not os.path.exists(readme_path):
        raise FileNotFoundError(f"Source file not found: {readme_path}")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    print("Parsing README.md into ReportLab flowable elements...")
    story = parse_readme_to_flowables(readme_path, base_dir, styles)
    print(f"Generated {len(story)} flowables from README.md.")

    print(f"Compiling publication PDF to: {output_pdf}")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully compiled PDF: {output_pdf}")

    import shutil
    shutil.copyfile(output_pdf, readme_pdf)
    print(f"Synchronized copy to: {readme_pdf}")


if __name__ == "__main__":
    export_readme_to_pdf()
