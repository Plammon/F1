Race dataset dosyalari bu klasore yazilir.

Pipeline sirasi:
1) `python rcode/collect_race_data.py`
2) `python rcode/merge_race_datas.py`
3) `python rcode/preprocessing_race.py`
4) `python rcode/feature_engineering_race.py`

Uretilen ana dosyalar:
- `*_race_data_final.csv` (yillik ham race verisi)
- `f1_master_race_dataset.csv`
- `f1_processed_race_readable.csv`
- `f1_final_race_features.csv`
