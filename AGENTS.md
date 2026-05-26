# MCP-Server-Tools

Single-file Python MCP server (`advanced_debate_server.py`, ~333 Zeilen, 2 Tools). Server-Name: `Dynamische-KI-Expertengruppe`. Alle Strings/Kommentare auf Deutsch.

## Setup

```posh
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python advanced_debate_server.py                # stdio
fastmcp dev advanced_debate_server.py           # hot reload
```

Keine `.env` für Produktion. API-Keys liegen auf dem Proxy-Host.

**`session-stand.md`** im Projekt-Root — Auto-Session-Speicherung.

**Wichtig**: `botocore` muss in der venv installiert sein, sonst erscheinen `EventStream`-Warnungen von litellm bei Bedrock/SageMaker.

## Environment

| Variable | Effekt | Default |
|---|---|---|
| `LITELLM_API_BASE` | **gesetzt** → Proxy-Modus (kein Rate-Limiting, OpenAI-Client); **nicht gesetzt** → Direkt-Modus (Rate-Limiting aktiv, litellm.completion) | `http://localhost:4000` |
| `LITELLM_API_KEY` | API-Key für den Proxy | `""` |
| `NVIDIA_RPM` | Requests/minute im Direkt-Modus | `10` |
| `MCP_TRANSPORT` | `stdio` oder `sse` | `stdio` |
| `PORT` / `HOST` | SSE-Port/Host | `8000` / `0.0.0.0` |

`LITELLM_API_BASE` steuert auch den RateLimiter: gesetzt = deaktiviert (Proxy-Modus), nicht gesetzt = aktiv (Direkt-Modus). **Env-Vars müssen vor dem Import/Subprozess gesetzt sein** (`advanced_debate_server.py:37-44`).

Proxy-Modus: OpenAI-Client (`openai.OpenAI`, `max_retries=0`) wird **einmalig** auf Modulebene erstellt, nicht pro Aufruf. `base_url` **ohne** `/v1`-Suffix (SDK hängt automatisch an). Direkt-Modus: `litellm.completion` + `RateLimiter` (Token-Bucket), alle `acquire()`-Aufrufe mit `if rate_limiter:` guard.

## Architektur

Drei-Phasen-Loop in `konsultiere_expertengruppe`:
1. **Completeness-Check** — Chef-Modell via `response_format={"type": "json_object"}`. `NEED_INFO` = früher Return. Exceptions → silent pass.
2. **Chef-moderierte Debatte** — JSON-Kommandos: `runde` (parallel via `asyncio.gather`), `synthese` (fertig), `beenden` (abbruch). Chef weist Rollen zu (Architekt, Code-Analyst usw.). Bei JSON-Parse-Fehler automatisch `runde` mit allen Modellen. `max_tokens=512` für Chef, `max_tokens=1024` für Modelle. Hard-Stop bei `maximale_sekunden` (Default 120s). Max 5 Modelle.
3. **Synthese** — Chef-Modell klassifiziert: `ERFOLG` / `TEILERGEBNIS` / `RATLOSIGKEIT`. `max_tokens=2048`.

Debatte-Logs: `logs/debates/debate_{timestamp}.md` (relativ zu CWD).

## Tools

- `liste_verfuegbare_modelle() -> str` — `litellm.utils.get_valid_models()`
- `konsultiere_expertengruppe(problemstellung, experten_modelle=None, maximale_sekunden=120) -> str`

Default-Modelle: `claude-3-5-sonnet`, `gpt-4o`, `gemini/gemini-2.5-flash`.

## Tests

**Custom-Test-Runner** (kein pytest):
```posh
python tests/test_debate_server.py              # alle
python tests/test_debate_server.py -k grund     # nur Kategorie A
python tests/test_debate_server.py -v           # verbose
```

6 Kategorien (A–F): Grundlagen, MCP-Transport, Debatten-Logik, SSE, Protokoll, Edge Cases.

Test-Prerequisites:
- `test/.env` mit `NVIDIA_API_KEY` muss existieren
- Test setzt `LITELLM_API_BASE` auf NVIDIA NIM-URL → RateLimiter deaktiviert
- Test setzt `LITELLM_LOG=WARNING` + `LITELLM_SUPPRESS_INFO=true` (Provider-List-Spam unterdrücken)
- Test-Modell: `deepseek-ai/deepseek-v4-flash` (über NVIDIA NIM, mit `openai/` Prefix für direkte litellm-Aufrufe)
- SSE-Test startet echten Server auf Port 9000
- Einige Edge-Case-Tests akzeptieren Timeout als gültiges Verhalten

## Deployment

```bash
docker build -t ghcr.io/peter-eske/mcp-debate-server:latest .
docker push ghcr.io/peter-eske/mcp-debate-server:latest
```

`Dockerfile` (python:3.12-slim) startet in SSE-Mode. NGINX benötigt `proxy_buffering off` für SSE.

`docker-compose.yml` bindet an `host.docker.internal:4000` (LiteLLM-Proxy). `docker-compose.test.yml` enthält vollständigen Stack mit PostgreSQL + LiteLLM-Proxy + Debate-Server.

## Conventions

- `EXPERTS_SYSTEM.md` ist der System-Prompt für den **aufrufenden Agent**, nicht für den Server.
- Keine Linting-, CI- oder Build-Skripte.
- `beispiel-config.yaml` = VPS-Proxy-Konfiguration (lokal irrelevant).
