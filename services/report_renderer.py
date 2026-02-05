"""
🖨️ HTML REPORT RENDERER - Equity Research Reports
Genera reportes HTML profesionales estilo FinRobot / Wall Street Research.
"""

import base64
from datetime import datetime
from typing import Dict, Optional, Any


class HTMLReportRenderer:
    """
    Genera reportes de investigación en HTML con estilo institucional.
    Inspirado en FinRobot y reportes de equity research de Wall Street.
    """
    
    def __init__(self):
        self.css = self._get_css()
    
    def _get_css(self) -> str:
        """CSS profesional estilo FinRobot."""
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            * { box-sizing: border-box; }
            
            body { 
                font-family: 'Inter', 'Helvetica Neue', sans-serif; 
                color: #1a1a2e; 
                line-height: 1.7; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 40px 20px;
                background: #fafafa;
            }
            
            .report-container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            }
            
            .header { 
                border-bottom: 3px solid #1a365d; 
                padding-bottom: 20px; 
                margin-bottom: 30px; 
                display: flex; 
                justify-content: space-between; 
                align-items: flex-start; 
            }
            
            .title { 
                font-size: 32px; 
                font-weight: 700; 
                color: #1a365d; 
                margin: 0 0 5px 0; 
            }
            
            .subtitle {
                color: #b8860b;
                font-weight: 600;
                font-size: 14px;
                letter-spacing: 1px;
            }
            
            .meta { 
                font-size: 12px; 
                color: #666; 
                text-align: right; 
                line-height: 1.8;
            }
            
            .recommendation-box { 
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border-left: 5px solid #1a365d; 
                padding: 25px 30px; 
                margin: 30px 0; 
                display: flex; 
                justify-content: space-around;
                border-radius: 0 8px 8px 0;
            }
            
            .metric { 
                text-align: center;
                padding: 0 15px;
            }
            
            .metric-val { 
                font-size: 26px; 
                font-weight: 700; 
                display: block; 
                margin-bottom: 5px;
            }
            
            .metric-label { 
                font-size: 11px; 
                text-transform: uppercase; 
                color: #64748b;
                letter-spacing: 0.5px;
                font-weight: 500;
            }
            
            .buy { color: #059669; }
            .sell { color: #dc2626; }
            .hold { color: #d97706; }
            .avoid { color: #7c3aed; }
            
            h2 { 
                color: #1a365d; 
                border-bottom: 2px solid #e2e8f0; 
                padding-bottom: 10px; 
                margin-top: 40px;
                font-size: 20px;
                font-weight: 600;
            }
            
            h2::before {
                margin-right: 10px;
            }
            
            .content {
                background: #f8fafc;
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                font-size: 14px;
            }
            
            .table-container { 
                overflow-x: auto; 
            }
            
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0; 
                font-size: 13px; 
            }
            
            th { 
                text-align: left; 
                padding: 12px; 
                background-color: #1a365d; 
                color: white;
                font-weight: 500;
            }
            
            td { 
                padding: 12px; 
                border-bottom: 1px solid #e2e8f0; 
            }
            
            tr:hover {
                background-color: #f8fafc;
            }
            
            .highlight-box {
                background: #fef3c7;
                border-left: 4px solid #d97706;
                padding: 15px 20px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }
            
            .risk-item {
                padding: 10px 15px;
                margin: 10px 0;
                background: #fee2e2;
                border-left: 4px solid #dc2626;
                border-radius: 0 6px 6px 0;
                font-size: 14px;
            }
            
            .bull-item {
                padding: 10px 15px;
                margin: 10px 0;
                background: #d1fae5;
                border-left: 4px solid #059669;
                border-radius: 0 6px 6px 0;
                font-size: 14px;
            }
            
            .disclaimer { 
                font-size: 10px; 
                color: #94a3b8; 
                margin-top: 50px; 
                border-top: 1px solid #e2e8f0; 
                padding-top: 20px;
                text-align: center;
            }
            
            .footer-logo {
                text-align: center;
                margin-top: 30px;
                font-size: 24px;
            }
            
            @media print {
                body { background: white; }
                .report-container { box-shadow: none; }
            }
        </style>
        """
    
    def render(
        self,
        ticker: str,
        price: float,
        veredicto: str,
        debate: str,
        fundamentals: Dict[str, Any],
        sentiment: str,
        value_audit: Optional[str] = None,
        growth_audit: Optional[str] = None,
        risk_audit: Optional[str] = None,
        macro_context: Optional[str] = None,
        allocation: Optional[str] = None
    ) -> str:
        """
        Genera el reporte HTML completo.
        
        Args:
            ticker: Símbolo de la acción
            price: Precio actual
            veredicto: Veredicto del CIO
            debate: Debate completo del comité
            fundamentals: Dict con datos fundamentales
            sentiment: Sentimiento del mercado
            value_audit: Auditoría de valor (opcional)
            growth_audit: Auditoría de crecimiento (opcional)
            risk_audit: Auditoría de riesgos (opcional)
            macro_context: Contexto macro (opcional)
            allocation: Allocation sugerida (opcional)
            
        Returns:
            HTML string completo
        """
        # Determinar color del veredicto
        color_class = "hold"
        veredicto_upper = veredicto.upper() if veredicto else ""
        if "COMPRA" in veredicto_upper or "BUY" in veredicto_upper:
            color_class = "buy"
        elif "VENTA" in veredicto_upper or "SELL" in veredicto_upper:
            color_class = "sell"
        elif "EVITA" in veredicto_upper or "AVOID" in veredicto_upper:
            color_class = "avoid"
        
        # Extraer veredicto corto para el box
        veredicto_corto = self._extract_short_verdict(veredicto)
        
        # Formatear fundamentales
        pe = fundamentals.get('pe_ratio', 0) or 0
        roe = fundamentals.get('roe', 0) or 0
        debt_equity = fundamentals.get('debt_to_equity', 0) or 0
        forward_pe = fundamentals.get('forward_pe', 0) or 0
        
        # Generar secciones opcionales
        value_section = self._format_audit_section("💰 Value Audit", value_audit, "content") if value_audit else ""
        growth_section = self._format_audit_section("🚀 Growth Audit", growth_audit, "content") if growth_audit else ""
        risk_section = self._format_risk_section(risk_audit) if risk_audit else self._default_risk_section()
        allocation_section = self._format_allocation_section(allocation) if allocation else ""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{ticker} - Equity Research Report | Sindicato V8</title>
            {self.css}
        </head>
        <body>
            <div class="report-container">
                <div class="header">
                    <div>
                        <h1 class="title">{ticker}</h1>
                        <div class="subtitle">EQUITY RESEARCH REPORT</div>
                        <div style="color: #64748b; font-size: 12px; margin-top: 5px;">SINDICATO V8 INSTITUTIONAL</div>
                    </div>
                    <div class="meta">
                        <strong>Fecha:</strong> {datetime.now().strftime('%d %b %Y')}<br>
                        <strong>Hora:</strong> {datetime.now().strftime('%H:%M')} CET<br>
                        <strong>Analista:</strong> AI Investment Committee<br>
                        {f'<strong>Macro:</strong> {macro_context[:50]}...<br>' if macro_context else ''}
                    </div>
                </div>

                <div class="recommendation-box">
                    <div class="metric">
                        <span class="metric-val {color_class}">{veredicto_corto}</span>
                        <span class="metric-label">Recomendación</span>
                    </div>
                    <div class="metric">
                        <span class="metric-val">${price:.2f}</span>
                        <span class="metric-label">Precio Actual</span>
                    </div>
                    <div class="metric">
                        <span class="metric-val">{pe:.1f}x</span>
                        <span class="metric-label">P/E Trailing</span>
                    </div>
                    <div class="metric">
                        <span class="metric-val">{forward_pe:.1f}x</span>
                        <span class="metric-label">P/E Forward</span>
                    </div>
                    <div class="metric">
                        <span class="metric-val">{sentiment}</span>
                        <span class="metric-label">Sentiment AI</span>
                    </div>
                </div>

                <h2>📊 Executive Summary</h2>
                <div class="content">
                    {self._format_text(veredicto)}
                </div>

                <h2>📈 Key Metrics</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                                <th>Assessment</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>P/E Ratio</strong></td>
                                <td>{pe:.1f}x</td>
                                <td>{self._assess_pe(pe)}</td>
                            </tr>
                            <tr>
                                <td><strong>Forward P/E</strong></td>
                                <td>{forward_pe:.1f}x</td>
                                <td>{self._assess_forward_pe(pe, forward_pe)}</td>
                            </tr>
                            <tr>
                                <td><strong>ROE</strong></td>
                                <td>{roe*100:.1f}%</td>
                                <td>{self._assess_roe(roe)}</td>
                            </tr>
                            <tr>
                                <td><strong>Debt/Equity</strong></td>
                                <td>{debt_equity:.1f}</td>
                                <td>{self._assess_debt(debt_equity)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                {value_section}
                {growth_section}
                
                <h2>⚠️ Risk Analysis</h2>
                {risk_section}

                {allocation_section}

                <h2>📝 Full Committee Debate</h2>
                <div class="content" style="max-height: 400px; overflow-y: auto;">
                    {self._format_text(debate)}
                </div>

                <div class="footer-logo">
                    🏛️
                </div>

                <div class="disclaimer">
                    <strong>DISCLAIMER:</strong> Este reporte ha sido generado por Inteligencia Artificial (Sindicato V8) 
                    con fines exclusivamente educativos e informativos. NO constituye asesoramiento financiero profesional, 
                    recomendación de inversión, ni oferta de compra o venta de valores. Los datos provienen de fuentes públicas 
                    (OpenBB, Yahoo Finance) y pueden tener retraso o inexactitudes. Consulte a un asesor financiero profesional 
                    antes de tomar decisiones de inversión. El usuario asume toda la responsabilidad por sus decisiones de inversión.
                    <br><br>
                    © {datetime.now().year} Sindicato V8 - Capital Preservation First
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _extract_short_verdict(self, veredicto: str) -> str:
        """Extrae un veredicto corto para el box."""
        if not veredicto:
            return "N/A"
        
        upper = veredicto.upper()
        if "COMPRAR" in upper or "COMPRA FUERTE" in upper:
            return "COMPRAR"
        elif "MANTENER" in upper or "HOLD" in upper:
            return "MANTENER"
        elif "EVITAR" in upper or "AVOID" in upper:
            return "EVITAR"
        elif "VENDER" in upper or "SELL" in upper:
            return "VENDER"
        else:
            # Intentar extraer las primeras palabras relevantes
            words = veredicto.split()[:2]
            return " ".join(words).upper()[:15]
    
    def _format_text(self, text: str) -> str:
        """Formatea texto para HTML."""
        if not text:
            return ""
        return text.replace('\n', '<br>').replace('  ', ' &nbsp;')
    
    def _format_audit_section(self, title: str, content: str, css_class: str) -> str:
        """Formatea una sección de auditoría."""
        if not content:
            return ""
        return f"""
        <h2>{title}</h2>
        <div class="{css_class}">
            {self._format_text(content)}
        </div>
        """
    
    def _format_risk_section(self, risk_audit: str) -> str:
        """Formatea la sección de riesgos."""
        if not risk_audit:
            return self._default_risk_section()
        
        # Intentar parsear bullet points
        lines = risk_audit.split('\n')
        risks_html = ""
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                clean_line = line.lstrip('-•* ').strip()
                if clean_line:
                    risks_html += f'<div class="risk-item">{clean_line}</div>'
        
        if not risks_html:
            risks_html = f'<div class="content">{self._format_text(risk_audit)}</div>'
        
        return risks_html
    
    def _default_risk_section(self) -> str:
        """Sección de riesgos por defecto."""
        return """
        <div class="risk-item">Verificar impacto de tasas de interés (10Y Treasury) en valoración y coste de deuda.</div>
        <div class="risk-item">Riesgos regulatorios y de compliance identificados en el 10-K.</div>
        <div class="risk-item">Presión competitiva potencial en márgenes operativos.</div>
        <div class="risk-item">Dependencia de factores macroeconómicos y ciclo económico.</div>
        """
    
    def _format_allocation_section(self, allocation: str) -> str:
        """Formatea la sección de allocation."""
        if not allocation:
            return ""
        return f"""
        <h2>💰 Capital Allocation</h2>
        <div class="highlight-box">
            {self._format_text(allocation)}
        </div>
        """
    
    def _assess_pe(self, pe: float) -> str:
        """Evalúa el P/E ratio."""
        if pe <= 0:
            return "⚠️ No disponible / Negativo"
        elif pe < 10:
            return "🟢 Muy barato"
        elif pe < 18:
            return "🟢 Atractivo"
        elif pe < 25:
            return "🟡 Fair value"
        elif pe < 35:
            return "🟠 Caro"
        else:
            return "🔴 Muy caro"
    
    def _assess_forward_pe(self, pe: float, forward_pe: float) -> str:
        """Evalúa la expansión/contracción de PE."""
        if forward_pe <= 0 or pe <= 0:
            return "⚠️ N/A"
        ratio = forward_pe / pe
        if ratio < 0.8:
            return "🟢 Fuerte crecimiento esperado"
        elif ratio < 0.95:
            return "🟢 Crecimiento esperado"
        elif ratio < 1.05:
            return "🟡 Estable"
        else:
            return "🔴 Contracción esperada"
    
    def _assess_roe(self, roe: float) -> str:
        """Evalúa el ROE."""
        if roe <= 0:
            return "🔴 Negativo"
        elif roe < 0.08:
            return "🟠 Bajo"
        elif roe < 0.15:
            return "🟡 Aceptable"
        elif roe < 0.25:
            return "🟢 Bueno"
        else:
            return "🟢 Excelente"
    
    def _assess_debt(self, debt_equity: float) -> str:
        """Evalúa el ratio de deuda."""
        if debt_equity < 0:
            return "⚠️ N/A"
        elif debt_equity < 0.3:
            return "🟢 Muy conservador"
        elif debt_equity < 0.8:
            return "🟢 Saludable"
        elif debt_equity < 1.5:
            return "🟡 Moderado"
        elif debt_equity < 2.5:
            return "🟠 Elevado"
        else:
            return "🔴 Alto riesgo"
    
    def get_download_link(self, html_content: str, filename: str) -> str:
        """
        Genera un link de descarga para el HTML.
        
        Args:
            html_content: Contenido HTML
            filename: Nombre del archivo (sin extensión)
            
        Returns:
            HTML string con el botón de descarga
        """
        b64 = base64.b64encode(html_content.encode()).decode()
        return f'''
        <a href="data:text/html;base64,{b64}" 
           download="{filename}.html" 
           style="
               display: inline-block;
               text-decoration: none; 
               background: linear-gradient(135deg, #1a365d 0%, #2d4a7c 100%); 
               color: white; 
               padding: 12px 24px; 
               border-radius: 8px; 
               font-weight: 600;
               font-size: 14px;
               transition: all 0.3s ease;
               box-shadow: 0 4px 15px rgba(26, 54, 93, 0.3);
           "
           onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(26, 54, 93, 0.4)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(26, 54, 93, 0.3)';"
        >
            📥 Descargar Research Report (HTML)
        </a>
        '''
    
    def get_pdf_download_link(self, html_content: str, filename: str) -> str:
        """
        Genera instrucciones para PDF.
        El usuario puede abrir el HTML y usar Ctrl+P para guardar como PDF.
        """
        return f'''
        <div style="
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 13px;
        ">
            💡 <strong>Tip:</strong> Abre el HTML descargado en tu navegador y usa 
            <code>Ctrl+P</code> (Windows) o <code>Cmd+P</code> (Mac) para guardarlo como PDF 
            con formato profesional.
        </div>
        '''
