#!/usr/bin/env python3
import pandas as pd
import os

csv_files = [f for f in os.listdir('/code/data/raw') if f.endswith('.csv')]
df = pd.read_csv(f'/code/data/raw/{csv_files[0]}', sep=';', encoding='latin-1', nrows=5)

print('Sample values from first few columns:')
for col in df.columns[:10]:
    print(f'{col}: {df[col].iloc[0]}')

print('\nColumns that might contain numeric values:')
numeric_cols = []
for col in df.columns:
    try:
        if any(str(val).replace('.', '').isdigit() for val in df[col].head() if pd.notna(val)):
            numeric_cols.append(col)
    except:
        pass
print(numeric_cols[:10])
