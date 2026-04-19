import pandas as pd
import joblib
import os
import sys

# 1. Dosya yolunu garantiye alalım ve import edelim
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    # Dosya adını 'constants' olarak güncelledik kanka
    from driver_team_circuit_constants import F1_2026_TRACKS
except ModuleNotFoundError:
    print("\n❌ HATA: 'driver_team_circuit_constants.py' bulunamadı!")
    print("💡 Lütfen klasördeki dosya adını 'constants' (t harfiyle) olarak düzelt.")
    sys.exit(1)

def get_f1_prediction(gp_name, rain_status=0):
    """
    GP adı ve yağmur durumuna göre 2026 performans sıralamasını döner.
    """
    project_root = os.path.dirname(current_dir)
    model_file = os.path.join(project_root, 'models', 'f1_optuna_pi_model.pkl')
    features_file = os.path.join(project_root, 'models', 'f1_optuna_feature_names.pkl')
    data_file = os.path.join(project_root, 'dataset', 'f1_final_features.csv')

    # 2. Sözlük Kontrolü (Pist veri setinde var mı?)
    if gp_name not in F1_2026_TRACKS:
        print(f"\n⚠️  HATA: '{gp_name}' geçerli bir pist değil.")
        print(f"📍 Mevcutlar: {list(F1_2026_TRACKS.keys())[:5]}...")
        return None

    # Sözlükten DNA ve Tip bilgilerini çekiyoruz
    track_type = F1_2026_TRACKS[gp_name]['Type']
    track_dna = F1_2026_TRACKS[gp_name]['DNA']

    # 3. Model ve Veriyi Yükle
    model = joblib.load(model_file)
    feature_names = joblib.load(features_file)
    df = pd.read_csv(data_file)

    # 4. Sadece 2026 Aktif Pilotlarını Al
    active_drivers = df[df['Year'] == 2026]['Driver'].unique()
    predict_df = df[df['Driver'].isin(active_drivers)].sort_values(['Year', 'GP']).groupby('Driver').last().reset_index()

    # 5. Girdi Verilerini Yarışa Göre Ayarla
    predict_df['GP'] = gp_name
    predict_df['Rain'] = rain_status
    predict_df['Year'] = 2026
    predict_df['Track_Type'] = track_type
    predict_df['Track_DNA'] = track_dna

    # 6. Encoding ve Hizalama (En kritik kısım burası)
    X = pd.get_dummies(predict_df, columns=['GP', 'Track_Type', 'Track_DNA'])
    X = X.reindex(columns=feature_names, fill_value=0)

    # 7. Tahmin ve Sıralama
    predict_df['AI_Score'] = model.predict(X)
    final_list = predict_df[['Driver', 'Team', 'AI_Score']].sort_values(by='AI_Score', ascending=False)
    final_list['Rank'] = range(1, len(final_list) + 1)

    return final_list

if __name__ == "__main__":
    print("\n🏁 F1 2026 Tahmin Motoru")
    print("-" * 30)
    
    yaris = input("Grand Prix adını gir (constants dosyasındaki gibi): ")
    try:
        hava = int(input("Yağmur Durumu (0: Güneşli, 1: Yağmurlu): "))
        
        sonuc = get_f1_prediction(yaris, rain_status=hava)
        
        if sonuc is not None:
            print(f"\n📊 {yaris} ({'Yağmurlu' if hava else 'Güneşli'}) AI Tahmini:")
            print("=" * 65)
            print(sonuc[['Rank', 'Driver', 'Team', 'AI_Score']].to_string(index=False))
            print("=" * 65)
    except ValueError:
        print("❌ Hata: Yağmur durumu için sadece 0 veya 1 girmelisin kanka.")