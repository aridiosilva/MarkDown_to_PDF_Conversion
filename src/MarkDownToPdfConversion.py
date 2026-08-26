import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
)
from reportlab.lib import colors

styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleX', parent=styles['Title'], fontSize=18, spaceAfter=4)
meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#444444'), spaceAfter=2)
h1_style = ParagraphStyle('H1X', parent=styles['Heading1'], fontSize=15, spaceBefore=18, spaceAfter=8, textColor=colors.HexColor('#1a1a2e'))
h2_style = ParagraphStyle('H2X', parent=styles['Heading2'], fontSize=12.5, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor('#22223b'))
body_style = ParagraphStyle('BodyX', parent=styles['Normal'], fontSize=10.2, leading=14, spaceAfter=4)
note_style = ParagraphStyle(
    'NoteX', parent=styles['Normal'], fontSize=9, leading=12.5,
    textColor=colors.HexColor('#6b6b6b'), leftIndent=10,
    borderColor=colors.HexColor('#cccccc'), borderWidth=0.5, borderPadding=6,
    spaceBefore=4, spaceAfter=8, backColor=colors.HexColor('#f5f5f7')
)
bullet_style = ParagraphStyle('BulletX', parent=styles['Normal'], fontSize=10.2, leading=14)

def inline(text):
    # negrito **texto**
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # itálico *texto*
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    # código inline `texto`
    text = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', text)
    return text

# Lê o markdown de origem
with open('spec_template.md', encoding='utf-8') as f:
    lines = f.read().split('\n')

story = []
i = 0
list_buffer = []
note_buffer = []

def flush_list():
    global list_buffer
    if list_buffer:
        items = [ListItem(Paragraph(inline(t), bullet_style), leftIndent=14) for t in list_buffer]
        story.append(ListFlowable(items, bulletType='bullet', start='•', leftIndent=10, spaceBefore=2, spaceAfter=8))
        list_buffer = []

def flush_note():
    global note_buffer
    if note_buffer:
        story.append(Paragraph(inline(' '.join(note_buffer)), note_style))
        note_buffer = []

while i < len(lines):
    line = lines[i].rstrip()

    # blockquotes (> ...) viram caixas de nota cinza
    if line.startswith('> '):
        flush_list()
        note_buffer.append(line[2:])
        i += 1
        continue
    else:
        flush_note()

    if not line.strip():
        flush_list()
        i += 1
        continue

    if line.startswith('# '):
        flush_list()
        story.append(Paragraph(inline(line[2:]), title_style))
    elif line.startswith('## '):
        flush_list()
        story.append(Paragraph(inline(line[3:]), h1_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#cccccc'), spaceAfter=4))
    elif line.startswith('### '):
        flush_list()
        story.append(Paragraph(inline(line[4:]), h2_style))
    elif line.strip() == '---':
        flush_list()
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd')))
        story.append(Spacer(1, 6))
    elif re.match(r'^\d+\.\s', line.strip()):
        # itens numerados (ex.: cenários Given/When/Then)
        list_buffer.append(re.sub(r'^\d+\.\s', '', line.strip()))
    elif line.strip().startswith('- '):
        list_buffer.append(line.strip()[2:])
    elif line.startswith('**') and line.rstrip().endswith('**') and line.count('**') == 2:
        flush_list()
        story.append(Paragraph(inline(line), meta_style))
    else:
        flush_list()
        story.append(Paragraph(inline(line), body_style))

    i += 1

flush_list()
flush_note()

doc = SimpleDocTemplate(
    'Feature_Specification_Template.pdf',
    pagesize=letter,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
    leftMargin=0.85*inch, rightMargin=0.85*inch,
    title="Feature Specification Template"
)
doc.build(story)
print("done")