import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Spécifiez le chemin complet du fichier CSV filtré
file_path = r"C:\Users\Maxen\Downloads\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horairefiltré.csv"

# Chargement du dataset en utilisant le séparateur ';' et un encodage approprié
try:
    df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
    print("Dataset loaded successfully using sep=';'.")
except FileNotFoundError:
    print("Error: The file was not found. Please check the file path.")
    sys.exit()
except Exception as e:
    print(f"An error occurred while reading the dataset: {e}")
    sys.exit()

# --- Préparation et nettoyage des données ---

# Liste des colonnes requises (cf. premier code)
required_columns = [
    "Date",
    "Production totale (MW)",
    "Thermique (MW)",
    "Bagasse/charbon (MW)",
    "Hydraulique (MW)",
    "Solaire photovoltaïque (MW)",
    "Eolien (MW)",
    "Bioénergies (MW)",
    "Coût moyen de production (€/MWh)"
]

# Si vos colonnes d'origine ne correspondent pas exactement aux noms ci-dessus,
# vous pouvez les renommer en construisant un dictionnaire de correspondance.
# Par exemple :
# rename_dict = {
#     "Année": "Date",
#     "Prod Totale": "Production totale (MW)",
#     "Thermique": "Thermique (MW)",
#      ...
# }
# df.rename(columns=rename_dict, inplace=True)
# Dans cet exemple, on supposera que le fichier contient déjà les bonnes colonnes.

# Afficher les colonnes existantes pour vérification
print("DataFrame columns:", df.columns.tolist())

# Vérifier que toutes les colonnes requises sont présentes
missing = [col for col in required_columns if col not in df.columns]
if missing:
    print(f"Error: The following required columns are missing from the DataFrame: {missing}")
    sys.exit()

# Ne conserver que les colonnes requises dans le bon ordre
df = df[required_columns]
print("DataFrame columns after filtering:", df.columns.tolist())

# Suppression des espaces superflus dans les noms de colonnes (si nécessaire)
df.columns = df.columns.str.strip()

# 1. Contrôle des valeurs manquantes par colonne
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nTotal missing values:", df.isnull().sum().sum())

# 2. Supprimer les lignes présentant des valeurs manquantes sur les colonnes requises
df = df.dropna(subset=required_columns)

# 3. Contrôle du nombre de lignes dupliquées
duplicates = df.duplicated().sum()
print(f"\nNumber of duplicate rows: {duplicates}")

#3.5 Supprimer les dates en double (si nécessaire) et invalidées
df = df.drop_duplicates(subset=["Date"])
print(f"\nNumber of duplicate rows after dropping duplicates: {df.duplicated().sum()}")

# 4. Suppression des colonnes entièrement vides (peu probable ici, vu que l'on ne conserve que celles
#    qui nous intéressent)
df = df.dropna(axis=1, how='all')
print(f"\nAfter dropping empty columns, columns present: {df.columns.tolist()}")

# 5. Visualiser les "boxplots" pour toutes les colonnes numériques afin d'identifier d'éventuels outliers
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
plt.figure(figsize=(15, 10))
for i, col in enumerate(numeric_columns):
    plt.subplot(3, 3, i + 1)
    sns.boxplot(x=df[col])
    plt.title(col)
plt.tight_layout()
boxplot_file = r"filepath.png"
plt.savefig(boxplot_file)
print(f"\nBoxplots saved as '{boxplot_file}'.")

# 6. Traitement des outliers par la méthode IQR pour toutes les colonnes numériques
df_cleaned = df.copy()
for col in numeric_columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
    if not outliers.empty:
        print(f"Found {len(outliers)} outliers in {col}.")
        # Limite des outliers aux bornes calculées
        df_cleaned[col] = np.where(df_cleaned[col] < lower_bound, lower_bound, df_cleaned[col])
        df_cleaned[col] = np.where(df_cleaned[col] > upper_bound, upper_bound, df_cleaned[col])

# 7. Enregistrement du dataset nettoyé dans un nouveau fichier CSV
output_file = r"C:\Users\Maxen\Downloads\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horaire-nettoyé.csv"
try:
    df_cleaned.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nCleaned data has been saved to '{output_file}'.")
except Exception as e:
    print(f"An error occurred while saving the file: {e}")