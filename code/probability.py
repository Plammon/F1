import pandas as pd
import joblib
import os
import numpy as np
from driver_team_circuit_constants import F1_2026_TRACKS
from prediction_context import apply_qualifying_context, latest_2026_driver_snapshot

def softmax(x, temperature=0.04):
    e_x = np.exp((x - np.max(x)) / temperature)
    return e_x / e_x.sum()

def get_probabilities(gp_name, rain_status=0):
    # Fonksiyon adını da 'get_probabilities' olarak güncelledik kral
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    model = joblib.load(os.path.join(project_root, 'models', 'f1_optuna_pi_model.pkl'))
    feature_names = joblib.load(os.path.join(project_root, 'models', 'f1_optuna_feature_names.pkl'))
    df = pd.read_csv(os.path.join(project_root, 'dataset', 'f1_final_features.csv'))

    if gp_name not in F1_2026_TRACKS:
        return None

    predict_df = latest_2026_driver_snapshot(df)
    predict_df = apply_qualifying_context(
        predict_df,
        df,
        track_name=gp_name,
        rain_status=rain_status,
    )

    X = pd.get_dummies(predict_df, columns=['GP', 'Track_Type', 'Track_DNA'])
    X = X.reindex(columns=feature_names, fill_value=0)
    
    scores = model.predict(X)
    probs = softmax(scores)
    predict_df['Probability'] = probs * 100

    return predict_df[['Driver', 'Team', 'Probability']].sort_values(by='Probability', ascending=False)
