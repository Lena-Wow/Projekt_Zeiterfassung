# edit_zeiterfassung.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import re


def detect_duration_column(df):
    for col in df.columns:
        if re.search(r"(dauer|stunden)", col, flags=re.IGNORECASE):
            return col
    return "Dauer (h)"


def normalize_duration_column_values(series):
    def fmt(v):
        if pd.isna(v):
            return ""
        if isinstance(v, (int, float)):
            s = f"{v:g}"
            return s.replace(".", ",")
        s = str(v).strip().replace(".", ",")
        s = re.sub(r",(\d)0+$", r",\1", s)
        return s

    return series.apply(fmt)


def edit_csv(csv_file):
    try:
        df = pd.read_csv(csv_file, sep=";", encoding="cp1252")
    except FileNotFoundError:
        st.info("Noch keine Einträge vorhanden.")
        return

    duration_col = detect_duration_column(df)
    if duration_col in df.columns:
        df[duration_col] = normalize_duration_column_values(df[duration_col])

    df_reversed = df.iloc[::-1]
    # st.subheader("Bisherige Einträge")
    # st.dataframe(df_reversed)

    st.subheader("Eintrag korrigieren")

    if df.empty:
        st.info("Keine Einträge zum Bearbeiten vorhanden.")
        return

    # Dropdown: wähle Eintrag aus
    options = df.apply(
        lambda row: f"{row['Datum']} | {row['Kursname']} | {row['Lernart']}", axis=1
    )
    selected_entry = st.selectbox("Welchen Eintrag korrigieren?", options)
