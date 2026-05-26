# Diagramme – MCP-Server-Tools

Dieser Ordner enthält Mermaid-Diagramme zur Architektur und zum Datenfluss.

## Inhalt

| Datei | Beschreibung |
|---|---|
| `architecture.mmd` | LangGraph-Architektur: Supervisor-basierter Experten-Dialog |
| `code.mmd` | Kopie für mermaid.live (Gist-Datei) |

## In mermaid.live öffnen

Im Editor bearbeiten:
```
https://mermaid.live/edit?gist=https://gist.github.com/peter-eske/20ac8d850440b071579dac0bf1009475
```

Nur anzeigen (View-Only):
```
https://mermaid.live/view?gist=https://gist.github.com/peter-eske/20ac8d850440b071579dac0bf1009475
```

## Wichtig

Die Gist-Datei muss `code.mmd` heißen – das ist das von mermaid.live erwartete Format.

## Gist aktualisieren

Nach Änderungen an `architecture.mmd` auch in `code.mmd` kopieren und Gist updaten:

```powershell
cp diagramme/architecture.mmd diagramme/code.mmd
gh gist edit 20ac8d850440b071579dac0bf1009475 diagramme/code.mmd
```
