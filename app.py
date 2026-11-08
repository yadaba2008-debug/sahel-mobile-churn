"""
app.py - Tableau de bord Sahel Mobile : analyse de la résiliation (churn).
Lancement : streamlit run app.py
"""

from pathlib import Path

import plotly.express as px
import streamlit as st

from cleaning import TENURE_LABELS, load_clean_data, risk_profile_mask

st.set_page_config(page_title="Sahel Mobile - Résiliations", page_icon="📡", layout="wide")

# Libellés lisibles pour un public non technique
CONTRATS = {"Month-to-month": "Mensuel", "One year": "Annuel", "Two year": "Biannuel"}
INTERNET = {"Fiber optic": "Fibre optique", "DSL": "DSL", "No": "Pas d'internet"}
VARIABLES = {
    "Contract": "Type de contrat",
    "InternetService": "Service internet",
    "PaymentMethod": "Mode de paiement",
    "tenure_bucket": "Ancienneté",
    "SeniorCitizen": "Senior",
    "Partner": "En couple",
    "Dependents": "Personnes à charge",
    "OnlineSecurity": "Option sécurité en ligne",
    "TechSupport": "Support technique",
    "PaperlessBilling": "Facture électronique",
    "gender": "Genre",
}


@st.cache_data
def charger():
    ici = Path(__file__).parent
    for chemin in (ici / "projet2_telco_churn.csv", ici / "data" / "projet2_telco_churn.csv"):
        if chemin.exists():
            return load_clean_data(chemin)
    st.error("Fichier projet2_telco_churn.csv introuvable (à placer à côté de app.py ou dans data/).")
    st.stop()


df = charger()

# ---------------- Barre latérale : navigation + filtres ----------------
st.sidebar.title("📡 Sahel Mobile")
page = st.sidebar.radio("Navigation", ["Vue d'ensemble", "Analyse par variable", "Abonnés à risque"])

st.sidebar.header("Filtres")
contrats = st.sidebar.multiselect("Type de contrat", list(CONTRATS), default=list(CONTRATS),
                                  format_func=CONTRATS.get)
internet = st.sidebar.multiselect("Service internet", list(INTERNET), default=list(INTERNET),
                                  format_func=INTERNET.get)
tranches = st.sidebar.multiselect("Tranche d'ancienneté", TENURE_LABELS, default=TENURE_LABELS)

filtre = (df["Contract"].isin(contrats) & df["InternetService"].isin(internet)
          & df["tenure_bucket"].isin(tranches))
data = df[filtre]

if data.empty:
    st.warning("Aucun abonné ne correspond à ces filtres. Élargissez votre sélection.")
    st.stop()

# Abonnés à risque = clients ENCORE ACTIFS qui présentent le profil à risque
a_risque = data[risk_profile_mask(data) & (data["Churn"] == "No")]


# ---------------- Page 1 : vue d'ensemble ----------------
if page == "Vue d'ensemble":
    st.title("Vue d'ensemble des résiliations")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Abonnés (selon filtres)", f"{len(data):,}".replace(",", " "))
    c2.metric("Taux de résiliation", f"{data['Churn_num'].mean():.1%}")
    c3.metric("Abonnés à risque", f"{len(a_risque):,}".replace(",", " "),
              help="Clients encore actifs : contrat mensuel + fibre + sans sécurité en ligne + sans support technique.")
    c4.metric("Revenu mensuel menacé", f"{a_risque['MonthlyCharges'].sum():,.0f}".replace(",", " "),
              help="Somme des factures mensuelles des abonnés à risque.")

    g1, g2 = st.columns(2)
    par_contrat = data.groupby("Contract")["Churn_num"].mean().mul(100).rename(index=CONTRATS).reset_index()
    fig = px.bar(par_contrat, x="Contract", y="Churn_num", text_auto=".1f",
                 labels={"Contract": "Contrat", "Churn_num": "Taux de résiliation (%)"},
                 title="Résiliation par type de contrat")
    g1.plotly_chart(fig, width="stretch")

    par_tranche = (data.groupby("tenure_bucket", observed=True)["Churn_num"].mean().mul(100).reset_index())
    fig = px.bar(par_tranche, x="tenure_bucket", y="Churn_num", text_auto=".1f",
                 labels={"tenure_bucket": "Ancienneté", "Churn_num": "Taux de résiliation (%)"},
                 title="Résiliation par ancienneté")
    g2.plotly_chart(fig, width="stretch")

# ---------------- Page 2 : analyse par variable ----------------
elif page == "Analyse par variable":
    st.title("Analyse par variable")
    var = st.selectbox("Comparer le taux de résiliation selon :", list(VARIABLES),
                       format_func=VARIABLES.get)

    taux = data.groupby(var, observed=True)["Churn_num"].agg(["mean", "count"]).reset_index()
    taux["Taux (%)"] = taux["mean"] * 100
    fig = px.bar(taux, x=var, y="Taux (%)", text_auto=".1f", hover_data={"count": True},
                 labels={var: VARIABLES[var], "count": "Abonnés"},
                 title=f"Taux de résiliation par modalité : {VARIABLES[var]}")
    fig.add_hline(y=data["Churn_num"].mean() * 100, line_dash="dash",
                  annotation_text="Moyenne des abonnés filtrés")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Distribution de l'ancienneté : résiliés et fidèles")
    fig = px.histogram(data, x="tenure", color="Statut", barmode="overlay", opacity=0.6, nbins=36,
                       color_discrete_map={"Résilié": "#C44E52", "Fidèle": "#4C72B0"},
                       labels={"tenure": "Ancienneté (mois)", "count": "Abonnés"})
    st.plotly_chart(fig, width="stretch")

# ---------------- Page 3 : abonnés à risque ----------------
else:
    st.title("Abonnés à risque")
    st.caption("Clients encore actifs avec le profil à risque, triés par revenu mensuel décroissant.")
    st.metric("Revenu mensuel menacé", f"{a_risque['MonthlyCharges'].sum():,.0f}".replace(",", " "))
    colonnes =     colonnes = {"customerID": "Identifiant", "MonthlyCharges": "Facture mensuelle",
                "InternetService": "Internet", "PaymentMethod": "Paiement"}
    tableau = (a_risque.sort_values("MonthlyCharges", ascending=False)[list(colonnes)]
               .rename(columns=colonnes))
    st.dataframe(tableau, width="stretch", hide_index=True)
    st.download_button("Télécharger la liste (CSV)", tableau.to_csv(index=False).encode("utf-8"),
                       "abonnes_a_risque.csv", "text/csv")
