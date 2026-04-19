import pandas as pd
import xgboost as xgb
import optuna
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
import os
import joblib
import numpy as np

def objective(trial, X, y, weights):
    # Optuna'nın deneyeceği parametre aralıkları
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 500, 1500),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'objective': 'reg:squarederror',
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Zaman serisi mantığıyla Cross-Validation (Daha sağlam ölçüm)
    tscv = TimeSeriesSplit(n_splits=3)
    errors = []
    
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        w_train = weights[train_index]
        
        model = xgb.XGBRegressor(**param)
        model.fit(X_train, y_train, sample_weight=w_train)
        
        preds = model.predict(X_test)
        errors.append(mean_absolute_error(y_test, preds))
    
    return np.mean(errors)

def train_optimized_model(input_path):
    df = pd.read_csv(input_path)
    df = df.sort_values(['Year', 'GP']).reset_index(drop=True)
    
    # 1. HEDEF DEĞİŞİKLİĞİ (Strategy 3)
    # Artık Final_Pos yerine Performance_Index tahmin ediyoruz
    y = df['Performance_Index']
    
    # 2. ÖZELLİK SEÇİMİ
    feature_cols = [
        'Year', 'TrackTemp', 'Rain', 'Grid_Size',
        'Driver_Weighted_Form', 'Team_Weighted_Form', 
        'Teammate_Pos_Diff', 'Track_Weather_Specialty', 
        'Performance_Trend', 'GP', 'Track_Type'
    ]
    X = pd.get_dummies(df[feature_cols], columns=['GP', 'Track_Type'])
    
    # 2026 Önceliği
    weights = np.where(df['Year'] == 2026, 5.0, 1.0)

    # 3. OPTUNA İLE PARAMETRE OPTİMİZASYONU (Strategy 1)
    print("🧪 Optuna en iyi parametreleri arıyor (Bu biraz sürebilir)...")
    study = optuna.create_study(direction='minimize')
    study.optimize(lambda trial: objective(trial, X, y, weights), n_trials=50) # 50 farklı kombinasyon dene

    print(f"✅ En İyi MAE (Index bazında): {study.best_value:.4f}")
    
    # 4. EN İYİ MODELİ EĞİT
    best_model = xgb.XGBRegressor(**study.best_params)
    best_model.fit(X, y, sample_weight=weights)
    
    return best_model, X.columns

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'dataset', 'f1_final_features.csv')
    
    model, feature_names = train_optimized_model(data_path)
    
    # Kaydetme
    model_dir = os.path.join(project_root, 'models')
    if not os.path.exists(model_dir): os.makedirs(model_dir)
    joblib.dump(model, os.path.join(model_dir, 'f1_optuna_pi_model.pkl'))
    joblib.dump(feature_names, os.path.join(model_dir, 'f1_optuna_feature_names.pkl'))
    print("🚀 Optimize edilmiş model 'models/' klasörüne kaydedildi.")