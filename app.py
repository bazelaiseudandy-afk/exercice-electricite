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
communes = sorted(df["commune"].unique())
communes_choisies = st.sidebar.multiselect(
    "Communes",
    communes,
    default=communes
)

annees = sorted(df["annee"].unique())
annee = st.sidebar.selectbox(
    "Année",
    annees,
    index=annees.index(2025)
)

if not communes_choisies:
    st.info("Choisissez au moins une commune.")
else:
    filtre = df[
        df["commune"].isin(communes_choisies)
        & (df["annee"] == annee)
    ]

    total_kwh = filtre["kwh"].sum()
    kwh_par_abonne = filtre["kwh_par_abonne"].mean()
    heures_moyennes = filtre["heures_courant"].mean()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Consommation totale", f"{total_kwh / 1_000_000:.2f} M kWh")
    with col2:
        st.metric("Consommation par abonné", f"{kwh_par_abonne:.1f} kWh")
    with col3:
        st.metric("Heures de courant", f"{heures_moyennes:.1f} h/jour")

    st.dataframe(filtre, hide_index=True)