# MCP-Server-Tools

Single-file Python MCP server (`advanced_debate_server.py`, ~300 Zeilen, 2 Tools). Server-Name: `Dynamische-KI-Expertengruppe`. Alle Strings/Kommentare auf Deutsch.

## Setup

```posh
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python advanced_debate_server.py                # SSE (default)
```

Keine `.env` für Produktion. API-Keys liegen auf dem Proxy-Host.

**`session-stand.md`** im Projekt-Root — Auto-Session-Speicherung (gitignored).

**`botocore`** muss in der venv installiert sein, sonst `EventStream`-Warnungen von litellm.

## Environment

| Variable | Effekt | Default |
|---|---|---|
| `LITELLM_API_BASE` | **Required** – URL zum LiteLLM-Proxy | – |
| `LITELLM_API_KEY` | API-Key für den Proxy (optional) | `""` |
| `PORT` / `HOST` | SSE-Port/Host | `8000` / `0.0.0.0` |
| `MCP_TRANSPORT` | Transport-Modus | `sse` |

Nur **Proxy-Modus** – `LITELLM_API_BASE` muss gesetzt sein.

OpenAI-Client (`openai.OpenAI`, `max_retries=0`) wird **einmalig** auf Modulebene erstellt, nicht pro Aufruf. `base_url` **ohne** `/v1`-Suffix (SDK hängt automatisch an).

## Architektur

Drei-Phasen-Loop in `konsultiere_expertengruppe`:
1. **Completeness-Check** — Chef-Modell via `response_format={"type": "json_object"}`. `NEED_INFO` = früher Return.
2. **Chef-moderierte Debatte** — JSON-Kommandos: `runde` (parallel via `asyncio.gather`), `synthese` (fertig), `beenden` (abbruch). Chef weist Rollen zu (12 Rollen aus `model_roles.yaml`). Bei JSON-Parse-Fehler automatisch `runde` mit allen Modellen. `max_tokens=512` für Chef, `max_tokens=1024` für Modelle. Hard-Stop bei `maximale_sekunden` (Default 120s). Max 5 Modelle.
3. **Synthese** — Chef-Modell klassifiziert: `ERFOLG` / `TEILERGEBNIS` / `RATLOSIGKEIT`. `max_tokens=2048`.

Debatte-Logs: `logs/debates/debate_{timestamp}.md` (relativ zu CWD).

**Modell-Rollen** aus `model_roles.yaml` (12 Rollen). Fallback auf Default-Liste bei Fehler. Default-Experten aus `model_roles.yaml` key `default_experten`.

**MCP-Registrierung**: `_register_at_litellm()` als Background-Thread beim Start (exponential backoff, max 20 Versuche). Haupt-Registrierung via `mcp_servers:` in `litellm-config.yaml`.

**Achtung:** LiteLLM akzeptiert keine Bindestriche in MCP-Server-Namen (`-` → `_` verwenden).

## Tools

- `liste_verfuegbare_modelle() -> str` — `litellm.utils.get_valid_models()`
- `konsultiere_expertengruppe(problemstellung, experten_modelle=None, maximale_sekunden=120) -> str`

## Tests

**Custom-Test-Runner** (kein pytest):
```posh
python test/test_debate_server.py              # alle
python test/test_debate_server.py -k grund     # nur Kategorie A
python test/test_debate_server.py -v           # verbose
```

7 Kategorien (A–G): Grundlagen, MCP-Transport stdio, Debatten-Logik, SSE, Protokoll, Edge Cases, MCP-Registrierung.

Voraussetzungen:
- `test/.env` mit `NVIDIA_API_KEY` muss existieren
- Test setzt `LITELLM_API_BASE` auf NVIDIA NIM (kein RateLimiter)
- Test setzt `LITELLM_LOG=WARNING` + `LITELLM_SUPPRESS_INFO=true`
- Test-Modell: `openai/deepseek-ai/deepseek-v4-flash` über NVIDIA NIM
- SSE-Test startet echten Server auf Port 9000
- Timeout bei Edge-Case-Tests ist gültiges Verhalten

## Deployment

```bash
docker build -t ghcr.io/peter-eske/mcp-debate-server:latest .
docker push ghcr.io/peter-eske/mcp-debate-server:latest
```

`Dockerfile` (python:3.12-slim) startet immer SSE. NGINX benötigt `proxy_buffering off`.

**LiteLLM-Config:** Modelle werden in `model_list:` der `litellm-config.yaml` definiert (versioniert, reproduzierbar). **Nicht** über Admin-API `/model/new` verwalten – LiteLLM lädt DB-Modelle nicht automatisch in den Routing-Table. `store_model_in_db: true` + `model_list` = Modelle landen in beiden Welten.

**DB-Backup:** `/root/backup_db.sh` auf VPS – `pg_dump` + gzip + 7-Tage-Retention. Manuell ausführbar nach Config-Änderungen.

**Proxy-URL:** `http://ftbot.de:4000/v1` (OpenAI-kompatibel). `opencode.json` enthält alle 30 Modelle mit Limits.

`docker-compose.yml`: Vollstack (PostgreSQL + LiteLLM + Debate-Server). `test/docker-compose.test.yml` analog.

**CI/CD**: GitHub Actions – baut/pusht bei Änderungen an Dockerfile, Server, model_roles.yaml oder requirements.txt.

## Conventions

- `EXPERTS_SYSTEM.md` ist der System-Prompt für den **aufrufenden Agent**, nicht für den Server.
- `model_roles.yaml` definiert 12 Rollen. `litellm-config.yaml` (root) = Produktion, `test/litellm-config.yaml` = Tests.
