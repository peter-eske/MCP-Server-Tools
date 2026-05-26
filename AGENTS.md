# MCP-Server-Tools

Single-file Python MCP server (`advanced_debate_server.py`, ~350 Zeilen, 2 Tools). Server-Name: `Dynamische-KI-Expertengruppe`. Alle Strings/Kommentare auf Deutsch.

## Setup

```posh
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python advanced_debate_server.py                # SSE (default)
```

Keine `.env` für Produktion. API-Keys liegen auf dem Proxy-Host.

**`session-stand.md`** im Projekt-Root — Auto-Session-Speicherung.

**Wichtig**: `botocore` muss in der venv installiert sein, sonst erscheinen `EventStream`-Warnungen von litellm bei Bedrock/SageMaker.

## Environment

| Variable | Effekt | Default |
|---|---|---|
| `LITELLM_API_BASE` | **Required** – URL zum LiteLLM-Proxy | – |
| `LITELLM_API_KEY` | API-Key für den Proxy (optional) | `""` |
| `PORT` / `HOST` | SSE-Port/Host | `8000` / `0.0.0.0` |

Nur **Proxy-Modus** – `LITELLM_API_BASE` muss gesetzt sein. Kein Direkt-Modus, kein RateLimiter.

OpenAI-Client (`openai.OpenAI`, `max_retries=0`) wird **einmalig** auf Modulebene erstellt, nicht pro Aufruf. `base_url` **ohne** `/v1`-Suffix (SDK hängt automatisch an).

## Architektur

Drei-Phasen-Loop in `konsultiere_expertengruppe`:
1. **Completeness-Check** — Chef-Modell via `response_format={"type": "json_object"}`. `NEED_INFO` = früher Return. Exceptions → silent pass.
2. **Chef-moderierte Debatte** — JSON-Kommandos: `runde` (parallel via `asyncio.gather`), `synthese` (fertig), `beenden` (abbruch). Chef weist Rollen zu (12 Rollen aus `model_roles.yaml`). Bei JSON-Parse-Fehler automatisch `runde` mit allen Modellen. `max_tokens=512` für Chef, `max_tokens=1024` für Modelle. Hard-Stop bei `maximale_sekunden` (Default 120s). Max 5 Modelle.
3. **Synthese** — Chef-Modell klassifiziert: `ERFOLG` / `TEILERGEBNIS` / `RATLOSIGKEIT`. `max_tokens=2048`.

Debatte-Logs: `logs/debates/debate_{timestamp}.md` (relativ zu CWD).

**Modell-Rollen** werden aus `model_roles.yaml` geladen (12 Rollen mit Top-3-Empfehlungen). Fallback auf Default-Liste bei Fehler.

**MCP-Registrierung**: `_register_at_litellm()` als Background-Thread beim Start (exponential backoff, max 20 Versuche). Fallback-Mechanismus – Haupt-Registrierung erfolgt via `mcp_servers:` in `litellm-config.yaml`.

## Tools

- `liste_verfuegbare_modelle() -> str` — `litellm.utils.get_valid_models()`
- `konsultiere_expertengruppe(problemstellung, experten_modelle=None, maximale_sekunden=120) -> str`

Default-Modelle: Aus `model_roles.yaml` (`default_experten`), Fallback `claude-3-5-sonnet`, `gpt-4o`, `gemini/gemini-2.5-flash`.

## Tests

**Custom-Test-Runner** (kein pytest):
```posh
python test/test_debate_server.py              # alle
python test/test_debate_server.py -k grund     # nur Kategorie A
python test/test_debate_server.py -v           # verbose
```

7 Kategorien (A–G): Grundlagen, MCP-Transport, Debatten-Logik, SSE, Protokoll, Edge Cases, MCP-Registrierung.

Test-Prerequisites:
- `test/.env` mit `NVIDIA_API_KEY` muss existieren
- Test setzt `LITELLM_API_BASE` auf NVIDIA NIM-URL → kein RateLimiter
- Test setzt `LITELLM_LOG=WARNING` + `LITELLM_SUPPRESS_INFO=true`
- Test-Modell: `deepseek-ai/deepseek-v4-flash` (über NVIDIA NIM, mit `openai/` Prefix)
- SSE-Test startet echten Server auf Port 9000
- Einige Edge-Case-Tests akzeptieren Timeout als gültiges Verhalten

## Deployment

```bash
docker build -t ghcr.io/peter-eske/mcp-debate-server:latest .
docker push ghcr.io/peter-eske/mcp-debate-server:latest
```

`Dockerfile` (python:3.12-slim) startet in SSE-Mode (immer). NGINX benötigt `proxy_buffering off` für SSE.

`docker-compose.yml` (Vollstack: PostgreSQL + LiteLLM + Debate-Server). `test/docker-compose.test.yml` mit gleicher Struktur.

**CI/CD**: GitHub Actions (`.github/workflows/docker-publish.yml`) baut und publiziert bei Änderungen an Dockerfile, Server, model_roles.yaml oder requirements.txt.

## Rollen (aus model_roles.yaml)

| Rolle | Beschreibung |
|---|---|
| Projektmanager | Koordiniert, fasst zusammen, priorisiert |
| System-Architekt | Entwirft Architektur, Komponenten, Schnittstellen |
| Code-Analyst | Analysiert Code, implementiert, optimiert |
| Security-Experte | Prüft Sicherheit, OWASP, Auth |
| DB-Spezialist | Datenbankdesign, Queries, Migrationen |
| DevOps | Infrastruktur, CI/CD, Deployment |
| UI/UX-Designer | Oberflächen, Interaktion, Accessibility |
| QA-Tester | Teststrategie, Testfälle, Automatisierung |
| Product-Owner | Anforderungen, User Stories |
| Performance-Optimierer | Laufzeit, Speicher, Caching |
| Dokumentations-Experte | Technische Dokumentation, API-Refs |
| Kritischer-Reviewer | Code/Architektur-Review, Risikoanalyse |

## Conventions

- `EXPERTS_SYSTEM.md` ist der System-Prompt für den **aufrufenden Agent**, nicht für den Server.
- `model_roles.yaml` definiert Rollen + Modell-Empfehlungen für die Debatte.
- `litellm-config.yaml` (root) = Produktion, `test/litellm-config.yaml` = Tests.
- Keine Linting-, CI- oder Build-Skripte (außer docker-publish.yml).
