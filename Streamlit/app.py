import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time, timedelta

# Importiere das Modul (gleicher Ordner)
import courses_module as cm

st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️", layout="wide")

CSV_PATH = Path(__file__).parent / "time_entries.csv"
# Standard: lädt courses.txt im aktuellen Arbeitsverzeichnis (oder erzeugt sie)
courses = cm.load_courses()  # -> List[str]


# ------------------- Funktionen -------------------
def load_data():
    if CSV_PATH.exists():
        return pd.read_csv(
            CSV_PATH,
            parse_dates=["Datum", "Startzeit", "Endzeit", "Created_at"],
            dayfirst=True,
        )
    else:
        return pd.DataFrame(
            columns=[
                "Datum",
                "Wochentag",
                "Kursname",
                "Lernart",
                "Thema / Inhalt",
                "Startzeit",
                "Endzeit",
                "Dauer (h)",
                "Lernmodus / Quelle",
                "Beschreibung",
                "Created_at",
            ]
        )


def save_entry(entry: dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)


def compute_weekday_de(d: date) -> str:
    weekdays = [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
        "Samstag",
        "Sonntag",
    ]
    return weekdays[d.weekday()]


def compute_duration_hours(start_dt: datetime, end_dt: datetime) -> float:
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    delta = end_dt - start_dt
    return round(delta.total_seconds() / 3600, 2)


# ------------------- Eingabefelder außerhalb des Formulars für Live-Dauer -------------------
st.title("⏱️ Zeiterfassung – Eintrag erstellen")

# Datum & Wochentag
datum = st.date_input("Datum", value=date.today())
wochentag = st.selectbox(
    "Wochentag",
    options=[
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
        "Samstag",
        "Sonntag",
    ],
    index=datetime.today().weekday(),
)

# Kurs & Lernart
# kursname = st.selectbox("Kursname",options=["Projekt","Python","SQL","ML","Excel","EDA","ETL","PowerBI","AWS","ScrumPO",],)
kursname = st.selectbox("Kursname", options=courses)

lernart = st.selectbox(
    "Lernart",
    options=[
        "Selbststudium",
        "Live-Call-Vorlesung",
        "Theorie-Video",
        "Live-Call-Hausaufgaben",
        "Sonstiges",
    ],
)

# Thema / Inhalt
thema = st.text_input("Thema / Inhalt", placeholder="z. B. Streamlit Formular")

# Startzeit / Endzeit
col1, col2, col3 = st.columns([1.5, 1.5, 2])
with col1:
    start_time = st.time_input("Startzeit", value=time(9, 0))
with col2:
    end_time = st.time_input("Endzeit", value=time(10, 0))

# Dauer automatisch berechnen
start_dt = datetime.combine(datum, start_time)
end_dt = datetime.combine(datum, end_time)
computed_duration = compute_duration_hours(start_dt, end_dt)

# Dauer manuell anpassen
with col3:
    dauer_manual = st.number_input(
        "Dauer (h)",
        min_value=0.0,
        step=0.25,
        value=float(computed_duration),
        format="%.2f",
    )

# Lernmodus / Beschreibung
lernmodus = st.selectbox(
    "Lernmodus / Quelle",
    options=[
        "Eigenständig",
        "Udemy",
        "DSI",
        "YouTube",
        "Excel",
        "Python",
        "GPT",
        "Buch",
        "Sonstiges",
    ],
)
beschreibung = st.text_area(
    "Beschreibung / Notizen (optional)",
    height=80,
    placeholder="Kurznotiz, was du gemacht hast",
)

# Submit Button
if st.button("Speichern"):
    final_duration = (
        dauer_manual
        if abs(dauer_manual - computed_duration) > 0.001
        else computed_duration
    )
    entry = {
        "Datum": datum.isoformat(),
        "Wochentag": wochentag,
        "Kursname": kursname,
        "Lernart": lernart,
        "Thema / Inhalt": thema,
        "Startzeit": datetime.combine(datum, start_time).isoformat(),
        "Endzeit": datetime.combine(datum, end_time).isoformat(),
        "Dauer (h)": float(final_duration),
        "Lernmodus / Quelle": lernmodus,
        "Beschreibung": beschreibung,
        "Created_at": datetime.now().isoformat(),
    }
    save_entry(entry)
    st.success("Eintrag gespeichert ✅")
