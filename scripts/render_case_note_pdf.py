from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "aws-support-case-note-aoss-403.md"
DST = ROOT / "docs" / "aws-support-case-note-aoss-403.pdf"

text = SRC.read_text(encoding="utf-8")

styles = getSampleStyleSheet()
normal = ParagraphStyle(
    "CaseNormal",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    spaceAfter=4,
)
heading = ParagraphStyle(
    "CaseHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=14,
    spaceBefore=8,
    spaceAfter=6,
)
mono = ParagraphStyle(
    "CaseMono",
    parent=styles["Code"],
    fontName="Courier",
    fontSize=8,
    leading=10,
)

story = []
in_code = False
code_lines = []

for line in text.splitlines():
    if line.strip().startswith("```"):
        if in_code:
            story.append(Preformatted("\n".join(code_lines), mono))
            story.append(Spacer(1, 6))
            code_lines = []
            in_code = False
        else:
            in_code = True
        continue

    if in_code:
        code_lines.append(line)
        continue

    if not line.strip():
        story.append(Spacer(1, 4))
        continue

    if line.startswith("# "):
        story.append(Paragraph(line[2:].strip(), ParagraphStyle("H1", parent=heading, fontSize=14, leading=16)))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:].strip(), heading))
    else:
        safe = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        story.append(Paragraph(safe, normal))

if code_lines:
    story.append(Preformatted("\n".join(code_lines), mono))

pdf = SimpleDocTemplate(str(DST), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
pdf.build(story)
print(str(DST))
