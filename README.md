# Sahel Mobile : analyse de la résiliation (churn)

Projet 2 du BootCamp Data Analyst : comprendre **qui** résilie, **quand** et **pourquoi**,
et livrer un tableau de bord Streamlit pour les chefs de produit.

## Contenu du dépôt
| Fichier | Rôle |
|---|---|
| `Examen_Finale.ipynb` | Exploration, nettoyage commenté, réponses aux 4 questions |
| `cleaning.py` | Logique de nettoyage, réutilisée par le notebook et l'app |
| `app.py` | Application Streamlit (3 pages) |
| `projet2_telco_churn.csv` | Données brutes (7 043 abonnés, 21 colonnes) |

## Lancer l'application
```bash
pip install -r requirements.txt
streamlit run app.py
```
Lien de l'application déployée : [https://yadaba2008-debug-sahel-mobile-churn-app-stme8x.streamlit.app](https://yadaba2008-debug-sahel-mobile-churn-app-stme8x.streamlit.app/)
## Décisions de nettoyage
| Problème détecté | Décision | Justification |
|---|---|---|
| `TotalCharges` en texte | Conversion en nombre | Impossible de calculer sur du texte |
| 11 `TotalCharges` vides (invisibles pour `isnull()`) | Remplacés par 0 | Ce sont les 11 abonnés à `tenure = 0` : pas encore facturés, et aucun n'a résilié |
| `SeniorCitizen` en 0/1 | Converti en No/Yes | Cohérence avec les autres colonnes |
| "No internet service" / "No phone service" | Fusionnés avec "No" | Même sens pour l'analyse ; évite une 3e modalité artificielle |
| Doublons | Aucun trouvé (lignes et `customerID`) | Contrôle effectué |

## Principaux résultats
- **Taux de résiliation global : 26,5 %** (1 869 abonnés sur 7 043).
- **Contrat** : mensuel 42,7 %, annuel 11,3 %, biannuel 2,8 %. Écart de 39,9 points, soit 15 fois plus de résiliations en mensuel qu'en biannuel.
- **Ancienneté** : le risque est maximal sur les 6 premiers mois (52,9 %) et diminue ensuite jusqu'à 9,5 % après 49 mois.
- **Fibre optique** : 41,9 % de résiliation contre 19,0 % pour le DSL, et toujours plus à contrat égal. Hypothèse (non démontrée) : facture plus élevée (91,5 " en moyenne contre 58,1 " pour le DSL).
- **Profil à risque** (contrat mensuel + fibre + sans sécurité en ligne + sans support technique) : **1 524 abonnés, 21,6 % du parc**, avec 60,7 % de résiliation.
- **Revenu menacé** : 599 abonnés du profil sont encore actifs, soit **50 640 " de facturation mensuelle** à protéger en priorité.

## Définitions retenues
- *Abonné à risque* : client **encore actif** qui présente le profil à risque ci-dessus.
- *Revenu mensuel menacé* : somme des factures mensuelles des abonnés à risque.

## Limites
Les données sont observationnelles : elles montrent des associations, pas des causes.
