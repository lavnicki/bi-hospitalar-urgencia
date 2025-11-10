"""
generate_simulated_data.py

Gera datasets simulados de atendimentos de urgência hospitalar:
- dados/atendimentos_urgencia_simulado.csv
- dados/demanda_horaria_urgencia_simulado.csv
"""

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_atendimentos(start, end, seed=42):
    np.random.seed(seed)

    specialties = ["Clínica Geral", "Ortopedia", "Pediatria", "Cardiologia"]
    triage_levels = ["Azul", "Verde", "Amarelo", "Laranja", "Vermelho"]
    sexes = ["M", "F"]
    outcomes = ["Alta", "Internação", "Óbito", "Evasão"]

    records = []
    id_atendimento = 1

    hours = int(((end - start).total_seconds() // 3600) + 1)
    current_time = start

    for _ in range(hours):
        # Pacientes por hora (varia conforme horário)
        if current_time.hour in range(2, 6):
            base = 2          # madrugada
        elif current_time.hour in range(18, 23):
            base = 10         # pico noturno
        else:
            base = 6          # horário normal

        n_patients = np.random.poisson(base)

        for _ in range(n_patients):
            arrival_offset = np.random.randint(0, 60)
            arrival_time = current_time + timedelta(minutes=int(arrival_offset))

            specialty = np.random.choice(specialties)
            triage = np.random.choice(triage_levels, p=[0.1, 0.4, 0.3, 0.15, 0.05])

            age = int(np.random.normal(45, 18))
            age = max(0, min(age, 100))  # faixa 0–100 anos

            sex = np.random.choice(sexes)

            # Tempo de espera de acordo com triagem
            base_wait = {
                "Vermelho": np.random.randint(0, 5),
                "Laranja": np.random.randint(5, 15),
                "Amarelo": np.random.randint(15, 40),
                "Verde": np.random.randint(30, 90),
                "Azul": np.random.randint(60, 180),
            }[triage]

            wait_time = base_wait + max(
                0, int(np.random.normal(loc=n_patients, scale=5))
            )

            atendimento_time = arrival_time + timedelta(minutes=wait_time)
            atendimento_duration = np.random.randint(10, 60)
            finish_time = atendimento_time + timedelta(minutes=atendimento_duration)

            outcome = np.random.choice(outcomes, p=[0.75, 0.2, 0.02, 0.03])
            bed_id = np.random.randint(1, 80) if outcome in ["Internação", "Óbito"] else None
            doctor_id = np.random.randint(1, 40)

            records.append(
                {
                    "id_atendimento": id_atendimento,
                    "data_hora_chegada": arrival_time,
                    "data_hora_atendimento": atendimento_time,
                    "data_hora_saida": finish_time,
                    "especialidade": specialty,
                    "nivel_triagem": triage,
                    "idade": age,
                    "sexo": sex,
                    "tempo_espera_min": wait_time,
                    "tempo_atendimento_min": atendimento_duration,
                    "desfecho": outcome,
                    "id_leito": bed_id,
                    "id_medico": doctor_id,
                }
            )

            id_atendimento += 1

        current_time += timedelta(hours=1)

    df = pd.DataFrame(records)
    return df


def add_date_features(df):
    """Adiciona colunas derivadas de data/hora."""
    df["data_hora_chegada"] = pd.to_datetime(df["data_hora_chegada"])
    df["data_hora_atendimento"] = pd.to_datetime(df["data_hora_atendimento"])
    df["data_hora_saida"] = pd.to_datetime(df["data_hora_saida"])

    df["data"] = df["data_hora_chegada"].dt.date
    df["hora_chegada"] = df["data_hora_chegada"].dt.hour
    df["dia_semana"] = df["data_hora_chegada"].dt.dayofweek  # 0=segunda, 6=domingo
    df["mes"] = df["data_hora_chegada"].dt.month
    return df


def aggregate_hourly(df):
    """Agrupa atendimentos por data e hora para demanda horária."""
    df_hourly = (
        df.groupby(["data", "hora_chegada"])
        .agg(
            qtd_pacientes=("id_atendimento", "count"),
            tempo_medio_espera=("tempo_espera_min", "mean"),
        )
        .reset_index()
    )

    df_hourly["data_hora"] = pd.to_datetime(df_hourly["data"].astype(str)) + pd.to_timedelta(
        df_hourly["hora_chegada"], unit="h"
    )
    df_hourly["dia_semana"] = df_hourly["data_hora"].dt.dayofweek
    df_hourly["mes"] = df_hourly["data_hora"].dt.month
    return df_hourly


def main():
    # Período da simulação (3 meses)
    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 3, 31, 23, 0)

    print("Gerando atendimentos simulados...")
    df = generate_atendimentos(start, end)
    df = add_date_features(df)

    print("Gerando agregação horária...")
    df_hourly = aggregate_hourly(df)

    # Garantir que a pasta 'dados' exista
    os.makedirs("dados", exist_ok=True)

    # Salvar arquivos
    path_atend = os.path.join("dados", "atendimentos_urgencia_simulado.csv")
    path_hourly = os.path.join("dados", "demanda_horaria_urgencia_simulado.csv")

    df.to_csv(path_atend, index=False)
    df_hourly.to_csv(path_hourly, index=False)

    print(f"Arquivo salvo: {path_atend}")
    print(f"Arquivo salvo: {path_hourly}")


if __name__ == "__main__":
    main()
