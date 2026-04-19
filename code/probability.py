import pandas as pd
import joblib
import os
import numpy as np
from driver_team_circuit_constants import F1_2026_TRACKS

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

    active_drivers = df[df['Year'] == 2026]['Driver'].unique()
    predict_df = df[df['Driver'].isin(active_drivers)].sort_values(['Year', 'GP']).groupby('Driver').last().reset_index()

    predict_df['GP'] = gp_name
    predict_df['Rain'] = rain_status
    predict_df['Year'] = 2026
    predict_df['Track_Type'] = F1_2026_TRACKS[gp_name]['Type']
    predict_df['Track_DNA'] = F1_2026_TRACKS[gp_name]['DNA']

    X = pd.get_dummies(predict_df, columns=['GP', 'Track_Type', 'Track_DNA'])
    X = X.reindex(columns=feature_names, fill_value=0)
    
    scores = model.predict(X)
    probs = softmax(scores)
    predict_df['Probability'] = probs * 100

    return predict_df[['Driver', 'Team', 'Probability']].sort_values(by='Probability', ascending=False)