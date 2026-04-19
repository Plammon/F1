import pandas as pd
import numpy as np
import os

def f1_readable_preprocessing(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    
    # 1. Grid Boyutu
    df['Grid_Size'] = df.groupby(['Year', 'GP'])['Driver'].transform('count')

    # 2. Senaryo A & B (Hiyerarşik Doldurma)
    # Pozisyonları olduğu gibi koruyoruz, elenenleri elendiği yere sabitliyoruz
    df['Q2_Pos'] = df['Q2_Pos'].fillna(df['Q1_Pos'])
    df['Final_Pos'] = df['Final_Pos'].fillna(df['Q2_Pos'])

    # 3. Delta Saniye (Zaman Farkı)
    for session in ['Q1_Time', 'Q2_Time', 'Q3_Time']:
        best_time = df.groupby(['Year', 'GP'])[session].transform('min')
        df[f'{session}_Delta'] = df[session] - best_time
        # Elenenlere ceza: Grid_Size * 2 saniye
        df[f'{session}_Delta'] = df[f'{session}_Delta'].fillna(df['Grid_Size'] * 2)

    # 4. Performance Index
    df['Performance_Index'] = (df['Grid_Size'] - df['Final_Pos']) / df['Grid_Size']

    # 5. GEREKSİZLERİ ATMA (İsimleri KORUYORUZ)
    # Sadece ham zamanları (Time) atıyoruz, çünkü Delta'lar artık iş görüyor.
    cols_to_drop = ['Q1_Time', 'Q2_Time', 'Q3_Time']
    final_df = df.drop(columns=cols_to_drop)

    final_df.to_csv(output_csv, index=False)
    return final_df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_path = os.path.join(project_root, 'dataset', 'f1_master_dataset.csv')
    output_path = os.path.join(project_root, 'dataset', 'f1_processed_readable.csv')

    try:
        processed_data = f1_readable_preprocessing(input_path, output_path)
        print("✅ Preprocessing Tamam! İsimler korundu, veriler temizlendi.")
        print(f"📊 Örnek Satır:\n{processed_data[['Driver', 'Team', 'Final_Pos', 'Performance_Index']].head(1)}")
    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")