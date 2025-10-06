import sys
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import seaborn as sns

file_path = r"C:\Users\maxen\Downloads\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horairefiltré.csv"

######################################################################################################


def tracer_production_mensuelle_par_filiere(file_path):
    # Charger le fichier CSV
    df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")

    # Convertir la colonne Date en datetime avec utc=True pour éviter le warning
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)

    # Supprimer les lignes avec des dates non valides
    df = df.dropna(subset=["Date"])

    # Extraire année et mois
    df["Mois"] = df["Date"].dt.to_period("M")

    # Afficher les colonnes pour vérifier ce qui est présent
    colonnes_disponibles = df.columns.str.strip()

    # Liste des colonnes de production attendues
    colonnes_production = [
        "Thermique (MW)",
        "Bagasse/charbon (MW)",
        "Hydraulique (MW)",
        "Solaire photovoltaïque (MW)",
        "Eolien (MW)",
        "Bioénergies (MW)"
    ]

    # Filtrer les colonnes qui existent réellement dans le fichier
    colonnes_production_presentes = [col for col in colonnes_production if col in colonnes_disponibles.tolist()]

    # Regrouper par mois et sommer les puissances (MW.h cumulés)
    df_mensuel = df.groupby("Mois")[colonnes_production_presentes].sum()

    # Tracer les courbes
    plt.figure(figsize=(12, 6))
    for col in colonnes_production_presentes:
        plt.plot(df_mensuel.index.to_timestamp(), df_mensuel[col], marker="o", label=col)

    # Mise en forme du graphique
    plt.title("Évolution mensuelle de la production électrique par filière à La Réunion")
    plt.xlabel("Mois")
    plt.ylabel("Production mensuelle cumulée (MW.h)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

    # Prévisions avec Prophet pour chaque filière disponible
    for filiere in colonnes_production_presentes:
        df_prophet = df_mensuel[[filiere]].reset_index()
        df_prophet.columns = ["ds", "y"]
        df_prophet["ds"] = df_prophet["ds"].dt.to_timestamp()

        model = Prophet()
        model.fit(df_prophet)

        future = model.make_future_dataframe(periods=24, freq="M")
        forecast = model.predict(future)

        # Tracer la prévision mensuelle
        plt.figure(figsize=(10, 6))
        plt.plot(df_prophet["ds"], df_prophet["y"], marker="o", label="Historique")
        plt.plot(forecast["ds"], forecast["yhat"], linestyle="--", label="Prévision")
        plt.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], alpha=0.2)
        plt.title(f"Prévision mensuelle de la production pour {filiere}")
        plt.xlabel("Mois")
        plt.ylabel("Production prévue (MW.h)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

        # Tendance annuelle (pas de modèle Prophet ici, simple moyenne)
        df_annee = df_prophet.copy()
        df_annee["Année"] = df_annee["ds"].dt.year
        tendance_annuelle = df_annee.groupby("Année")["y"].mean()

        plt.figure(figsize=(10, 5))
        plt.plot(tendance_annuelle.index, tendance_annuelle.values, marker='o', linestyle='-', label='Tendance annuelle')
        plt.title(f"Tendance annuelle moyenne de la production pour {filiere}")
        plt.xlabel("Année")
        plt.ylabel("Production moyenne (MW.h)")
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Variation moyenne par mois (simple agrégation)
        df_prophet["Mois"] = df_prophet["ds"].dt.month
        variation_mensuelle = df_prophet.groupby("Mois")["y"].mean()

        plt.figure(figsize=(10, 5))
        plt.plot(variation_mensuelle.index, variation_mensuelle.values, marker='s', linestyle='--', label='Moyenne par mois')
        plt.title(f"Variation moyenne mensuelle de la production pour {filiere}")
        plt.xlabel("Mois")
        plt.ylabel("Production moyenne (MW.h)")
        plt.grid()
        plt.legend()
        plt.tight_layout()
        plt.show()



def heatmap_production_par_heure_et_mois(file_path, filiere):
    df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
    df = df.dropna(subset=["Date"])

    if filiere not in df.columns:
        print(f"Filière {filiere} non trouvée dans le fichier.")
        return

    df["Heure"] = df["Date"].dt.hour
    df["Mois"] = df["Date"].dt.month
    heatmap_data = df.groupby(["Mois", "Heure"])[filiere].mean().unstack()

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap="YlOrRd", linewidths=0.5)
    plt.title(f"Carte de chaleur de la production horaire mensuelle – {filiere}")
    plt.xlabel("Heure de la journée")
    plt.ylabel("Mois")
    plt.tight_layout()
    plt.show()

# Afficher les graphiques
heatmap_production_par_heure_et_mois(file_path, "Eolien (MW)")
tracer_production_mensuelle_par_filiere(file_path)
#exploration à continuer , pour l'instant seulement 2 fonctions mettant en lien les données de production d'électricité avec les années et les types d'énergie