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

        analyses = df[df["commune"].isin(communes_choisies)]

    onglets = st.tabs([
        "Par quartier",
        "Évolution",
        "Chaleur ou courant ?",
        "Coupures",
        "Records",
    ])

    with onglets[0]:
        moyenne_quartier = (
            analyses.groupby("quartier")["kwh_par_abonne"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(moyenne_quartier, alt="Consommation moyenne par abonné et par quartier")
        st.write(
            f"{moyenne_quartier.index[0]} arrive en tête avec "
            f"{moyenne_quartier.iloc[0]:.1f} kWh par abonné."
        )

    with onglets[1]:
        mensuel = analyses.pivot_table(
            index="mois",
            columns="commune",
            values="kwh_par_abonne",
            aggfunc="mean",
        )
        st.line_chart(mensuel, alt="Évolution mensuelle par commune")

        totaux = analyses.groupby(["commune", "annee"])["kwh"].sum().unstack()
        variations = ((totaux[2025] / totaux[2024] - 1) * 100).sort_values()
        st.write(
            f"La hausse va de {variations.iloc[0]:.1f} % à "
            f"{variations.iloc[-1]:.1f} % selon la commune."
        )

    with onglets[2]:
        residentiel = analyses[analyses["type"] == "Résidentiel"]
        st.scatter_chart(
            residentiel,
            x="heures_courant",
            y="kwh_par_abonne",
            alt="Consommation par abonné selon les heures de courant",
        )
        corr_courant = residentiel["kwh_par_abonne"].corr(residentiel["heures_courant"])
        corr_temperature = residentiel["kwh_par_abonne"].corr(residentiel["temperature_c"])
        st.write(
            f"Corrélation avec les heures de courant : {corr_courant:.2f}; "
            f"avec la température : {corr_temperature:.2f}."
        )

    with onglets[3]:
        medianes = analyses.groupby("commune")["heures_courant"].median().sort_values()
        st.bar_chart(medianes, alt="Médiane des heures de courant par commune")

        coupures = analyses[
            (analyses["annee"] == 2025)
            & (analyses["heures_courant"] < 8)
        ]
        st.write(
            f"En 2025, {len(coupures)} relevés sont sous 8 heures de courant par jour : "
            f"{', '.join(coupures['quartier']) or 'aucun'}."
        )

    with onglets[4]:
        top3 = analyses.nlargest(3, "kwh").copy()
        top3["releve"] = top3["quartier"] + " - " + top3["mois"]
        st.bar_chart(
            top3.set_index("releve")["kwh"],
            alt="Les trois relevés ayant la plus forte consommation",
        )
        premier = top3.iloc[0]
        st.write(
            f"Le maximum est de {premier['kwh']:.0f} kWh, "
            f"à {premier['quartier']} en {premier['mois']}."
        )

    st.markdown(
        "Dans les quartiers résidentiels, la consommation par abonné est plus "
        "fortement associée aux heures de courant (corrélation de 0,76) qu’à la "
        "température (-0,15). Ces données suggèrent que la consommation suit "
        "davantage la disponibilité du courant que la chaleur. Toutefois, une "
        "corrélation ne prouve pas un lien de cause à effet, et d’autres facteurs "
        "peuvent intervenir."
    )

    with st.expander("Afficher les données filtrées"):
        st.dataframe(filtre, hide_index=True)