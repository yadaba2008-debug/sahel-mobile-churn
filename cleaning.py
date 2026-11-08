"""
cleaning.py - Nettoyage du dataset Sahel Mobile (Telco Churn).
Réutilisé par le notebook et par l'application Streamlit (app.py).

    from cleaning import load_clean_data
    df = load_clean_data("projet2_telco_churn.csv")
"""

import pandas as pd

# Tranches d'ancienneté (en mois), partagées par le notebook et l'app
TENURE_BINS = [-1, 6, 12, 24, 48, 72]
TENURE_LABELS = ["0-6 mois", "7-12 mois", "13-24 mois", "25-48 mois", "49-72 mois"]

COLS_INTERNET = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
                 "TechSupport", "StreamingTV", "StreamingMovies"]


def load_clean_data(filepath: str) -> pd.DataFrame:
    """Charge le CSV brut et applique les décisions de nettoyage.

    1. TotalCharges (texte -> float) : 11 chaînes vides (invisibles pour
       isnull()) = clients à tenure=0, pas encore facturés -> 0.0.
    2. SeniorCitizen (0/1 -> No/Yes) : cohérence avec les autres colonnes.
    3. "No internet service" / "No phone service" -> "No" : même sens que
       "No" pour l'analyse, évite une 3e modalité artificielle.
    4. Doublons : aucun (lignes et customerID) ; suppression par sécurité.
    5. Colonnes dérivées : Churn_num (0/1), tenure_bucket (tranches),
       Statut (libellé lisible pour les graphiques).
    """
    df = pd.read_csv(filepath)

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].str.strip(), errors="coerce").fillna(0.0)
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    df[COLS_INTERNET] = df[COLS_INTERNET].replace("No internet service", "No")
    df["MultipleLines"] = df["MultipleLines"].replace("No phone service", "No")
    df = df.drop_duplicates().reset_index(drop=True)

    df["Churn_num"] = (df["Churn"] == "Yes").astype(int)
    df["Statut"] = df["Churn"].map({"Yes": "Résilié", "No": "Fidèle"})
    df["tenure_bucket"] = pd.cut(df["tenure"], bins=TENURE_BINS, labels=TENURE_LABELS)
    return df


def risk_profile_mask(df: pd.DataFrame) -> pd.Series:
    """Profil à risque : mensuel + fibre + sans OnlineSecurity + sans TechSupport."""
    return (
        (df["Contract"] == "Month-to-month")
        & (df["InternetService"] == "Fiber optic")
        & (df["OnlineSecurity"] == "No")
        & (df["TechSupport"] == "No")
    )


if __name__ == "__main__":
    import sys
    d = load_clean_data(sys.argv[1] if len(sys.argv) > 1 else "projet2_telco_churn.csv")
    p = d[risk_profile_mask(d)]
    print(f"{d.shape} | manquants={d.isnull().sum().sum()} | churn={d['Churn_num'].mean():.1%}")
    print(f"Profil à risque : {len(p)} abonnés, dont {(p['Churn_num']==0).sum()} actifs")
