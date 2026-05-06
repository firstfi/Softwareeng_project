# Softwareeng_project
Project for software engeneering
# StudySync — Intelligente Lern-App mit Kalenderintegration

> Dein persönlicher Lernplaner, der weiß wann du Zeit hast und wie viel du noch brauchst.

---

## Projektübersicht

StudySync ist eine Lern-App, die deinen Kalender analysiert und automatisch optimale Lernzeiten plant. Sie berücksichtigt deine Prüfungsdaten, deinen aktuellen Lernfortschritt und dein persönliches Lerntempo — und erstellt daraus einen realistischen, individuellen Lernplan.

---

## Features

### Kalenderintegration
- Verbindung mit Google Calendar & Apple Calendar
- Automatische Erkennung freier Zeitfenster
- Lernblöcke werden direkt in den Kalender eingetragen
- Bearbeitung und Verschieben von Sessions möglich

### Lernplanung
- Prüfungsdaten & Deadlines erfassen
- Automatische Zeitschätzung pro Fach
- Smarte Sessions: schwere Themen in energiereiche Zeiten legen
- Persönliches Lerntempo wird über die Zeit erkannt und angepasst

### Fortschrittsanzeige
- Fortschrittsbalken pro Fach (0–100%)
- Übersicht bereits erledigter Aufgaben
- Wochenrecap: geplante vs. tatsächliche Lernzeit
- Streak-Anzeige für regelmäßiges Lernen

### Wiederholungen
- Spaced Repetition: optimale Wiederholungsintervalle
- Confidence-Rating nach jeder Session

### Microlearning & Benachrichtigungen
- Kurze 5–15 min Sessions für Pausen oder Pendeln
- Smarte Push-Notifications (nicht während anderer Termine)

### UI & Komfort
- Dark Mode & Light Mode
- Offline-Modus mit automatischer Synchronisation
- Individuelle Farbgebung

---

## Zielgruppen

| Persona | Beschreibung |
|---|---|
| Studenten | Prüfungsvorbereitung mit mehreren Fächern gleichzeitig |
| Lektoren | Strukturiertes Lernen und Wiederholungsmanagement |
| - Weiterbildung neben dem Job, kleine Lerneinheiten |

---

## User Stories (GitHub Issues)

Alle User Stories sind als GitHub Issues im Repository angelegt:

| # | Titel | Epic |
|---|---|---|
| #6 | User Story Studenten | Intelligente Lernplanung P0 |
| #7 | User Story Lektoren | Intelligente Lernplanung P0 |
| #9 | User Story Programmierer | Intelligente Lernplanung P0 | 
| #10 | UserStory Einkaufen | Infotracker |
| #11 | User Story Dark Mode | Dark und Light Mode |
| #12 | User Story Offline-Mode | Offline Modus |
| #13 | User Story Streak & Lernstatistiken | Streak Anzeige |
| #14 | User Story Fortschritt | Infotracker |
| #15 | User Story Smarte Sessions | Aufgabenmanagement |
| #16 | User Story Persönliches Lerntempo | Intelligente Lernplanung |
| #17 | User Story Prüfungsdaten erfassen | Intelligente Lernplanung |
| #18 | User Story Kalendervernüpfung | Kalenderfeature |
| #19 | User Story Microlearning & Benachrichtigungen | Intelligente Lernplanung |
| #20 | User Story Wiederholungen | Intelligente Lernplanung |
| #21 | User story Übersicht | Infotracker P0 | 
| #22 | User Story Dauer | Aufgabenmanagement P0 | 
| #23 | User Story Bearbeitung | Kalenderfeature P0 |
| #24 | User Story Umstrukturierung | Aufgabenmanagement |
| #26 | User Story bereits erledigte Aufgaben | Infotracker |
| #27 | User Story Wochenrecap | Infotracker |
| #28 | User Story Farben | — |

---

## Projektstruktur

```
studysync/
├── src/
│   ├── features/
│   │   ├── calendar/        # Kalenderintegration
│   │   ├── planner/         # Lernplanung & Zeitschätzung
│   │   ├── tracker/         # Fortschrittsanzeige
│   │   ├── repetition/      # Spaced Repetition
│   │   └── notifications/   # Benachrichtigungen
│   ├── components/          # Wiederverwendbare UI-Komponenten
│   └── utils/               # Hilfsfunktionen
├── docs/                    # Dokumentation
└── README.md
```

---

## Roadmap

### Phase 1 — MVP (aktuell)
- [x] Kalenderintegration
- [x] Lernplanung & Zeitschätzung
- [x] Fortschrittsanzeige

### Phase 2 — In Arbeit
- [ ] Streak & Wochenrecap
- [ ] Dark Mode
- [ ] Offline-Modus
- [ ] Smarte Benachrichtigungen

### Phase 3 — Geplant
- [ ] Spaced Repetition / Wiederholungen
- [ ] Microlearning-Sessions
- [ ] Persönliches Lerntempo
- [ ] Lerngruppen

---

## Team

| GitHub | Rolle |
|---|---|
| @yungreindl | Developer |
| @JonasSTD | Developer |
| @Jana816 | Developer |
| @Cora44 | Dveloper |
| @firstfi | Scrammaster |
| @maximilianpapst160-spec | Product-Owner (versteht leider garnichts) |


---

## Lizenz

Dieses Projekt entsteht im Rahmen eines Schulprojekts.
