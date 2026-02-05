"""
👨🏫 MENTOR AGENT V8
Agente de educación financiera
"""

import logging

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from config import MODELS
from prompts import AGENT_PROMPTS

logger = logging.getLogger(__name__)


class MentorAgent:
    """Agente profesor para educación financiera."""
    
    def __init__(self):
        self._llm = ChatOpenAI(
            model=MODELS.fast_model,
            temperature=0.3
        )
    
    def explain(self, question: str, context: str = "") -> str:
        """
        Explica un concepto financiero.
        
        Args:
            question: Pregunta del usuario
            context: Contexto del RAG (opcional)
            
        Returns:
            Explicación didáctica
        """
        mentor = Agent(
            role='Profesor de Finanzas',
            goal='Enseñar conceptos financieros de forma clara',
            backstory=AGENT_PROMPTS['mentor'],
            llm=self._llm,
            verbose=False
        )
        
        task_desc = f"""
        PREGUNTA DEL ESTUDIANTE:
        {question}
        """
        
        if context:
            task_desc += f"""
            
            CONTEXTO DE LA BIBLIOTECA:
            {context[:2000]}
            """
        
        task_desc += """
        
        TU RESPUESTA DEBE:
        1. Explicar el concepto de forma simple
        2. Usar analogías del mundo real si ayuda
        3. Dar un ejemplo con números
        4. Conectar con la práctica de inversión
        5. Responder SIEMPRE en ESPAÑOL
        """
        
        task = Task(
            description=task_desc,
            agent=mentor,
            expected_output="Explicación didáctica en español"
        )
        
        result = Crew(agents=[mentor], tasks=[task]).kickoff()
        
        return result.raw if result else "Error generando respuesta"
