import os
import asyncio
import time
import json
import yaml
import threading
from datetime import datetime
from mcp.server.fastmcp import FastMCP
import openai
import litellm

_litellm_base = os.environ.get("LITELLM_API_BASE")
if not _litellm_base:
    raise RuntimeError("LITELLM_API_BASE muss gesetzt sein (Proxy-Modus)")

api_key = os.environ.get("LITELLM_API_KEY", "")
_openai_client = openai.OpenAI(
    base_url=_litellm_base.rstrip("/"),
    api_key=api_key,
    max_retries=0,
)

def _call_model_sync(model, messages, **kwargs):
    return _openai_client.chat.completions.create(model=model, messages=messages, **kwargs)

MODEL_ROLES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_roles.yaml")

def _load_model_roles():
    try:
        with open(MODEL_ROLES_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    except Exception:
        return None

_model_roles_data = _load_model_roles()

DEFAULT_EXPERTS = ["claude-3-5-sonnet", "gpt-4o", "gemini/gemini-2.5-flash"]
if _model_roles_data and "default_experten" in _model_roles_data:
    DEFAULT_EXPERTS = _model_roles_data["default_experten"]

_ROLLEN_TEXT = (
    "Projektmanager, System-Architekt, Code-Analyst, Security-Experte, "
    "DB-Spezialist, DevOps, UI/UX-Designer, QA-Tester, Product-Owner, "
    "Performance-Optimierer, Dokumentations-Experte, Kritischer-Reviewer"
)

CHEF_MODERATOR_PROMPT = f"""Du bist der Diskussionsleiter einer KI-Expertendebatte.

Nach jeder Runde bekommst du den Stand und entscheidest den nächsten Schritt.

ANTWORTE NUR ALS JSON. Mögliche Aktionen:

1. NEUE RUNDE — Ein oder mehrere Modelle befragen:
   {{"aktion": "runde", "aufrufe": [{{"modell": "gpt-4o", "rolle": "Architekt", "fokus": "Entwirf die Systemarchitektur", "max_tokens": 512}}, ...], "begruendung": "Kurze Begründung", "max_sekunden": 90}}
   Für alle Modelle: {{"aktion": "runde", "aufrufe": "alle", "fokus": "Frage an alle", "max_sekunden": 60}}

2. SYNTHESE — Debatte abschließen:
   {{"aktion": "synthese", "begruendung": "Warum die Debatte abgeschlossen wird"}}

3. ABBRECHEN — Wenn kein Fortschritt:
   {{"aktion": "beenden", "grund": "Warum abgebrochen wird"}}

Verfügbare Rollen: {_ROLLEN_TEXT}.
Verwende für jedes Modell eine passende Rolle. Maximal 5 Modelle pro Aufruf.

Steuerungshinweise:
- max_tokens (optional): Sag dem Modell wie ausführlich es antworten soll. Default 1024.
- max_sekunden (optional): Setzt die verbleibende Zeit für die Debatte neu. Niedrig = schneller beenden."""

mcp = FastMCP("Dynamische-KI-Expertengruppe", host="0.0.0.0")

def save_debate_log(problem: str, protocol: str, final_result: str):
    log_dir = os.path.join(os.getcwd(), "logs", "debates")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debate_{timestamp}.md"
    filepath = os.path.join(log_dir, filename)

    md_content = f"""# KI-Debatten-Protokoll ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

## Ursprüngliche Problemstellung
{problem}

## Verlauf der Experten-Diskussion
{protocol}

## Finales Synthese-Ergebnis
{final_result}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    return filepath

@mcp.tool()
async def liste_verfuegbare_modelle() -> str:
    """Fragt den LiteLLM-Server ab und gibt eine Liste aller Modelle zurück."""
    try:
        models = litellm.utils.get_valid_models()
        if not models:
            return "Keine Modelle auf dem Server gefunden."
        return "Verfügbare KI-Modelle:\n" + "\n".join(f"- {m}" for m in models)
    except Exception as e:
        return f"Fehler beim Abrufen der Modellliste: {str(e)}"

@mcp.tool()
async def konsultiere_expertengruppe(
    problemstellung: str,
    experten_modelle: list[str] = None,
    maximale_sekunden: int = 120
) -> str:
    """Übergibt ein Problem an eine KI-Gruppe aus bis zu 5 Modellen."""
    start_time = time.time()
    warning_msg = ""
    if experten_modelle:
        if len(experten_modelle) > 5:
            experten_modelle = experten_modelle[:5]
            warning_msg = "Es wurden mehr als 5 Modelle angefordert. Die Liste wurde auf die ersten 5 Modelle gekürzt.\n\n"
        models_to_use = experten_modelle
    else:
        models_to_use = DEFAULT_EXPERTS

    protokoll = "=== DISKUSSIONSPROTOKOLL ===\n"
    protokoll += f"Beteiligte Modelle: {', '.join(models_to_use)}\n\n"
    chef_model = models_to_use[0]

    check_prompt = (
        f"Analysiere diese Problemstellung:\n{problemstellung}\n\n"
        "Fehlen kritische Informationen? Wenn JA, antworte AUSSCHLIESSLICH im JSON-Format: "
        '{"status": "NEED_INFO", "fragen": ["Frage 1", "Frage 2"]}. '
        'Wenn genug Infos da sind, antworte mit {"status": "READY"}.'
    )
    try:
        loop = asyncio.get_running_loop()
        check_res = await loop.run_in_executor(
            None, lambda: _call_model_sync(
                model=chef_model,
                messages=[{"role": "user", "content": check_prompt}],
                response_format={"type": "json_object"}
            )
        )
        check_json = json.loads(check_res.choices[0].message.content)
        if check_json.get("status") == "NEED_INFO":
            fragen_liste = "\n".join([f"- {f}" for f in check_json.get("fragen", [])])
            return f"DIE EXPERTENGRUPPE BENÖTIGT WEITERE INFORMATIONEN:\n{fragen_liste}"
    except Exception:
        pass

    loop = asyncio.get_running_loop()
    runde = 0
    zeitlimit_erreicht = False

    while True:
        elapsed = time.time() - start_time
        if elapsed >= maximale_sekunden:
            zeitlimit_erreicht = True
            protokoll += "\n--- ZEITLIMIT ERREICHT ---\n"
            break

        chef_context = (
            f"Problem: {problemstellung}\n\n"
            f"Bisheriger Stand (nach Runde {runde}):\n{protokoll}\n\n"
            "Was ist der nächste Schritt?"
        )
        chef_msg = [
            {"role": "system", "content": CHEF_MODERATOR_PROMPT},
            {"role": "user", "content": chef_context},
        ]

        try:
            chef_raw = await loop.run_in_executor(
                None, lambda: _call_model_sync(
                    model=chef_model, messages=chef_msg,
                    response_format={"type": "json_object"},
                    max_tokens=512
                )
            )
            cmd = json.loads(chef_raw.choices[0].message.content)
        except Exception:
            cmd = {"aktion": "runde", "aufrufe": "alle",
                   "fokus": "Setze die Diskussion zum Problem fort"}

        aktion = cmd.get("aktion", "runde")

        if aktion == "synthese":
            break

        if aktion == "beenden":
            zeitlimit_erreicht = True
            protokoll += f"\n--- DEBATTE ABGEBROCHEN: {cmd.get('grund', 'Keine Angabe')} ---\n"
            break

        if "max_sekunden" in cmd:
            neue_limit = min(int(cmd["max_sekunden"]), 600)
            if time.time() - start_time >= neue_limit:
                zeitlimit_erreicht = True
                protokoll += "\n--- VOM CHEF GESETZTES ZEITLIMIT ERREICHT ---\n"
                break
            maximale_sekunden = neue_limit

        if aktion == "runde":
            runde += 1
            aufrufe = cmd.get("aufrufe", "alle")
            if aufrufe == "alle":
                to_call = models_to_use[:5]
                rollen = [{"modell": m, "rolle": "Experte",
                           "fokus": cmd.get("fokus", "Bringe dich ein"),
                           "max_tokens": cmd.get("max_tokens", 1024)} for m in to_call]
            else:
                to_call = [a["modell"] for a in aufrufe[:5]]
                rollen = aufrufe[:5]

            rolle_map = {r["modell"]: (r.get("rolle", "Experte"), r.get("fokus", ""), r.get("max_tokens", 1024)) for r in rollen}
            prompts_tokens = []
            for m in to_call:
                rolle, fokus, tokens = rolle_map.get(m, ("Experte", "", 1024))
                prompts_tokens.append(
                    (m,
                     f"Du bist {rolle} in einer Expertendebatte.\n"
                     f"Problem: {problemstellung}\n"
                     f"Bisher diskutiert:\n{protokoll}\n"
                     f"Dein Fokus: {fokus}",
                     tokens)
                )

            tasks = [
                loop.run_in_executor(
                    None, lambda m=m, p=p, t=t: _call_model_sync(
                        model=m, messages=[{"role": "user", "content": p}],
                        max_tokens=t
                    )
                )
                for m, p, t in prompts_tokens
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for modell, result in zip(to_call, results):
                if isinstance(result, Exception):
                    protokoll += f"[{modell}]: Fehler ({str(result)})\n\n"
                else:
                    protokoll += f"[{modell}]: {result.choices[0].message.content}\n\n"

    synthese_prompt = (
        f"Hier ist das Protokoll der KI-Diskussion:\n{protokoll}\n\n"
        "Erstelle das finale Ergebnis. Klassifiziere es als ERFOLG, "
        f"TEILERGEBNIS (Zeitlimit hit: {zeitlimit_erreicht}) oder RATLOSIGKEIT."
    )

    try:
        _s = synthese_prompt
        final_res = await loop.run_in_executor(
            None, lambda s=_s: _call_model_sync(
                model=chef_model, messages=[{"role": "user", "content": s}],
                max_tokens=2048
            )
        )
        final_content = final_res.choices[0].message.content
        log_path = save_debate_log(problemstellung, protokoll, final_content)
        return f"{warning_msg}{final_content}\n\n*Ein detailliertes Protokoll dieser Debatte wurde unter {log_path} gespeichert.*"
    except Exception as e:
        return f"Fehler bei der finalen Auswertung: {str(e)}"


def _register_at_litellm():
    """Fallback: Versucht sich am LiteLLM-MCP-Server zu registrieren (Background-Thread)."""
    import urllib.request
    import json as j
    delay = 3
    max_delay = 30
    for attempt in range(20):
        try:
            payload = j.dumps({
                "server_name": "dynamische_ki_expertengruppe",
                "transport": "sse",
                "url": f"http://127.0.0.1:{os.environ.get('PORT', '8000')}/sse",
            }).encode()
            req = urllib.request.Request(
                f"{_litellm_base}/v1/mcp/server",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
            return
        except Exception:
            time.sleep(delay)
            delay = min(delay * 2, max_delay)


if __name__ == "__main__":
    thread = threading.Thread(target=_register_at_litellm, daemon=True)
    thread.start()
    transport = os.environ.get("MCP_TRANSPORT", "sse")
    if transport == "sse":
        mcp.settings.port = int(os.environ.get("PORT", "8000"))
        mcp.settings.host = os.environ.get("HOST", "0.0.0.0")
        mcp.run(transport="sse")
    else:
        mcp.run()
