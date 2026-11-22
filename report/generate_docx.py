"""
=============================================================================
ACADEMIC PROJECT REPORT BUILDER (MARKDOWN TO DOCX CONVERTER)
=============================================================================
Generates a polished, professional Word document (report.docx) matching
university thesis guidelines:
  - Font: Times New Roman
  - Body: 12 pt, 1.5 line spacing, 6 pt after paragraph
  - Headings: Styled H1 (18pt Bold), H2 (14pt Bold), H3 (12.5pt Bold)
  - Margins: 1 inch on all sides
  - Tables: Styled headers, borders, proper alignments
  - Images: Embedded high-resolution screenshots with centered figure captions
  - Clean page breaks before chapters
=============================================================================
"""

import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_footer_page_number(run):
    """Inserts a dynamic Word PAGE field for automatic page numbering."""
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    run._r.append(fldSimple)

def build_docx_report():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    md_path = os.path.join(base_dir, "report", "report.md")
    docx_path = os.path.join(base_dir, "report", "report.docx")
    screenshots_dir = os.path.join(base_dir, "screenshots")
    
    doc = Document()
    
    # Configure 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = False
        
        # Add Page Numbering in Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("Page ")
        f_run.font.name = "Times New Roman"
        f_run.font.size = Pt(9)
        f_run.font.color.rgb = RGBColor(120, 120, 120)
        add_footer_page_number(f_run)

    # Configure Default "Normal" Style
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(12)
    normal_font.color.rgb = RGBColor(30, 30, 30)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    lines = md_text.splitlines()
    i = 0
    in_code_block = False
    code_lines = []
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle Page Breaks
        if stripped in ["\\newpage", "---"]:
            # If line is markdown horizontal rule or newpage, add page break
            # Don't add if previous was already empty or page break
            doc.add_page_break()
            i += 1
            continue

        # Handle Code Blocks
        if stripped.startswith("```"):
            if in_code_block:
                # End of code block
                in_code_block = False
                code_text = "\n".join(code_lines)
                cp = doc.add_paragraph()
                cp.paragraph_format.left_indent = Inches(0.4)
                cp.paragraph_format.right_indent = Inches(0.4)
                cp.paragraph_format.space_before = Pt(4)
                cp.paragraph_format.space_after = Pt(8)
                cp.paragraph_format.line_spacing = 1.15
                c_run = cp.add_run(code_text)
                c_run.font.name = 'Consolas'
                c_run.font.size = Pt(9.5)
                c_run.font.color.rgb = RGBColor(40, 40, 40)
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle Markdown Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            
            # Parse table lines
            rows_data = []
            for t_line in table_lines:
                # Check if it's separator row like | :--- | :--- |
                inner = t_line.strip("|").strip()
                if set(inner).issubset({'-', ':', '|', ' '}):
                    continue
                cells = [c.strip() for c in t_line.split("|")[1:-1]]
                rows_data.append(cells)
                
            if rows_data:
                num_cols = max(len(r) for r in rows_data)
                tbl = doc.add_table(rows=len(rows_data), cols=num_cols)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                tbl.style = 'Table Grid'
                
                for r_idx, row in enumerate(rows_data):
                    is_header = (r_idx == 0)
                    for c_idx, cell_text in enumerate(row):
                        if c_idx < num_cols:
                            cell = tbl.cell(r_idx, c_idx)
                            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
                            
                            p = cell.paragraphs[0]
                            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            p.paragraph_format.line_spacing = 1.15
                            p.paragraph_format.space_after = Pt(2)
                            p.paragraph_format.space_before = Pt(2)
                            
                            run = p.add_run(cell_text)
                            run.font.name = 'Times New Roman'
                            if is_header:
                                run.font.bold = True
                                run.font.size = Pt(10)
                                run.font.color.rgb = RGBColor(255, 255, 255)
                                set_cell_background(cell, "1E3A8A")  # Deep Blue Header
                            else:
                                run.font.size = Pt(9.5)
                                if r_idx % 2 == 1:
                                    set_cell_background(cell, "F8FAFC")
                
                # Add spacing after table
                tp_space = doc.add_paragraph()
                tp_space.paragraph_format.space_after = Pt(6)
            continue

        # Handle Images: ![Alt Text](../screenshots/image.png)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            caption_text = img_match.group(1)
            raw_path = img_match.group(2)
            img_filename = os.path.basename(raw_path)
            full_img_path = os.path.join(screenshots_dir, img_filename)
            
            if os.path.exists(full_img_path):
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(10)
                p_img.paragraph_format.space_after = Pt(4)
                run_img = p_img.add_run()
                
                # Fit width nicely
                if "heatmap" in img_filename or "distributions" in img_filename or "model_comparison" in img_filename:
                    run_img.add_picture(full_img_path, width=Inches(6.0))
                else:
                    run_img.add_picture(full_img_path, width=Inches(4.5))
                    
                # Caption paragraph
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_after = Pt(12)
                cap_run = p_cap.add_run(f"Figure: {caption_text}")
                cap_run.font.name = 'Times New Roman'
                cap_run.font.size = Pt(10)
                cap_run.font.italic = True
                cap_run.font.color.rgb = RGBColor(80, 80, 80)
            else:
                p_ph = doc.add_paragraph()
                p_ph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r_ph = p_ph.add_run(f"[{caption_text} - Image Artifact: {img_filename}]")
                r_ph.font.italic = True
            i += 1
            continue

        # Handle Headings
        if stripped.startswith("# "):
            text = stripped[2:].strip()
            hp = doc.add_paragraph()
            hp.paragraph_format.space_before = Pt(16)
            hp.paragraph_format.space_after = Pt(8)
            hp.paragraph_format.keep_with_next = True
            hrun = hp.add_run(text)
            hrun.font.name = 'Times New Roman'
            hrun.font.size = Pt(17)
            hrun.font.bold = True
            hrun.font.color.rgb = RGBColor(16, 44, 87)
            i += 1
            continue
            
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            hp = doc.add_paragraph()
            hp.paragraph_format.space_before = Pt(12)
            hp.paragraph_format.space_after = Pt(6)
            hp.paragraph_format.keep_with_next = True
            hrun = hp.add_run(text)
            hrun.font.name = 'Times New Roman'
            hrun.font.size = Pt(13.5)
            hrun.font.bold = True
            hrun.font.color.rgb = RGBColor(30, 58, 138)
            i += 1
            continue

        if stripped.startswith("### "):
            text = stripped[4:].strip()
            hp = doc.add_paragraph()
            hp.paragraph_format.space_before = Pt(10)
            hp.paragraph_format.space_after = Pt(4)
            hp.paragraph_format.keep_with_next = True
            hrun = hp.add_run(text)
            hrun.font.name = 'Times New Roman'
            hrun.font.size = Pt(12)
            hrun.font.bold = True
            hrun.font.color.rgb = RGBColor(40, 40, 40)
            i += 1
            continue

        # Handle Bullet List Items
        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = stripped[2:].strip()
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.line_spacing = 1.35
            bp.paragraph_format.space_after = Pt(4)
            _add_formatted_text(bp, item_text)
            i += 1
            continue

        # Handle Numbered Lists
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            item_text = num_match.group(2)
            np_item = doc.add_paragraph(style='List Number')
            np_item.paragraph_format.line_spacing = 1.35
            np_item.paragraph_format.space_after = Pt(4)
            _add_formatted_text(np_item, item_text)
            i += 1
            continue

        # Handle Normal Paragraphs
        if stripped:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(6)
            _add_formatted_text(p, stripped)
            
        i += 1

    doc.save(docx_path)
    print(f"Project report successfully compiled to: {docx_path}")

def _add_formatted_text(paragraph, text):
    """Parses basic inline bold, italic, and code formatting."""
    # Pattern to match bold (**text**), italic (*text*), code (`text`), or plain
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.font.name = 'Times New Roman'
            run.bold = True
        elif token.startswith("*") and token.endswith("*"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = 'Times New Roman'
            run.italic = True
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(180, 40, 40)
        else:
            run = paragraph.add_run(token)
            run.font.name = 'Times New Roman'

if __name__ == "__main__":
    build_docx_report()
