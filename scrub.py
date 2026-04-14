import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


file_path = r"C:\Users\Maxen\Downloads\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horairefiltré.csv"


try:
    df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
    print("Dataset loaded successfully using sep=';'.")
except FileNotFoundError:
    print("Error: The file was not found. Please check the file path.")
    sys.exit()
except Exception as e:
    print(f"An error occurred while reading the dataset: {e}")
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
    "Coût moyen de production (€/MWh)"
]


print("DataFrame columns:", df.columns.tolist())


missing = [col for col in required_columns if col not in df.columns]
if missing:
    print(f"Error: The following required columns are missing from the DataFrame: {missing}")
    sys.exit()


df = df[required_columns]
print("DataFrame columns after filtering:", df.columns.tolist())


df.columns = df.columns.str.strip()


print("\nMissing values per column:")
print(df.isnull().sum())
print("\nTotal missing values:", df.isnull().sum().sum())


df = df.dropna(subset=required_columns)


duplicates = df.duplicated().sum()
print(f"\nNumber of duplicate rows: {duplicates}")


df = df.drop_duplicates(subset=["Date"])
print(f"\nNumber of duplicate rows after dropping duplicates: {df.duplicated().sum()}")

df = df.dropna(axis=1, how='all')
print(f"\nAfter dropping empty columns, columns present: {df.columns.tolist()}")


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

output_file = r"C:\Users\Maxen\Downloads\production-d-electricite-par-filiere-et-couts-de-production-au-pas-horaire-nettoyé.csv"
try:
    df_cleaned.to_csv(output_file, index=False, sep=';', encoding='utf-8-sig')
    print(f"\nCleaned data has been saved to '{output_file}'.")
except Exception as e:
    print(f"An error occurred while saving the file: {e}")
