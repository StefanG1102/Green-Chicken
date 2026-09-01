# Green-Chicken

> Das Programm sorgt dafür das Analyse Berreiche festgelegt werden können die auf den Grünen Farbton überprüft werden. Damit lässt sich feststellen wieviel Prozent in den jeweiligen Berreichen Grün ist. Durch sogennante Dead Zones können in den Analyse Berreichen festgelegt werden was nicht beachtet werden soll.

---

## Inhaltsverzeichnis

- [Über das Projekt](#über-das-projekt)
- [Projektstruktur](#projektstruktur)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [Windows-Version (.exe)](#windows-version-exe)
- [Zitieren](#zitieren)
- [Autor](#autor)
- [Lizenz](#lizenz)

---

## Über das Projekt (Work in Progress)



## Projektstruktur

```
projektname/
├── main.py              # Einstiegspunkt des Programms
├── modul_a/              # Beschreibung des Ordners
├── modul_b/              # Beschreibung des Ordners
├── export/                # Ausgabeordner für Ergebnisse (wird automatisch erstellt)
├── requirements.txt       # Python-Abhängigkeiten
├── icon.ico                # App-Icon für die .exe
└── README.md
```

## Installation

### Voraussetzungen

- Python 3.x 
- pip

### Setup

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
pip install -r requirements.txt
```

## Verwendung

```bash
python main.py
```

Die Ergebnisse werden im Ordner `export/` abgelegt.


## Windows-Version (.exe)

Für Nutzer ohne Python-Installation steht eine ausführbare Windows-Datei zur Verfügung.

Build selbst erstellen:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

Die fertige `.exe` liegt danach im Ordner `dist/`. Der `export/`-Ordner wird beim ersten Programmstart automatisch neben der `.exe` erstellt.

## Zitieren

Falls du dieses Projekt oder Teile davon in eigener Forschung, einer Arbeit oder einem Projekt verwendest, zitiere es bitte wie folgt.

**APA:**

```
Nachname, V. (2026). Projektname (Version 1.0) [Computer software]. GitHub. https://github.com/<username>/<repo>
```

**BibTeX:**

```bibtex
@software{nachname2026projektname,
  author  = {Nachname, Vorname},
  title   = {Projektname},
  year    = {2026},
  version = {1.0},
  url     = {https://github.com/<username>/<repo>},
  note    = {Universität, im Rahmen von [Veranstaltung]}
}
```

## Autor

- **Name:** [Dein Name]
- **Universität:** [Name der Universität]
- **Kontakt:** [E-Mail, optional]

## Funktionsweise

Die Software ist in **fünf Bereiche** (Tabs) gegliedert, die der Nutzer von links nach rechts durchläuft: **Datei**, **Bereiche**, **Dead Zones**, **Analyse** und **Export**.

### 1. Datei

Hier startet der Nutzer den Workflow. Zur Auswahl stehen:

- **Datei auswählen** – öffnet den Windows-Explorer, in dem ein Bild ausgewählt werden kann. Das gewählte Bild wird anschließend als **Originalbild** in der Software angezeigt.
- **Beenden** – schließt die Anwendung.

Im angezeigten Bild kann jederzeit navigiert werden:
- **Rechte Maustaste (gedrückt halten + bewegen):** Bild verschieben
- **Mausrad:** Bild zoomen

### 2. Bereiche

Sobald das richtige Bild geladen ist, können hier die zu untersuchenden **Bereiche** festgelegt werden:

- **Linksklick** im Bild setzt einen Punkt. Jeder neue Punkt wird automatisch mit dem vorherigen verbunden.
- **Doppelklick** setzt den letzten Punkt und schließt den Bereich, indem dieser Punkt mit dem allerersten Punkt verbunden wird – es entsteht ein geschlossenes Polygon.
- Es können **beliebig viele Bereiche** definiert werden.

### 3. Dead Zones

In diesem Tab lassen sich innerhalb der zuvor definierten Bereiche **Dead Zones** markieren – also Teilflächen, die bei der späteren Analyse ignoriert werden sollen.

- Vor dem Platzieren einer Dead Zone muss zunächst der **Bereich ausgewählt** werden, dem sie zugeordnet werden soll.
- Das Platzieren erfolgt nach demselben Prinzip wie bei den Bereichen: Linksklick setzt Punkte, Doppelklick schließt die Dead Zone.

### 4. Analyse

Hier stehen dem Nutzer **zwei Filter** zur Auswahl sowie die Möglichkeit, die **Analyse zu starten**.

Nach dem Start der Analyse:
- wird im unteren Teil der Software eine **Ergebnistabelle** erzeugt,
- und im Bereich **Analysebild** eine Art **Negativbild** als visuelle Auswertung angezeigt.

### 5. Export

Im letzten Tab können die Ergebnisse der Analyse gesichert werden:

- Export des **Analysebilds**
- Export der **Ergebnistabelle**

---

### Ablauf im Überblick

```
Datei  →  Bereiche  →  Dead Zones  →  Analyse  →  Export
  |           |              |            |           |
Bild      Bereiche      Ignorierte     Filter +    Analysebild
laden     festlegen     Teilflächen    Start       & Tabelle
                         festlegen                  exportieren
```

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE)
