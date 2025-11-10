"""
analytics_predictive.py

Análise preditiva da demanda horária de atendimentos de urgência.

Entrada:
- dados/demanda_horaria_urgencia_simulado.csv
    (gerado pelo script generate_simulated_data.py)

Saída:
- dados/demanda_horaria_urgencia_com_previsao.csv
    (mesmos campos + coluna qtd_prevista)

Uso:
    python codigo/analytics_predictive.py
"""

import os

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


INPUT_PATH = os.path.join("dados", "demanda_horaria_urgencia_simulado.csv")
OUTPUT_PATH = os.path.join("dados", "demanda_horaria_urgencia_com_previsao.csv")


def load_hourly_data(path: str) -> pd.DataFrame:
    """Carrega o dataset horário de demanda."""
    df = pd.read_csv(path, parse_dates=["data_hora"])
    return df


def train_model(df: pd.DataFrame):
    """
    Treina um modelo de Random Forest para prever qtd_pacientes
    a partir de hora_chegada, dia_semana e mes.
    """
    features = ["hora_chegada", "dia_semana", "mes"]
    target = "qtd_pacientes"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print("Desempenho do modelo:")
    print(f"  R²  = {r2:.3f}")
    print(f"  MAE = {mae:.3f} pacientes/hora")

    return model, r2, mae


def generate_predictions(df: pd.DataFrame, model: RandomForestRegressor) -> pd.DataFrame:
    """Gera a coluna qtd_prevista para todo o dataset horário."""
    features = ["hora_chegada", "dia_semana", "mes"]
    df = df.copy()
    df["qtd_prevista"] = model.predict(df[features])
    return df


def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado em {INPUT_PATH}. "
            "Certifique-se de rodar generate_simulated_data.py antes."
        )

    print(f"Lendo dados horários de {INPUT_PATH}...")
    df_hourly = load_hourly_data(INPUT_PATH)

    print("Treinando modelo preditivo (Random Forest)...")
    model, r2, mae = train_model(df_hourly)

    print("Gerando previsões para todas as linhas...")
    df_with_pred = generate_predictions(df_hourly, model)

    # Garante existência da pasta
    os.makedirs("dados", exist_ok=True)
    df_with_pred.to_csv(OUTPUT_PATH, index=False)

    print(f"Arquivo com previsões salvo em: {OUTPUT_PATH}")
    print("Pronto! Dataset com qtd_prevista disponível para uso no Power BI.")


if __name__ == "__main__":
    main()
