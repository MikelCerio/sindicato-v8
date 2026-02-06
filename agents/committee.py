"""
🦈 INVESTMENT COMMITTEE V8
Agentes del comité institucional con CrewAI
"""

import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from config import MODELS
from prompts import AGENT_PROMPTS, SYSTEM_PROMPT_BASE, SYSTEM_PROMPT_SMALL_CAP

logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    value_audit: str
    growth_audit: str
    risk_audit: str
    raw_debate: str


@dataclass
class VerdictResult:
    cio_verdict: str
    pm_allocation: str


class InvestmentCommittee:
    """Comité de Inversiones Institucional con agentes especializados."""
    
    def __init__(self):
        self._llm = None
    
    @property
    def llm(self) -> ChatOpenAI:
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=MODELS.standard_model,
                temperature=MODELS.temperature
            )
        return self._llm
    
    def run_audit(self, ticker: str, macro_brief: str, context: Dict[str, str], mode: str = "standard") -> AuditResult:
        """
        Ejecuta auditoría completa con los 3 analistas.
        
        Args:
            ticker: Símbolo de la acción
            macro_brief: Contexto macro actual
            context: Dict con claves 'value', 'growth', 'risk'
            mode: 'standard' (Large Caps) o 'small_cap' (Estilo Alpha)
        
        Returns:
            AuditResult con los 3 informes
        """
        logger.info(f"Iniciando auditoría de {ticker} en modo {mode}")
        
        # Seleccionar personalidad del agente según modo
        if mode == "small_cap":
            base_prompt = SYSTEM_PROMPT_SMALL_CAP
            role_prefix = "Alpha"
            focus_areas = {
                'value': 'SKIN IN THE GAME y Deuda',
                'growth': 'ROCE y Ventaja Competitiva',
                'risk': 'Concentración de Clientes y Deuda'
            }
        else:
            base_prompt = SYSTEM_PROMPT_BASE
            role_prefix = "Institucional"
            focus_areas = {
                'value': 'Balance y Deuda',
                'growth': 'I+D e Innovación',
                'risk': 'Riesgos Macro y Regulatorios'
            }
        
        # Crear agentes con personalidad adaptada
        value_agent = Agent(
            role=f'{role_prefix} Value Auditor',
            goal=f'Analizar {focus_areas["value"]}',
            backstory=AGENT_PROMPTS['forensic_auditor'] + "\n\n" + base_prompt,
            llm=self.llm,
            verbose=False
        )
        
        growth_agent = Agent(
            role=f'{role_prefix} Growth Analyst',
            goal=f'Evaluar {focus_areas["growth"]}',
            backstory=AGENT_PROMPTS['growth_analyst'] + "\n\n" + base_prompt,
            llm=self.llm,
            verbose=False
        )
        
        risk_agent = Agent(
            role=f'{role_prefix} Risk Hunter',
            goal=f'Identificar {focus_areas["risk"]}',
            backstory=AGENT_PROMPTS['risk_hunter'] + "\n\n" + base_prompt,
            llm=self.llm,
            verbose=False
        )
        
        # Crear tareas adaptadas al modo
        if mode == "small_cap":
            value_task = Task(
                description=f"""
                TICKER: {ticker}
                MACRO CONTEXT: {macro_brief}
                
                DATOS FINANCIEROS:
                {context.get('value', 'No disponible')}
                
                TU MISIÓN ALPHA:
                1. **SKIN IN THE GAME**: ¿Cuánto % de acciones tiene el CEO/Fundador?
                2. **INSIDER TRANSACTIONS**: ¿Están comprando o vendiendo?
                3. **DEUDA**: Deuda Neta / EBITDA (debe ser < 2x)
                4. **CAPITAL ALLOCATION**: ¿Buybacks o M&A? ¿Crearon valor?
                5. CONCLUSIÓN: ¿Los dueños están alineados con accionistas?
                """,
                agent=value_agent,
                expected_output="Informe Alpha con ownership y deuda"
            )
            
            growth_task = Task(
                description=f"""
                TICKER: {ticker}
                
                DATOS DEL NEGOCIO:
                {context.get('growth', 'No disponible')}
                
                TU MISIÓN ALPHA:
                1. **ROCE**: Return on Capital Employed (debe ser > 15%)
                2. **MOAT**: ¿Qué hace difícil copiar este negocio?
                3. **NICHO**: ¿Monopolio local? ¿Switching costs?
                4. **MÁRGENES**: Comparar con competidores
                5. CONCLUSIÓN: ¿Es un negocio de calidad o commodity?
                """,
                agent=growth_agent,
                expected_output="Análisis de ROCE y ventaja competitiva"
            )
            
            risk_task = Task(
                description=f"""
                TICKER: {ticker}
                
                DATOS DE RIESGOS:
                {context.get('risk', 'No disponible')}
                
                TU MISIÓN ALPHA:
                1. **CONCENTRACIÓN**: ¿Más del 20% revenue de 1 cliente?
                2. **DEUDA CORTO PLAZO**: ¿Riesgo de refinanciación?
                3. **CONTABILIDAD**: DSO creciente, inventario inflado
                4. **LITIGIOS**: Demandas pendientes
                5. DEAL-BREAKERS: ¿Hay algo que invalide la tesis?
                """,
                agent=risk_agent,
                expected_output="Red flags y deal-breakers"
            )
        else:
            # Modo Standard (original)
            value_task = Task(
                description=f"""
                TICKER: {ticker}
                MACRO CONTEXT: {macro_brief}
                
                DATOS DEL BALANCE Y DEUDA:
                {context.get('value', 'No disponible')}
                
                TU MISIÓN:
                1. Extrae Deuda Total y Cash/Equivalentes
                2. Calcula Deuda Neta = Deuda Total - Cash
                3. Evalúa Debt/Equity y cobertura de intereses
                4. ¿Hay goodwill inflado o intangibles dudosos?
                5. CONCLUSIÓN: ¿La empresa está sobreendeudada?
                """,
                agent=value_agent,
                expected_output="Informe de auditoría de valor con números concretos"
            )
            
            growth_task = Task(
                description=f"""
                TICKER: {ticker}
                
                DATOS DE I+D Y ESTRATEGIA:
                {context.get('growth', 'No disponible')}
                
                TU MISIÓN:
                1. Gasto en I+D en $ absolutos
                2. Ratio I+D / Revenue (debería estar entre 5-20%)
                3. ¿Hay productos concretos en pipeline?
                4. ¿Menciona patentes o IP específica?
                5. CONCLUSIÓN: ¿Innovación real o humo?
                """,
                agent=growth_agent,
                expected_output="Informe de innovación con métricas de I+D"
            )
            
            risk_task = Task(
                description=f"""
                TICKER: {ticker}
                MACRO CONTEXT: {macro_brief}
                
                DATOS DE RIESGOS:
                {context.get('risk', 'No disponible')}
                
                TU MISIÓN:
                1. Identifica TOP 3 riesgos severos
                2. Cuantifica litigios pendientes si los hay
                3. Evalúa dependencia de clientes/proveedores
                4. Riesgos regulatorios o geopolíticos
                5. DEAL-BREAKERS: ¿Hay algo que mate la tesis?
                """,
                agent=risk_agent,
                expected_output="Top 3 riesgos con cuantificación"
            )
        
        # Ejecutar crew
        crew = Crew(
            agents=[value_agent, growth_agent, risk_agent],
            tasks=[value_task, growth_task, risk_task],
            verbose=False
        )
        
        result = crew.kickoff()
        
        return AuditResult(
            value_audit=value_task.output.raw if value_task.output else "",
            growth_audit=growth_task.output.raw if growth_task.output else "",
            risk_audit=risk_task.output.raw if risk_task.output else "",
            raw_debate=str(result.raw) if result else ""
        )
    
    def run_verdict(self, ticker: str, debate_raw: str) -> VerdictResult:
        """
        Ejecuta decisión final con CIO y Portfolio Manager.
        
        Args:
            ticker: Símbolo
            debate_raw: Resultado del debate del comité
            
        Returns:
            VerdictResult con veredicto y allocation
        """
        logger.info(f"Emitiendo veredicto para {ticker}")
        
        cio = Agent(
            role='Chief Investment Officer',
            goal='Decisión final de inversión',
            backstory=AGENT_PROMPTS['cio'],
            llm=self.llm,
            verbose=False
        )
        
        pm = Agent(
            role='Portfolio Manager',
            goal='Sizing y asignación de capital',
            backstory=AGENT_PROMPTS['portfolio_manager'],
            llm=self.llm,
            verbose=False
        )
        
        cio_task = Task(
            description=f"""
            Tienes el debate completo del comité sobre {ticker}:
            
            {debate_raw[:3000]}
            
            EMITE TU VEREDICTO ESTRUCTURADO:
            1. TOP 3 ARGUMENTOS BULL
            2. TOP 3 ARGUMENTOS BEAR
            3. DEAL-BREAKERS IDENTIFICADOS
            4. DECISIÓN FINAL: COMPRAR / MANTENER / EVITAR
            5. NIVEL DE CONVICCIÓN: Alta / Media / Baja
            """,
            agent=cio,
            expected_output="Veredicto estructurado del CIO"
        )
        
        pm_task = Task(
            description=f"""
            El CIO ha emitido su veredicto. Tu trabajo es determinar el sizing.
            
            INSTRUCCIONES:
            - Tienes 10.000€ para asignar
            - Considera la convicción del CIO
            - Aplica las reglas: max 30% por posición
            
            RESPONDE CON:
            1. € a invertir en {ticker}
            2. € a mantener en caja
            3. Justificación del sizing
            4. Precio objetivo de entrada
            5. Stop-loss sugerido (%)
            """,
            agent=pm,
            expected_output="Allocation detallada con sizing"
        )
        
        crew = Crew(
            agents=[cio, pm],
            tasks=[cio_task, pm_task],
            verbose=False
        )
        
        crew.kickoff()
        
        return VerdictResult(
            cio_verdict=cio_task.output.raw if cio_task.output else "",
            pm_allocation=pm_task.output.raw if pm_task.output else ""
        )
