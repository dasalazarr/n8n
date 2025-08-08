#!/usr/bin/env python3
"""
Análisis de datos de accidentes laborales
"""

import pandas as pd
import os

def analyze_excel_data():
    """Analizar estructura del archivo Excel"""
    excel_path = 'docs/Registro de accidentes laborales EVP - Ago25 (SN).xlsx'
    
    if not os.path.exists(excel_path):
        print('❌ Excel file not found')
        return None
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        print('✅ Excel file loaded successfully')
        print(f'📊 Total records: {len(df)}')
        print(f'📋 Columns: {len(df.columns)}')
        print('\n🔍 Column names:')
        for i, col in enumerate(df.columns, 1):
            print(f'  {i}. {col}')
        
        print('\n📈 Data sample (first 2 rows):')
        print(df.head(2).to_string())
        
        print('\n📊 Data types:')
        print(df.dtypes)
        
        print('\n📈 Basic statistics:')
        print(df.describe())
        
        return df
        
    except Exception as e:
        print(f'❌ Error reading Excel: {e}')
        return None

if __name__ == "__main__":
    analyze_excel_data()
