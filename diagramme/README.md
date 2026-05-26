# Diagramme

**Architekturdiagramme** für den MCP-Server-Tools Debate-Server.

---

## Inhalt

| Datei | Beschreibung |
|---|---|
| `architecture.mmd` | Vollständige Systemarchitektur – alle Komponenten, Betriebsmodi, Beziehungen |

---

## Diagramm betrachten

Das Diagramm wird im [Haupt-README](../README.md) als nativer Mermaid-Block gerendert (GitHub unterstützt Mermaid nativ).

| Methode | Link |
|---|---|
| **GitHub Gist** (interaktiv) | https://gist.github.com/peter-eske/20ac8d850440b071579dac0bf1009475 |
| **mermaid.live** (bearbeiten) | https://mermaid.live/edit?gist=https://gist.github.com/peter-eske/20ac8d850440b071579dac0bf1009475 |

---

## Format

Mermaid `flowchart LR` mit 8 Subgraphen und 19 farbkodierten Knoten (Tailwind-Palette):

| Farbe | Komponententyp |
|---|---|
| Indigo | Client |
| Gelb | MCP-Server |
| Grau | Transport / Betriebsmodi |
| Blau | LiteLLM-Proxy |
| Grün | KI-Modelle |
| Rot | Speicher (DB, Config, Logs) |
| Türkis | Deployment |
| Pink | Test-Infrastruktur |

Jeder Knoten enthält eine duale Beschreibung:
- **IT:** Fachliche Beschreibung
- **Alle:** Laienverständliche Erklärung

Kanten zwischen Knoten zeigen die **Richtung des Datenflusses** und sind mit den entsprechenden Protokollen/Mechanismen beschriftet.

---

## Gist aktualisieren

```powershell
gh gist edit 20ac8d850440b071579dac0bf1009475 diagramme/architecture.mmd
```
