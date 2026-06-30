#!/usr/bin/env python3
"""Create a simple 1-page sample PDF for testing"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Create PDF
pdf_file = "sample1page.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter)
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor='#000000',
    spaceAfter=12,
    alignment=TA_CENTER
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=12,
    textColor='#000000',
    spaceAfter=6
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    spaceAfter=8,
    alignment=TA_LEFT
)

# Content
story = []

# Title
story.append(Paragraph("Machine Learning Fundamentals", title_style))
story.append(Spacer(1, 0.2*inch))

# Content sections
story.append(Paragraph("What is Machine Learning?", heading_style))
story.append(Paragraph(
    "Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("Key Concepts", heading_style))
story.append(Paragraph(
    "<b>Supervised Learning:</b> Models trained on labeled data to predict outcomes. Examples include classification and regression tasks used in email spam detection and house price prediction.",
    body_style
))
story.append(Paragraph(
    "<b>Unsupervised Learning:</b> Finding patterns in unlabeled data. Clustering and dimensionality reduction are common techniques used for customer segmentation and data exploration.",
    body_style
))
story.append(Paragraph(
    "<b>Reinforcement Learning:</b> Agents learn by interacting with their environment and receiving rewards. This approach powers game-playing AI and robotics applications.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("Applications", heading_style))
story.append(Paragraph(
    "Machine Learning is revolutionizing industries including healthcare (diagnostic imaging), finance (fraud detection), transportation (autonomous vehicles), and natural language processing (chatbots and translation). The ability to process large datasets and extract meaningful patterns has made ML an essential technology in modern data-driven organizations.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("Getting Started", heading_style))
story.append(Paragraph(
    "To begin learning Machine Learning, start with foundational mathematics (linear algebra, calculus, probability), then progress to popular frameworks like scikit-learn, TensorFlow, and PyTorch. Practice with real datasets from Kaggle and implement projects from concept to deployment.",
    body_style
))

# Build PDF
doc.build(story)
print(f"✅ Sample PDF created: {pdf_file}")
