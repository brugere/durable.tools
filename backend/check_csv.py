#!/usr/bin/env python3
import pandas as pd
import os

csv_files = [f for f in os.listdir('/code/data/raw') if f.endswith('.csv')]
print('Checking first few CSV files:')

for i, csv_file in enumerate(csv_files[:3]):
    print(f'File {i+1}: {csv_file}')
    try:
        df = pd.read_csv(f'/code/data/raw/{csv_file}', sep=';', encoding='latin-1', nrows=3)
        print('nom_modele:', df['nom_modele'].tolist())
        print('nom_metteur_sur_le_marche:', df['nom_metteur_sur_le_marche'].tolist())
        print('---')
    except Exception as e:
        print(f'Error reading {csv_file}: {e}')
        print('---')
