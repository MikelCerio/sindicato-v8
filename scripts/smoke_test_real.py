"""
🔥 Prueba con datos REALES del copiloto e informes (research/)

Uso (desde la raíz del repo):
    python scripts/smoke_test_real.py            # MSFT por defecto
    python scripts/smoke_test_real.py AAPL ITX.MC

Comprueba cada pieza por separado y termina con un resumen OK/FALLO.
Sin OPENAI_API_KEY se salta las pruebas de IA (el resto funciona igual).
Genera <TICKER>_informe.html en la carpeta actual.
"""

import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from research import DataHub, ToolRegistry, FinancialCopilot, EquityReportGenerator  # noqa: E402
from research import valuation  # noqa: E402

results = []


def check(name, fn):
    t0 = time.time()
    try:
        out = fn()
        ok = out is not False
        results.append((name, ok, f"{time.time() - t0:.1f}s"))
        print(f"{'✅' if ok else '❌'} {name}: {str(out)[:300]}")
    except Exception as exc:
        results.append((name, False, str(exc)[:120]))
        print(f"❌ {name}: {exc}")
        traceback.print_exc(limit=2)


def main(tickers):
    hub = DataHub()
    t = tickers[0]

    check("Cotización", lambda: hub.quote(t)["price"] or False)
    check("Perfil", lambda: hub.profile(t)["sector"] or False)
    check("Cuenta de resultados", lambda: list(hub.financial_statement(t, "income").columns) or False)
    check("Ratios", lambda: (lambda r: r if r["operating_margin"] is not None else False)(hub.key_ratios(t)["profitability"]))
    check("Rentabilidad 1a", lambda: hub.price_performance(t).get("return_1y") if hub.price_performance(t).get("return_1y") is not None else False)
    check("Consenso", lambda: (lambda a: a if a.get("target_mean") else False)(hub.analyst_view(t)))
    check("Noticias", lambda: [n["title"] for n in hub.news(t, 3)] or False)
    check("SEC filings", lambda: (lambda f: False if f and "error" in f[0] else (f or "sin datos (normal si no es de EE.UU.)"))(hub.sec_filings(t, limit=3)))
    check("SEC XBRL", lambda: (lambda d: False if "no disponible" in str(d.get("error", "")) else d)(hub.sec_fundamentals(t)))
    check("DCF", lambda: (lambda v: {k: x for k, x in v.items() if k != "sensitivity"} if v.get("applicable") else False)(valuation.auto_valuation(hub, t)))
    check("Piotroski/Altman", lambda: (lambda q: q if q["piotroski"]["score"] is not None else False)(valuation.quality_scores(hub, t)))
    if len(tickers) > 1:
        check("Comparativa", lambda: hub.compare(tickers).to_string())

    has_ai = bool(os.getenv("OPENAI_API_KEY"))
    gen = EquityReportGenerator(hub, use_ai=has_ai)

    def report():
        rep = gen.generate(t, progress=lambda m, p: print(f"   … {m}"))
        path = f"{t.replace('.', '_')}_informe.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(rep.to_html())
        return f"{path} ({'IA' if rep.ai_generated else 'solo datos'})"

    check("Informe automático", report)

    if has_ai:
        def copilot():
            cp = FinancialCopilot(ToolRegistry(hub))
            r = cp.ask(f"Resume en 5 viñetas la situación financiera de {t} y si parece cara.",
                       on_tool_call=lambda n, a: print(f"   🔧 {n} {a}"))
            print("\n" + r.content + "\n")
            return f"{len(r.tool_calls)} herramientas usadas" if r.tool_calls else False
        check("Copiloto (chat)", copilot)
    else:
        print("⚠️  Sin OPENAI_API_KEY: se omite la prueba del copiloto.")

    print("\n===== RESUMEN =====")
    for name, ok, info in results:
        print(f"{'OK   ' if ok else 'FALLO'} {name:<22} {info}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main([a.upper() for a in sys.argv[1:]] or ["MSFT", "GOOGL"]))
