import pandas as pd
import glob
import os

def merge_f1_csvs(output_name='f1_master_dataset.csv'):
    # 1. Senin formatına uygun deseni belirliyoruz: *_quali_data_final.csv
    # Yıldız (*) işareti yıl kısmını (2022, 2023 vb.) temsil eder.
    file_pattern = '*_quali_data_final.csv'
    all_files = glob.glob(file_pattern)
    
    if not all_files:
        print(f"❌ '{file_pattern}' formatında dosya bulunamadı!")
        print("Lütfen script'i CSV'lerin olduğu klasörde çalıştırdığından emin ol.")
        return

    # Dosyaları isim sırasına göre dizelim (2022 önce gelsin)
    all_files.sort()
    print(f"📂 Birleştirilecek dosyalar: {all_files}")

    df_list = []
    for filename in all_files:
        print(f"📖 Okunuyor: {filename}")
        df = pd.read_csv(filename)
        df_list.append(df)
    
    # 2. Hepsini alt alta ekle
    merged_df = pd.concat(df_list, ignore_index=True)

    # 3. Sıralama (Yıl ve GP bazlı)
    if 'Year' in merged_df.columns:
        merged_df = merged_df.sort_values(by=['Year', 'GP']).reset_index(drop=True)

    # 4. Master dosyayı oluştur
    merged_df.to_csv(output_name, index=False)
    
    print("\n" + "="*30)
    print(f"✅ Master Dataset Hazır: {output_name}")
    print(f"📊 Toplam Satır Sayısı: {len(merged_df)}")
    print(f"📅 Kapsanan Yıllar: {merged_df['Year'].unique() if 'Year' in merged_df.columns else 'Bilinmiyor'}")
    print("="*30)

if __name__ == "__main__":
    merge_f1_csvs()