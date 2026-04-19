import pandas as pd
import numpy as np
import os

def generate_f1_features(input_path, output_path):
    df = pd.read_csv(input_path)
    
    # 1. Veriyi kronolojik sırala
    df = df.sort_values(by=['Year', 'GP', 'Driver']).reset_index(drop=True)

    # 2. EWMA (Üssel Ağırlıklı Ortalama) Fonksiyonu
    def calculate_weighted_form(series):
        return series.ewm(alpha=0.3, adjust=False).mean().shift(1)

    # 3. Sürücü ve Takım Formu
    df['Driver_Weighted_Form'] = df.groupby('Driver')['Performance_Index'].transform(calculate_weighted_form)
    df['Team_Weighted_Form'] = df.groupby('Team')['Performance_Index'].transform(calculate_weighted_form)
    
    # 4. TAKIM ARKADAŞI KIYASI (Hatasız ve Hızlı Yöntem)
    # apply() yerine transform() kullanarak o meşhur FutureWarning'den kurtuluyoruz
    def teammate_diff(x):
        if len(x) == 2:
            return x.iloc[::-1].values - x.values
        return np.zeros(len(x))

    df['Teammate_Pos_Diff'] = df.groupby(['Year', 'GP', 'Team'])['Final_Pos'].transform(teammate_diff)

    # 5. PİST + HAVA DURUMU SİNERJİSİ
    # 'Track_Type_Street' yerine orijinal 'Track_Type' sütununu kullanıyoruz
    df['Track_Weather_Specialty'] = df.groupby(['Driver', 'Track_Type', 'Rain'])['Performance_Index'].transform(
        lambda x: x.expanding().mean().shift(1)
    )

    # 6. TREND ANALİZİ (Son 5 Yarış)
    df['Performance_Trend'] = df.groupby('Driver')['Performance_Index'].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean().diff().shift(1)
    )

    # 7. Boşlukları Doldurma (Eksik verisi olan çaylaklar için)
    feature_cols = ['Driver_Weighted_Form', 'Team_Weighted_Form', 'Teammate_Pos_Diff', 
                    'Track_Weather_Specialty', 'Performance_Trend']
    
    for col in feature_cols:
        df[col] = df[col].fillna(0)

    # 8. ÇIKTI (Dataset klasörüne kaydet)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_path = os.path.join(project_root, 'dataset', 'f1_processed_readable.csv')
    output_path = os.path.join(project_root, 'dataset', 'f1_final_features.csv')

    try:
        final_df = generate_f1_features(input_path, output_path)
        print("\n" + "="*30)
        print("🚀 FEATURE ENGINEERING BAŞARIYLA TAMAMLANDI!")
        print(f"📂 Kaydedilen dosya: {output_path}")
        print(f"📊 Toplam Feature Sayısı: {len(final_df.columns)}")
        print("="*30)
    except Exception as e:
        print(f"❌ Hata: {e}")