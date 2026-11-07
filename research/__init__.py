"""
🔬 RESEARCH - Copiloto financiero e informes automáticos (Sindicato V8)

Módulos ligeros (sin Streamlit ni OpenBB):
- data_hub   → datos de mercado y SEC
- valuation  → DCF, DCF inverso, Piotroski, Altman
- tools      → herramientas para el agente (function calling)
- copilot    → chat con herramientas
- report     → informe de análisis automático
"""

from .data_hub import DataHub, CompanySnapshot
from .tools import ToolRegistry
from .copilot import FinancialCopilot, CopilotReply
from .report import EquityReportGenerator, EquityReport

__all__ = ["DataHub", "CompanySnapshot", "ToolRegistry", "FinancialCopilot", "CopilotReply",
           "EquityReportGenerator", "EquityReport"]
