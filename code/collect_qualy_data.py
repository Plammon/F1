import fastf1
import pandas as pd
from tqdm import tqdm
import time
import os

# 1. Pist DNA Sözlüğü (Senin için genişlettim, eksikleri buradan tamamlayabilirsin)
F1_2026_TRACK_DNA = {
    "Sakhir": {"Type": "Permanent", "DNA": "Traction & Braking"},
    "Jeddah": {"Type": "Street", "DNA": "Ultra-High-Speed"},
    "Melbourne": {"Type": "Street/Hybrid", "DNA": "Medium-Speed"},
    "Suzuka": {"Type": "Permanent", "DNA": "High-Speed-Flowing"},
    "Monaco": {"Type": "Street", "DNA": "Low-Speed / Max-Downforce"},
    "Silverstone": {"Type": "Permanent", "DNA": "Ultra-High-Speed"},
    "Monza": {"Type": "Permanent", "DNA": "Top-Speed / Low-Drag"},
    "Singapore": {"Type": "Street", "DNA": "Traction / Technical"},
    "Baku": {"Type": "Street", "DNA": "Top-Speed / 90-Degree-Turns"},
    "Spa": {"Type": "Permanent", "DNA": "Power-Unit / Long-Straights"}
}

def normalize_names(team, year):
    mapping = {
        "AlphaTauri": "Racing Bulls", "RB": "Racing Bulls", "VCARB": "Racing Bulls",
        "Sauber": "Audi (Sauber)", "Alfa Romeo": "Audi (Sauber)",
        "Aston Martin Aramco": "Aston Martin", "Haas F1 Team": "Haas"
    }
    return mapping.get(team, team)

if not os.path.exists('.f1_cache'):
    os.makedirs('.f1_cache')


fastf1.Cache.enable_cache('.f1_cache')

def collect_f1_data(start_year=2026, end_year=2026):
    all_data = []
    
    for year in range(start_year, end_year + 1):
        print(f"\n--- {year} Sezonu Kayıtları Alınıyor ---")
        try:
            schedule = fastf1.get_event_schedule(year)
            events = schedule[schedule['EventFormat'] != 'testing']
        except: continue

        for _, event in tqdm(events.iterrows(), total=len(events)):
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'Q')
                session.load(laps=False, telemetry=False, weather=True)
                
                # Rank Hesaplama
                results = session.results.copy()
                results['Q1_Rank'] = results['Q1'].rank(method='min')
                results['Q2_Rank'] = results['Q2'].rank(method='min')
                
                # Pist Bilgisi Çekme (Location üzerinden)
                loc = event['Location']
                dna = F1_2026_TRACK_DNA.get(loc, {"Type": "Permanent", "DNA": "Standard"})
                
                # Hava durumu
                weather = session.weather_data
                avg_temp = weather['TrackTemp'].mean()
                rain = 1 if weather['Rainfall'].any() else 0
                
                for _, driver in results.iterrows():
                    all_data.append({
                        'Year': year,
                        'GP': event['EventName'],
                        # İŞTE BURADALAR:
                        'Track_Type': dna['Type'],
                        'Track_DNA': dna['DNA'],
                        'Driver': driver['FullName'],
                        'Team': normalize_names(driver['TeamName'], year),
                        'Q1_Time': driver['Q1'].total_seconds() if pd.notnull(driver['Q1']) else None,
                        'Q2_Time': driver['Q2'].total_seconds() if pd.notnull(driver['Q2']) else None,
                        'Q3_Time': driver['Q3'].total_seconds() if pd.notnull(driver['Q3']) else None,
                        'Q1_Pos': int(driver['Q1_Rank']) if pd.notnull(driver['Q1_Rank']) else None,
                        'Q2_Pos': int(driver['Q2_Rank']) if pd.notnull(driver['Q2_Rank']) else None,
                        'Final_Pos': int(driver['Position']),
                        'TrackTemp': avg_temp,
                        'Rain': rain
                    })
                time.sleep(0.3) # API'yi yormayalım
            except: continue

    return pd.DataFrame(all_data)

if __name__ == "__main__":
    df = collect_f1_data()
    df.to_csv('2026_quali_data_final.csv', index=False)
    print("\n✅ Veri seti hazır! DNA ve Pozisyonlar eklendi.")