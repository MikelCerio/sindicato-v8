"""
🤖 COPILOTO FINANCIERO - Chat con herramientas
==============================================

Bucle de agente "razona → llama herramienta → lee resultado → responde":

    usuario ─▶ LLM ──(tool_call)──▶ ToolRegistry ──▶ datos reales
                 ▲                                       │
                 └───────────── resultado JSON ◀─────────┘

El LLM nunca inventa cifras: si necesita un dato, llama a una herramienta.
Cada respuesta incluye la traza de herramientas usadas (transparencia / fuentes).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Dict, List, Optional

from .tools import ToolRegistry, serialize

DEFAULT_MODEL = os.getenv("COPILOT_MODEL", "gpt-4o")

SYSTEM_PROMPT = """Eres el Copiloto de Análisis del Sindicato V8: un analista de renta variable \
riguroso que trabaja para un inversor particular. Hoy es {today}.

REGLAS
1. Cifras SOLO desde herramientas. Si necesitas un dato, llama a la herramienta adecuada; \
nunca uses números de memoria. Si una herramienta falla o no hay datos, dilo.
2. Cita la fuente y la fecha/periodo de cada cifra relevante (p.ej. "Yahoo Finance, ejercicio 2025").
3. Los ratios vienen en tanto por uno: 0.25 = 25 %. Muéstralos en porcentaje.
4. Separa HECHOS (datos) de INTERPRETACIÓN (tu opinión razonada). Señala riesgos y lo que \
podría invalidar la tesis.
5. Un DCF es tan bueno como sus supuestos: muéstralos y comenta la sensibilidad.
6. No das asesoramiento financiero personalizado ni órdenes de compra/venta; ofreces análisis \
para que el usuario decida.
7. Responde en español, claro y estructurado (títulos cortos, viñetas, tablas markdown si ayudan). \
Sé conciso: prioriza lo que cambia la decisión.
{context}"""


@dataclass
class ToolTrace:
    name: str
    arguments: Dict[str, Any]
    result_preview: str


@dataclass
class CopilotReply:
    content: str
    tool_calls: List[ToolTrace] = field(default_factory=list)
    model: str = DEFAULT_MODEL


class FinancialCopilot:
    """
    Uso:
        copilot = FinancialCopilot()
        reply = copilot.ask("¿Está cara Microsoft frente a Alphabet?")
        print(reply.content)
    """

    def __init__(self, registry: Optional[ToolRegistry] = None, client: Any = None,
                 model: str = DEFAULT_MODEL, max_tool_rounds: int = 6, temperature: float = 0.2):
        self.registry = registry or ToolRegistry()
        self._client = client
        self.model = model
        self.max_tool_rounds = max_tool_rounds
        self.temperature = temperature
        self.history: List[Dict[str, Any]] = []

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def reset(self) -> None:
        self.history = []

    def _system(self, focus_ticker: Optional[str]) -> Dict[str, str]:
        ctx = f"\nCONTEXTO: el usuario está mirando la empresa {focus_ticker} en la app; " \
              f"si pregunta sin nombrar empresa, se refiere a ella." if focus_ticker else ""
        return {"role": "system", "content": SYSTEM_PROMPT.format(today=date.today().isoformat(), context=ctx)}

    def ask(self, question: str, focus_ticker: Optional[str] = None,
            on_tool_call: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> CopilotReply:
        """Hace una pregunta manteniendo el historial de la conversación."""
        self.history.append({"role": "user", "content": question})
        messages = [self._system(focus_ticker)] + self.history
        traces: List[ToolTrace] = []

        for _ in range(self.max_tool_rounds):
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=self.registry.schemas(),
                tool_choice="auto", temperature=self.temperature,
            )
            msg = response.choices[0].message
            calls = getattr(msg, "tool_calls", None) or []
            if not calls:
                content = msg.content or ""
                self.history.append({"role": "assistant", "content": content})
                return CopilotReply(content=content, tool_calls=traces, model=self.model)

            # El modelo pide datos: ejecutamos cada herramienta y le devolvemos el resultado
            assistant_msg = {"role": "assistant", "content": msg.content or "", "tool_calls": [
                {"id": c.id, "type": "function",
                 "function": {"name": c.function.name, "arguments": c.function.arguments}} for c in calls]}
            messages.append(assistant_msg)
            for c in calls:
                try:
                    args = json.loads(c.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                if on_tool_call:
                    on_tool_call(c.function.name, args)
                result_text = serialize(self.registry.call(c.function.name, args))
                traces.append(ToolTrace(c.function.name, args, result_text[:400]))
                messages.append({"role": "tool", "tool_call_id": c.id, "content": result_text})

        # Demasiadas rondas: pedimos una respuesta final sin herramientas
        messages.append({"role": "user", "content": "Responde ya con los datos obtenidos, sin más herramientas."})
        response = self.client.chat.completions.create(model=self.model, messages=messages,
                                                       temperature=self.temperature)
        content = response.choices[0].message.content or ""
        self.history.append({"role": "assistant", "content": content})
        return CopilotReply(content=content, tool_calls=traces, model=self.model)
