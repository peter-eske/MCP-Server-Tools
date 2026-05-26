# Dokumentation: Interaktives KI-Experten-Debatten-System (MCP)

Dieses Dokument dient als System-Anweisung und Architektur-Erklärung für die Haupt-KI. Es beschreibt den Zweck, den Ablauf und die Verhaltensregeln für die Nutzung des angeschlossenen MCP-Tools `konsultiere_expertengruppe`.

---

## 1. Strategischer Plan (Die Vision)

Bei der Planung großer Software-Architekturen oder der Lösung komplexer, hartnäckiger Bugs stößt ein einzelnes KI-Modell oft an seine Grenzen (Gefahr von Halluzinationen oder Tunnelblick).

**Der Plan für dieses System ist es, Qualität durch Diversität und kollaborative Intelligenz zu sichern:**

1. **Spezialisierung:** Komplexe Aufgaben werden an eine Gruppe unterschiedlicher Top-Modelle (Claude, GPT, Gemini) übergeben, die über das `litellm`-Backend orchestriert werden.
2. **Qualitätssicherung:** Die Modelle agieren als unabhängige Experten (Architekt, Code-Analyst, Security-Spezialist) und korrigieren sich gegenseitig in einer simulierten Debatte.
3. **Effizienz:** Die Diskussion läuft vollautomatisch im Hintergrund ab, ist jedoch streng zeitbegrenzt, um Deadlocks und unnötigen Token-Verbrauch zu verhindern.

---

## 2. Funktionsweise des Codes (`advanced_debate_server.py`)

Das MCP-Werkzeug basiert auf einer dreistufigen, asynchronen Python-Architektur:

### Phase 1: Vollständigkeitsprüfung (Pruning)

Bevor Rechenzeit verschwendet wird, prüft das Tool über das Architekten-Modell, ob die übergebene Problemstellung präzise genug ist.

- **Verhalten bei unvollständigen Daten:** Das Tool bricht sofort ab und liefert eine strukturierte Liste mit Rückfragen im JSON-Format.

### Phase 2: Zeitgesteuerte asynchrone Debatte

Das Tool startet eine dynamische Schleife (`asyncio`), die rollierend Statements der verschiedenen Experten einholt. Jedes Modell liest die Argumente der Vorgänger und baut darauf auf.

- **Die Zeitbegrenzung:** Das System misst die verstrichene Zeit (`time.time()`). Sobald das Limit (`max_seconds`, Standard: 45s) erreicht wird, bricht die Schleife *hart* ab, unabhängig davon, wer gerade spricht.

### Phase 3: Synthese und Validierung

Ein finales Modell analysiert das Protokoll der Debatte und kategorisiert das Ergebnis in drei mögliche Zustände:

1. **Erfolg:** Ein klarer, konsolidierter Lösungs- und Architekturplan.
2. **Teilergebnis:** Das Zeitlimit wurde erreicht. Die KI liefert den bis dahin erarbeiteten Stand und benennt die noch offenen Fragen.
3. **Ratlosigkeit:** Die Experten kamen zu keinem Ergebnis oder widersprechen sich fundamental. Das Tool deklariert dies offen, statt eine falsche Lösung zu erfinden.

---

## 3. Handlungsanweisungen für die Haupt-KI

Als primäre Arbeits-KI in diesem Workspace musst du dich strikt an folgende Interaktionsregeln halten:

### Wann du das Tool aufrufen MUSST:

- Wenn der Benutzer eine App-Architektur von Grund auf plant.
- Wenn Refactorings über mehrere Dateien hinweg anstehen.
- Wenn ein Bug nach zwei Fehlversuchen deinerseits nicht behoben werden konnte.

### Wie du mit den Rückgabewerten umgehst:

1. **Wenn das Tool Fragen zurückgibt (Zusatzinfos benötigt):**
   - Unterbrich deine Code-Generierung sofort.
   - Präsentiere dem Benutzer die Fragen der Expertengruppe im Terminal und bitte ihn um Klärung.
   - Starte den Tool-Aufruf erneut, sobald du die Antworten des Benutzers hast.

2. **Wenn das Tool ein 'TEILERGEBNIS' liefert:**
   - Implementiere nur die Teile des Codes, die von der Gruppe als sicher und beschlossen deklariert wurden.
   - Weise den Benutzer transparent darauf hin, welche Architekturfragen aufgrund des Zeitlimits offen geblieben sind.

3. **Wenn das Tool 'DIE EXPERTENGRUPPE IST RATLOS' zurückgibt:**
   - Generiere auf keinen Fall eigenen Code auf Gutglück!
   - Zeige dem Benutzer die Begründung der Expertengruppe.
   - Bitte den Benutzer um architektonische Vorgaben oder schlage alternative Lösungswege vor.

### 4. Zweistufiger Workflow zur dynamischen Experten-Auswahl

Du besitzt die Fähigkeit, dein Expertenteam komplett selbstständig und maßgeschneidert für jedes Problem zusammenzustellen. Befolge dabei immer diese zwei Schritte:

#### Schritt 1: Liste abrufen
Bevor du die Expertengruppe konsultierst, rufst du das Tool `liste_verfuegbare_modelle` auf. Dadurch erfährst du live, welche KIs auf dem Server einsatzbereit konfiguriert sind.

#### Schritt 2: Team zusammenstellen (Maximal 5 Modelle)
Analysiere dein aktuelles Problem und wähle aus der erhaltenen Liste **mindestens 2 und maximal 5 Modelle** aus, die am besten zur Aufgabe passen.

*Beispiele für deine logische Auswahl:*
- **Hartnäckiger Code-Bug (Fokus Logik):** Wähle 3 bis 4 verschiedene Top-Modelle für maximalen logischen Abgleich (z. B. `gpt-4o`, `claude-3-5-sonnet`, `deepseek-coder`).
- **Große App-Planung (Fokus Vielseitigkeit):** Nutze das Limit von 5 Modellen voll aus, um unterschiedliche Perspektiven zu erhalten (z. B. 1x Architektur-Spezialist, 2x Code-Analysten, 1x Security-Spezialist, 1x Cloud/Infrastruktur-Spezialist).

**Einschränkung:** Übergib niemals mehr als 5 Modelle im Parameter `experten_modelle`. Das System schneidet überschüssige Modelle automatisch ab.
