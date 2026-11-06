from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")


@st.cache_data
def charger_donnees():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")


df = charger_donnees()

st.write("Ce tableau rassemble les relevés mensuels de 12 quartiers, de janvier 2024 à décembre 2025.")
st.write("Chaque relevé combine consommation, abonnés, heures de courant et données météo.")
st.dataframe(df, hide_index=True)