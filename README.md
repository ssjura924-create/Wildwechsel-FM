# Wildwechsel FM

Produktionssoftware für deutschsprachige GTA-Kurzvideos mit Ralle, dem Waschbären. Ziel: Gameplay, Moderation, Untertitel und MP4-Export verbinden.

Status: Entwicklung. Keine automatische Veröffentlichung ohne geprüfte Inhalte und Nutzungsrechte.

## Folge produzieren

In GitHub unter Actions den Workflow **Wildwechsel FM - Folge produzieren** öffnen.
- **preview**: synthetisierte deutsche Stimme, exakt auf die Sprachabschnitte abgestimmte Untertitel, neutrale Testfläche.
- **episode**: eigene bzw. lizenzierte Aufnahme als `inputs/gameplay.mp4` und transparenter Ralle als `inputs/ralle.png` (Standbild mit leichter Bewegung) oder `inputs/ralle.webm` (fertige Alpha-Animation).
- Moderation in kurzen Sätzen eingeben, getrennt durch |. Maximal 60 Sekunden.
- Unter Artefakte steht `wildwechsel-folge` mit MP4, WAV und SRT zum Download.

Die Stimme wird mit Piper und dem deutschen Modell Thorsten High ohne kostenpflichtige Sprach-API erzeugt. [Modellkarte](https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/de/de_DE/thorsten/high/MODEL_CARD).

Das Repository ist öffentlich. Keine privaten Daten, Zugangsdaten oder Aufnahmen ohne Veröffentlichungsrechte hochladen. Der Workflow veröffentlicht nichts auf TikTok. Ein transparentes Overlay ersetzt keine echte 3D-Integration oder Lippensynchronisation.
