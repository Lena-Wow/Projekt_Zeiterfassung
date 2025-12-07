import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))  # aktueller Ordner
import edit_zeiterfassung

import pandas as pd
from datetime import datetime, timedelta
import re  # re: reguläre Ausdrücke (z.B. für Spalten-Erkennung)

CSV_FILE = "zeiterfassung.csv"  # Dateiname der CSV, die gelesen und geschrieben wird.
# Vorteil: Wenn du die Datei umbenennen oder in einen anderen Ordner legen willst, änderst du nur diese eine Zeile.


st.set_page_config(page_title="Zeiterfassung", page_icon="⏰", layout="centered")
st.title("Zeiterfassung Fortführung")


def detect_duration_column(df):
    # Diese Funktion versucht, die Spalte zu finden,
    # in der die Dauer/Stunden gespeichert ist.
    for col in df.columns:
        # df.columns enthält alle Spaltennamen der eingelesenen CSV
        # Prüft: enthält der Spaltenname das Wort "dauer" oder "stunden"?
        # re.search  → durchsucht den Text
        # r"(dauer|stunden)" → Regex: entweder "dauer" ODER "stunden"
        # flags=re.IGNORECASE → Groß/Kleinschreibung egal
        if re.search(r"(dauer|stunden)", col, flags=re.IGNORECASE):
            return col  # Wenn gefunden → diesen Spaltennamen zurückgeben
    # Falls keine passende Spalte gefunden wurde,
    # Standard-Spaltenname zurückgeben:
    return "Dauer (h)"


def normalize_duration_column_values(series):
    # Innere Hilfsfunktion, die einen einzelnen Wert formatiert
    def fmt(v):
        # Wenn der Wert fehlend ist (NaN), gib leeren String zurück
        if pd.isna(v):
            return ""

        # Wenn der Wert numerisch ist (int oder float):
        # -> Formatierung in eine kompakte Darstellung
        #    z.B. 3.0 -> "3", 3.5 -> "3.5"
        # numeric -> '3.5' oder '3' -> '3,5' bzw '3'
        if isinstance(v, (int, float)):
            s = f"{v:g}"  # 3.0 -> '3', 3.5 -> '3.5'# :g entfernt unnötige Nachkommastellen
            return s.replace(".", ",")  # Dezimalpunkt -> Komma

        # Wenn der Wert als Text vorliegt:
        s = str(v).strip()
        # replace dot decimal sep with comma
        s = s.replace(".", ",")
        # Entfernt unnötige Nullen am Ende:
        # Beispiel: "3,50" -> "3,5"
        #           "2,40" -> "2,4"
        s = re.sub(r",(\d)0+$", r",\1", s)
        return s

    # wendet fmt() auf jedes Element der Series an
    return series.apply(fmt)


# Formular
with st.form("zeiterfassung_form"):
    datum = st.date_input("Datum", value=datetime.today())
    # Wochentag auf Deutsch
    tage_deutsch = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag",
    }
    weekday_en = datum.strftime("%A")  # Englischer Wochentag
    weekday = tage_deutsch[weekday_en]  # Übersetzt ins Deutsche

    st.write(f"Ausgewähltes Datum: {datum.strftime('%d.%m.%Y')}, Wochentag: {weekday}")
    # Wochentag auf Deutsch
    tage_deutsch = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag",
    }
    weekday_en = datum.strftime("%A")  # Englischer Wochentag
    weekday = tage_deutsch[weekday_en]  # Übersetzt ins Deutsche

    st.write(f"Ausgewähltes Datum: {datum.strftime('%d.%m.%Y')}, Wochentag: {weekday}")

    # Einfaches Texteingabefeld für den Namen des Kurses.
    # Der Benutzer kann hier frei einen Kurstitel eingeben.
    kursname = st.selectbox(
        "Kurs",
        [
            "– bitte auswählen –",  # neutraler Platzhalter
            "AWS",
            "Excel",
            "EDA",
            "ETL",
            "Tableau",
            "SQL",
            "ScrumPO",
            "Teilprojekt",
            "PowerBI",
            "Machine Learning",
            "Docker",
            "GitHub",
            "Statistik",
            "NoSQL",
            "Python",
            "Streamlit",
            "Projekt",
            "BigData",
            "Organisation",
            "Karrierecoaching",
        ],
    )

    # Auswahlfeld (Dropdown) für die Art des Lernens.
    # Der Benutzer muss eine der drei vordefinierten Optionen auswählen:
    # - Theorie (Video)
    # - Live-Call-Vorlesung
    # - Selbststudium
    lernart = st.selectbox(
        "Lernart",
        [
            "– bitte auswählen –",  # neutraler Platzhalter
            "Theorie (Video)",
            "Live-Call-Vorlesung",
            "Selbststudium",
            "Live-Call-Hausaufgaben",
        ],
    )

    # Eingabefeld für die Startzeit.
    # Der Benutzer wählt eine Uhrzeit aus (Stunden und Minuten).
    # Streamlit gibt ein Python-Objekt vom Typ datetime.time zurück.
    startzeit = st.time_input("Startzeit")

    # Eingabefeld für die Endzeit.
    # Auch hier wird eine Uhrzeit ausgewählt.
    # Diese wird später zusammen mit der Startzeit genutzt,
    # um die Dauer der Lerneinheit zu berechnen.
    endzeit = st.time_input("Endzeit")

    # Um die Dauer berechnen zu können, müssen wir aus den Uhrzeiten (datetime.time)
    # echte Zeitdifferenzen (timedelta) machen.

    # Startzeit in ein timedelta-Objekt umwandeln.
    # Beispiel: 14:30 -> timedelta(hours=14, minutes=30). Wird aber intern in sec gerechnet
    start_dt = timedelta(hours=startzeit.hour, minutes=startzeit.minute)

    # Endzeit ebenfalls in ein timedelta umwandeln.
    # Beispiel: 16:00 -> timedelta(hours=16, minutes=0)
    end_dt = timedelta(hours=endzeit.hour, minutes=endzeit.minute)
    # Dauer berechnen: einfach Endzeit minus Startzeit.
    # timedelta - timedelta ergibt eine Zeitspanne als timedelta.
    dauer = end_dt - start_dt

    # Falls die Endzeit vor der Startzeit liegt (z. B. Start: 22:00, Ende: 01:00),
    # wäre die Differenz negativ. In diesem Fall bedeutet es, dass die Arbeit
    # über Mitternacht ging → also 1 Tag (24 Stunden) hinzufügen.
    if dauer.total_seconds() < 0:
        dauer += timedelta(days=1)

    # Die Dauer (timedelta) in Stunden umrechnen:
    # total_seconds() liefert die Gesamtdauer in Sekunden.
    # Durch 3600 teilen ergibt Stunden.
    # round(..., 2) → auf zwei Nachkommastellen runden.
    stunden = round(dauer.total_seconds() / 3600, 2)

    # Infos für den Nutzer anzeigen: automatische Berechnung der Stunden.
    st.info(f"Dauer automatisch berechnet: {stunden} Stunden")

    # Button, um das Formular endgültig abzusenden.
    # Wenn der Nutzer auf "Eintragen" klickt, wird submitted = True.
    submitted = st.form_submit_button("Eintragen")

    if submitted:
        if kursname == "– bitte auswählen –" or lernart == "– bitte auswählen –":
            st.warning("Bitte Kurs und Lernart auswählen!")
            st.stop()  # Stoppt die weitere Ausführung, solange die Auswahl nicht getroffen ist
        # Dieser Block wird nur ausgeführt, wenn der Benutzer auf „Eintragen“ geklickt hat.
        try:
            # Versuche die bestehende CSV-Datei zu laden.
            # sep=";"  → CSV wird mit Semikolon getrennt.
            # encoding="cp1252" → wichtig, damit deutsche Sonderzeichen wie ä ö ü ß funktionieren.
            df = pd.read_csv(CSV_FILE, sep=";", encoding="cp1252")

        # Falls die Datei NICHT existiert (z. B. beim ersten Start):
        # Erstelle einen leeren DataFrame mit der richtigen Spaltenstruktur.
        # Dadurch wird die CSV beim Speichern korrekt angelegt.
        except FileNotFoundError:
            df = pd.DataFrame(
                columns=[
                    "Datum",
                    "Wochentag",
                    "Kursname",
                    "Lernart",
                    "Startzeit",
                    "Endzeit",
                    "Dauer (h)",
                ]
            )

        # Erkenne die Spalte, in der die Dauer/Stunden gespeichert sind
        duration_col = detect_duration_column(df)
        # Falls die erkannte Spalte noch gar nicht existiert (z. B. leere CSV),
        # erstelle sie und fülle sie mit leeren Strings
        if duration_col not in df.columns:
            df[duration_col] = ""

        # # Normalisiere alle EXISTIERENDEN Werte in der Dauer-Spalte
        # z. B. 3.5 → 3,5, 3.50 → 3,5
        df[duration_col] = normalize_duration_column_values(df[duration_col])

        #  Bereite die Dauer für den neuen Eintrag vor
        # 'stunden' ist ein Float, z.B. 3.0 oder 3.5

        # f"{stunden:g}" → Formatierung:
        #   - :g entfernt überflüssige Nachkommastellen bei ganzen Zahlen
        #     Beispiel: 3.0 → "3", 3.5 → "3.5"

        # .replace(".", ",") → deutsche Schreibweise:
        #   - Punkt durch Komma ersetzen, z.B. 3.5 → "3,5"
        dauer_str = f"{stunden:g}".replace(".", ",")

        #  Erstelle ein Dictionary für die neue Zeile
        # Jede Schlüssel/Wert-Paar entspricht einer Spalte in der CSV
        neue_zeile = {
            "Datum": datum.strftime("%d.%m.%Y"),
            "Wochentag": weekday,
            "Kursname": kursname,
            "Lernart": lernart,
            "Startzeit": startzeit.strftime("%H:%M"),
            "Endzeit": endzeit.strftime("%H:%M"),
            duration_col: dauer_str,
        }

        # Anhängen
        df = pd.concat([df, pd.DataFrame([neue_zeile])], ignore_index=True)

        # ***WICHTIG: Nochmals komplette Dauer-Spalte normalisieren***
        # Grund: Nach dem Anhängen der neuen Zeile kann sich der Datentyp der Spalte
        #       "Dauer" ändern (z. B. float + string = object).
        #       Power Query / CSV erwarten aber ein konsistentes Format.
        df[duration_col] = normalize_duration_column_values(df[duration_col])

        # cols_wanted
        # Hier definierst du die ideale Reihenfolge der wichtigsten Spalten.
        # Vorteil: CSV sieht sauber aus, alte Spalten + neue Spalten bleiben erhalten.
        cols_wanted = [
            "Datum",
            "Wochentag",
            "Kursname",
            "Lernart",
            "Startzeit",
            "Endzeit",
            duration_col,
        ]
        # Nur die Spalten aus cols_wanted, die wirklich existieren  +
        # Alle zusätzlichen Spalten (z. B. Kommentare, Lernmodus),
        # # die nicht in cols_wanted sind, werden hinten angehängt.
        cols_final = [c for c in cols_wanted if c in df.columns]
        # + [
        # c for c in df.columns if c not in cols_wanted]

        df = df[cols_final]

        #  Speichern des DataFrames in eine CSV-Datei
        # cp1252 → Windows-1252 / ANSI Encoding, damit deutsche Umlaute korrekt gespeichert werden
        # sep=";" → Semikolon als Trennzeichen
        # index=False → Pandas-Index nicht mit in die CSV schreiben
        # Ergebnis: CSV enthält alle alten + neuen Einträge in konsistentem Format (Dauer als '3,5')

        df.to_csv(CSV_FILE, sep=";", index=False, encoding="cp1252")
        st.success("Zeiterfassung erfolgreich gespeichert!")  # Feedback an den Benutzer
# Zeigt eine grüne Bestätigung in Streamlit, dass alles erfolgreich gespeichert wurde

# Anzeige: lade und zeige normalisierte Datei
try:
    # Lade die CSV-Datei in einen DataFrame
    # sep=";" → Semikolon-Trennzeichen
    # encoding="cp1252" → für Umlaute wie ä, ö, ü
    df_display = pd.read_csv(CSV_FILE, sep=";", encoding="cp1252")

    # Erkenne die Dauer-Spalte
    duration_col_display = detect_duration_column(df_display)

    #  Normalisiere die Werte der Dauer-Spalte, falls sie existiert
    if duration_col_display in df_display.columns:
        df_display[duration_col_display] = normalize_duration_column_values(
            df_display[duration_col_display]
        )
    # DataFrame umdrehen, damit der letzte Eintrag oben erscheint
    df_display_reversed = df_display.iloc[::-1]
    st.subheader("Bisherige Einträge")
    st.dataframe(df_display_reversed)
    edit_zeiterfassung.edit_csv(CSV_FILE)
except FileNotFoundError:
    st.info("Noch keine Einträge vorhanden.")
