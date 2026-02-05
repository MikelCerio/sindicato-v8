"""
📄 PDF GENERATOR SERVICE V8
"""

import io
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib import colors


class PDFGenerator:
    """Genera Investment Memos profesionales en PDF."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='Subtitle', parent=self.styles['Heading2'],
            textColor=HexColor('#00ff88'), spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='BodyCompact', parent=self.styles['Normal'],
            fontSize=9, leading=11, spaceAfter=6
        ))
    
    def create_investment_memo(
        self,
        ticker: str,
        veredicto: str,
        asignacion: str,
        macro_context: str,
        value_audit: Optional[str] = None,
        growth_audit: Optional[str] = None,
        risk_audit: Optional[str] = None
    ) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=40, bottomMargin=40)
        story = []
        
        # Header
        story.append(Paragraph(f"<b>SINDICATO CAPITAL - INVESTMENT MEMO</b>", self.styles['Title']))
        story.append(Paragraph(f"<b>TICKER: {ticker}</b>", self.styles['Subtitle']))
        story.append(Spacer(1, 8))
        
        # Metadata
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles['Normal']))
        story.append(Paragraph(f"Contexto Macro: {macro_context}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Veredicto
        story.append(Paragraph("<b>VEREDICTO DEL CIO</b>", self.styles['Heading2']))
        story.append(Spacer(1, 6))
        veredicto_clean = veredicto[:2000].replace('\n', '<br/>')
        story.append(Paragraph(veredicto_clean, self.styles['BodyCompact']))
        story.append(Spacer(1, 15))
        
        # Allocation
        story.append(Paragraph("<b>ASIGNACIÓN DE CAPITAL (10.000 EUR)</b>", self.styles['Heading2']))
        story.append(Spacer(1, 6))
        asig_clean = asignacion[:1500].replace('\n', '<br/>')
        story.append(Paragraph(asig_clean, self.styles['BodyCompact']))
        story.append(Spacer(1, 20))
        
        # Audits
        if value_audit:
            story.append(Paragraph("<b>VALUE AUDIT</b>", self.styles['Heading3']))
            story.append(Paragraph(value_audit[:800].replace('\n', '<br/>'), self.styles['BodyCompact']))
            story.append(Spacer(1, 10))
        
        if growth_audit:
            story.append(Paragraph("<b>GROWTH AUDIT</b>", self.styles['Heading3']))
            story.append(Paragraph(growth_audit[:800].replace('\n', '<br/>'), self.styles['BodyCompact']))
            story.append(Spacer(1, 10))
        
        if risk_audit:
            story.append(Paragraph("<b>RISK AUDIT</b>", self.styles['Heading3']))
            story.append(Paragraph(risk_audit[:800].replace('\n', '<br/>'), self.styles['BodyCompact']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("---", self.styles['Normal']))
        story.append(Paragraph("Este documento es para uso interno. No constituye asesoramiento financiero.", self.styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
