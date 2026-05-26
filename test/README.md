# Tests

**Test-Infrastruktur** für den Debate-Server mit eigenem Test-Runner (kein pytest/unittest).

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](python)

---

## Inhalt

| Datei | Beschreibung |
|---|---|
| `test_debate_server.py` | Haupt-Test-Skript (890 Zeilen, 6 Kategorien) |
| `.env` | API-Keys (gitignored – `NVIDIA_API_KEY`, `POSTGRES_PASSWORD`) |
| `docker-compose.test.yml` | Vollständiger Test-Stack: Postgres + LiteLLM + Debate-Server |
| `litellm-config.yaml` | LiteLLM-Konfiguration mit NVIDIA NIM-Modellen |
| `completion_body.json` | JSON-Template für API-Call-Tests |
| `key_body.json` | JSON-Template für Key-Generierung |
| `quick_test.py` | Schneller Smoke-Test |
| `test_debate_via_sse.py` | SSE-Protokoll-Test |
| `test_http.py` | HTTP-Endpoint-Tests |
| `test_mcp_spe.py` | MCP-over-SSE-Test |
| `test_openai.py` | OpenAI-Client-Kompatibilitätstest |

---

## Test-Runner

Das Haupt-Test-Skript `test_debate_server.py` verwendet einen **eigenen Test-Runner** – kein pytest, kein unittest.

```bash
# Alle Tests ausführen
python test/test_debate_server.py

# Nur eine Kategorie filtern
python test/test_debate_server.py -k grund

# Ausführliche Ausgabe
python test/test_debate_server.py -v
```

---

## Test-Kategorien

| Kategorie | Beschreibung | Umfang |
|---|---|---|
| **A – Grundlagen** | Environment-Variablen, LiteLLM-Verbindung, Modellverfügbarkeit | ✅ |
| **B – MCP-Transport (stdio)** | Server-Start, Tool-Registrierung, Tool-Aufruf | ✅ |
| **C – Debatten-Logik** | Vollständige Debatte, `NEED_INFO`, Zeitlimit (maximale_sekunden) | ✅ |
| **D – SSE-Transport** | HTTP-Server-Start, SSE-Endpoint, MCP-Nachrichten | ✅ |
| **E – Protokoll-Ausgabe** | Markdown-Format, Klassifikation (`ERFOLG`/`TEILERGEBNIS`/`RATLOSIGKEIT`), Dateipfad | ✅ |
| **F – Edge Cases** | Ungültige API-Base, fehlender API-Key, >5 Modell-Trunkierung, leere Modell-Liste | ✅ |

---

## Voraussetzungen

### 1. `.env` Datei

`test/.env` muss existieren und folgende Variablen enthalten:

```env
NVIDIA_API_KEY=nvapi-...
POSTGRES_PASSWORD=secure_password
OPENCODE_API_KEY=sk-...
```

### 2. Test-Modell

Der Test nutzt `deepseek-ai/deepseek-v4-flash` über **NVIDIA NIM** (`https://integrate.api.nvidia.com/v1`).

Das Test-Skript setzt automatisch:
- `LITELLM_API_BASE=https://integrate.api.nvidia.com/v1` → RateLimiter deaktiviert
- `LITELLM_LOG=WARNING` – Provider-List-Spam unterdrücken
- `LITELLM_SUPPRESS_INFO=true` – zusätzliche Informationsausgabe unterdrücken

### 3. Docker (für SSE-Tests)

Die SSE-Tests (Kategorie D) starten einen **echten HTTP-Server auf Port 9000** und benötigen daher keine Container. Der vollständige Stack mit Postgres und LiteLLM steht via `docker-compose.test.yml` bereit:

```bash
docker compose -f test/docker-compose.test.yml up -d
```

---

## Test-Stack (Docker)

```yaml
services:
  postgres:          # PostgreSQL 16 für LiteLLM-Usage-DB
  litellm-gateway:   # LiteLLM-Proxy auf :4000
  debate-server:     # Debate-Server auf :8000
```

Alle drei Container laufen mit `restart: unless-stopped` und teilen sich das Netzwerk. Der Debate-Server verbindet sich via `http://litellm-gateway:4000`.

---

## Edge Cases

Folgende Grenzfälle werden explizit getestet:

| Test | Erwartung |
|---|---|
| `LITELLM_API_BASE` auf ungültige URL gesetzt | Server startet, API-Call schlägt fehl |
| Kein API-Key gesetzt | Klar definierte Fehlermeldung |
| >5 Modelle übergeben | Wird auf 5 gekürzt |
| Leere Modell-Liste (`[]`) | Fallback auf Default-Modelle |
| Timeout bei `maximale_sekunden=1` | Abbruch mit `TEILERGEBNIS` oder `RATLOSIGKEIT` |
