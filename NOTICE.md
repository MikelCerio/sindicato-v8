# Avisos y atribuciones

## Inspiración
El copiloto con herramientas (`research/copilot.py`) y el generador de informes
(`research/report.py`) están **inspirados conceptualmente** en proyectos open source de
análisis financiero con IA, en particular:

- **FinRobot** (AI4Finance Foundation) — Apache-2.0 — https://github.com/AI4Finance-Foundation/FinRobot
- **OpenBB** (OpenBB Inc.) — AGPL-3.0 — https://github.com/OpenBB-finance/OpenBB

**No se ha copiado código** de ninguno de los dos. Todo el paquete `research/` está escrito
desde cero y se apoya solo en fórmulas financieras estándar (DCF, CAPM, Piotroski, Altman)
y en las APIs de yfinance, SEC EDGAR y OpenAI.

`OpenBB` sigue siendo una dependencia **opcional** (comentada en `requirements.txt`) usada vía
su API pública en `services/openbb_service.py`, sin modificar su código. Si la instalas y
despliegas la app como servicio web, revisa sus condiciones AGPL-3.0:
https://docs.openbb.co/platform/licensing

FinRobot y OpenBB son marcas de sus respectivos titulares; este proyecto no está afiliado a ellos.

## Datos
- Yahoo Finance vía `yfinance` (uso personal/educativo; revisa sus condiciones).
- SEC EDGAR: datos públicos del Gobierno de EE.UU.

## Aviso
Herramienta educativa de análisis. No constituye asesoramiento financiero.
