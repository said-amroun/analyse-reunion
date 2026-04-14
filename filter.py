import pandas as pd
import sys


file_path = r"C:\Users\maxen\Downloads\projetinfo\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horaire.csv"

try:
    df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
    print("Dataset loaded successfully using sep=';'.")
except FileNotFoundError:
    print("Error: The file was not found. Please check the file path.")
    sys.exit()
except Exception as e:
    print(f"An error occurred while reading the dataset: {e}")
    sys.exit()


print("Columns present in the dataset:")
print(df.columns.tolist())



supprimer_colonnes_vides = [col for col in df.columns if df[col].isnull().all()]
if supprimer_colonnes_vides:
    df.drop(columns=supprimer_colonnes_vides, inplace=True)
    print(f"Removed empty columns: {supprimer_colonnes_vides}")

if "Territoire" in df.columns:
    df = df[df["Territoire"] == "Réunion"]
    print("Filtrage effectué : seules les données pour le territoire 'Réunion' ont été conservées.")
else:
    print("Erreur : La colonne 'Territoire' est absente du dataset.")
    sys.exit()

required_columns = [
    "Date", 
    "Production totale (MW)",
    "Thermique (MW)",
    "Bagasse/charbon (MW)",
    "Hydraulique (MW)",
    "Solaire photovoltaïque (MW)",
    "Eolien (MW)",
    "Bioénergies (MW)",
    "Coût moyen de production (€/MWh)"]


missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"Error: The following required columns are missing in the dataset: {missing_columns}")
    sys.exit()


filtered_df = df[required_columns].copy()

output_file = r"C:\Users\Maxen\Downloads\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horairefiltré.csv"
try:
    filtered_df.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')
    print(f"Filtered data has been saved to '{output_file}'.")
except Exception as e:
    print(f"An error occurred while saving the file: {e}")

