import pandas as pd
import joblib
import os
import numpy as np

def make_pi_prediction(gp_name, year=2026, rain=0):
    # 1. Dosya Yollarını Hazırla
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    model_path = os.path.join(project_root, 'models', 'f1_optuna_pi_model.pkl')
    features_path = os.path.join(project_root, 'models', 'f1_optuna_feature_names.pkl')
    data_path = os.path.join(project_root, 'dataset', 'f1_final_features.csv')

    # 2. Modeli ve Özellik İsimlerini Yükle
    try:
        model = joblib.load(model_path)
        feature_names = joblib.load(features_path)
    except FileNotFoundError:
        return "❌ Hata: Model dosyaları bulunamadı! Lütfen önce eğitimi tamamla."

    # 3. Veriyi Oku ve Filtrele
    df = pd.read_csv(data_path)
    
    # KRİTİK: Sadece 2026'da koltuğu olan gerçek pilotları al (33 pilot hatasını çözer)
    active_2026_drivers = df[df['Year'] == 2026]['Driver'].unique()
    
    # Sadece aktif pilotların veri setindeki en güncel form bilgilerini çek
    latest_stats = df[df['Driver'].isin(active_2026_drivers)].sort_values(['Year', 'GP']).groupby('Driver').last().reset_index()

    # 4. Tahmin Parametrelerini Güncelle
    latest_stats['GP'] = gp_name
    latest_stats['Year'] = year
    latest_stats['Rain'] = rain
    
    # Pist tipini ana veriden otomatik bulalım
    track_info = df[df['GP'] == gp_name]['Track_Type'].unique()
    if len(track_info) > 0:
        latest_stats['Track_Type'] = track_info[0]
    else:
        latest_stats['Track_Type'] = 'Permanent' # Varsayılan

    # 5. Encoding ve Kolon Hizalama (XGBoost Beklentisi)
    X_pred = pd.get_dummies(latest_stats, columns=['GP', 'Track_Type'])
    
    # DÜZELTME: fill_value=0 ile eksik kolonları tamamla
    X_pred = X_pred.reindex(columns=feature_names, fill_value=0)
    
    # 6. Tahmin Yap (Performance Index Skoru)
    latest_stats['AI_Score'] = model.predict(X_pred)
    
    # 7. Sonuçları Büyükten Küçüğe Sırala (1.0 En İyi Puan)
    results = latest_stats[['Driver', 'Team', 'AI_Score']].sort_values(by='AI_Score', ascending=False)
    results['Rank'] = range(1, len(results) + 1)
    
    return results

if __name__ == "__main__":
    # SİMÜLASYON AYARLARI
    # Bugün 19 Nisan 2026; sıradaki büyük yarış Imola olabilir!
    target_gp = "Emilia Romagna Grand Prix" 
    weather_condition = 0 # 0: Güneşli, 1: Yağmurlu
    
    print(f"🏎️  2026 {target_gp} Simülasyonu Başlatılıyor...")
    print(f"📅 Tarih: 19 Nisan 2026 | Durum: {'Yağmurlu' if weather_condition else 'Güneşli'}")
    
    prediction_table = make_pi_prediction(target_gp, rain=weather_condition)
    
    if isinstance(prediction_table, str):
        print(prediction_table)
    else:
        print("\n" + "="*60)
        print(f"{'Sıra':<6} {'Pilot':<22} {'Takım':<22} {'AI Skoru':<10}")
        print("-" * 60)
        for _, row in prediction_table.iterrows():
            print(f"{int(row['Rank']):<6} {row['Driver']:<22} {row['Team']:<22} {row['AI_Score']:<10.4f}")
        print("="*60)
        print("\n💡 Bilgi: Skoru 1.0000'e en yakın olan pilot podyumun zirvesindedir.")