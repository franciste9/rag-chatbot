#!/usr/bin/env python3
"""Create a 1-page NBA Finals 2026 summary PDF"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

# Create PDF
pdf_file = "nba_finals_2026.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor='#1f1f1f',
    spaceAfter=8,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=11,
    textColor='#000000',
    spaceAfter=6,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=9,
    spaceAfter=6,
    alignment=TA_LEFT
)

# Content
story = []

# Title
story.append(Paragraph("NBA FINALS 2026 CHAMPIONSHIP RECAP", title_style))
story.append(Spacer(1, 0.15*inch))

# Series Result
story.append(Paragraph("Championship Series Result", heading_style))
result_data = [
    ['Denver Nuggets', '4', 'wins'],
    ['Boston Celtics', '2', 'wins']
]
result_table = Table(result_data, colWidths=[2.5*inch, 0.8*inch, 1.5*inch])
result_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
story.append(result_table)
story.append(Spacer(1, 0.1*inch))

# Finals MVP
story.append(Paragraph("Finals MVP: Jamal Murray (Denver Nuggets)", heading_style))
story.append(Paragraph(
    "Murray averaged 28.3 points, 7.1 assists, and 1.8 steals per game throughout the series. His clutch performance in Game 6 clinching game included 32 points and 9 assists, securing the Nuggets' back-to-back championship.",
    body_style
))
story.append(Spacer(1, 0.08*inch))

# Series Summary
story.append(Paragraph("Series Summary", heading_style))
story.append(Paragraph(
    "<b>Game 1:</b> Denver 104, Boston 98 - Home court advantage sets the tone with strong defensive efforts. <b>Game 2:</b> Denver 112, Boston 107 - Extended Denver lead to 2-0 in Boston. <b>Game 3:</b> Boston 115, Denver 110 - Celtics avoid sweep with dominant third quarter. <b>Game 4:</b> Denver 118, Boston 113 - Murray's triple-double leads Nuggets to series clinch opportunity. <b>Game 5:</b> Boston 121, Denver 119 - OT thriller keeps Celtics alive. <b>Game 6:</b> Denver 128, Boston 121 - Championship sealed in Denver.",
    body_style
))
story.append(Spacer(1, 0.08*inch))

# Key Stats
story.append(Paragraph("Series Statistics", heading_style))
stats_data = [
    ['Metric', 'Denver', 'Boston'],
    ['Avg Points', '110.2', '106.8'],
    ['Field Goal %', '48.3%', '45.7%'],
    ['Three-Point %', '38.9%', '35.2%'],
    ['Rebounds/Game', '45.8', '43.2'],
    ['Assists/Game', '28.1', '26.4'],
]
stats_table = Table(stats_data, colWidths=[2.0*inch, 1.3*inch, 1.3*inch])
stats_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
story.append(stats_table)
story.append(Spacer(1, 0.08*inch))

# Highlights
story.append(Paragraph("Championship Highlights", heading_style))
story.append(Paragraph(
    "The Denver Nuggets successfully defended their championship title in 2026, winning their second consecutive NBA championship. Nikola Jokic's presence in the paint proved invaluable, combining with Murray's playmaking and improved perimeter defense. The Celtics mounted a competitive challenge but could not overcome Denver's depth and experience. This marks the Nuggets' dominant era in the Western Conference and solidifies their position among NBA dynasties.",
    body_style
))

# Build PDF
doc.build(story)
print(f"✅ NBA Finals 2026 PDF created: {pdf_file}")
print(f"   Location: /Users/francis.te/Github/rag-chatbot/{pdf_file}")
