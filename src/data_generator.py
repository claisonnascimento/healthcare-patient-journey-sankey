"""Gerador de sinistros sintéticos com lógica clínica.

Cada beneficiário percorre uma cadeia de Markov de eventos assistenciais. A chance de
descompensar (Pronto-Socorro / Internação) cresce com o risco da comorbidade, a faixa
etária e, principalmente, a baixa adesão ao acompanhamento eletivo — o mecanismo que o
dashboard pretende tornar visível.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.taxonomy import EVENTS, URGENCY_EVENTS

COMORBIDITIES = ["Hipertensão", "Diabetes", "Obesidade", "Cardiopatia", "DPOC"]
COMORBIDITY_WEIGHTS = [0.32, 0.24, 0.18, 0.14, 0.12]
# Risco relativo de descompensação aguda por condição
COMORBIDITY_RISK = {
    "Hipertensão": 1.0,
    "Diabetes": 1.15,
    "Obesidade": 0.9,
    "Cardiopatia": 1.6,
    "DPOC": 1.5,
}

AGE_BANDS = ["18-39", "40-59", "60+"]
AGE_WEIGHTS = [0.25, 0.45, 0.30]
AGE_RISK = {"18-39": 0.7, "40-59": 1.0, "60+": 1.4}

ADHERENCE_RATE = 0.62
# Multiplicador sobre as transições para urgência: aderentes descompensam bem menos
ADHERENCE_URGENCY_FACTOR = {True: 0.5, False: 2.4}
# Probabilidade de abandonar o acompanhamento após cada evento
DROPOUT_PROB = {True: 0.06, False: 0.28}
# Intervalo (dias) até o próximo contato
FOLLOW_UP_GAP_DAYS = {True: (10, 30), False: (20, 55)}

# Porta de entrada no período (ordem de EVENTS)
ENTRY_PROBS = np.array([0.46, 0.24, 0.12, 0.03, 0.12, 0.03])

# Matriz de transição base (linha = evento atual, colunas na ordem de EVENTS)
BASE_TRANSITIONS = {
    "Consulta_APS":          [0.15, 0.28, 0.37, 0.10, 0.07, 0.03],
    "Consulta_Especialista": [0.25, 0.15, 0.20, 0.30, 0.07, 0.03],
    "Exame_Rotina":          [0.50, 0.30, 0.05, 0.05, 0.07, 0.03],
    "Exame_Complexo":        [0.20, 0.60, 0.05, 0.05, 0.07, 0.03],
    "Pronto_Socorro":        [0.25, 0.25, 0.08, 0.10, 0.12, 0.20],
    "Internacao":            [0.30, 0.45, 0.05, 0.10, 0.07, 0.03],
}

# Custo por evento (R$): mediana e dispersão de uma log-normal
EVENT_COST = {
    "Consulta_APS": (110, 0.25),
    "Consulta_Especialista": (240, 0.30),
    "Exame_Rotina": (85, 0.40),
    "Exame_Complexo": (850, 0.45),
    "Pronto_Socorro": (620, 0.40),
    "Internacao": (9_500, 0.55),
}

HORIZON_DAYS = 90
MAX_EVENTS = 8
_URGENCY_IDX = [EVENTS.index(e) for e in URGENCY_EVENTS]


def _adjust_for_risk(probs: np.ndarray, risk: float) -> np.ndarray:
    """Escala as probabilidades de urgência pelo risco do paciente e renormaliza."""
    adjusted = np.asarray(probs, dtype=float).copy()
    adjusted[_URGENCY_IDX] *= risk
    return adjusted / adjusted.sum()


def _event_cost(rng: np.random.Generator, event: str) -> float:
    median, sigma = EVENT_COST[event]
    return round(float(median * rng.lognormal(0.0, sigma)), 2)


def generate_synthetic_claims(n_patients: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Gera registros sintéticos de utilização (claims) para beneficiários crônicos.

    Retorna um DataFrame com uma linha por atendimento:
    id_beneficiario, comorbidade, faixa_etaria, data_atendimento, tipo_evento, custo_evento.
    """
    rng = np.random.default_rng(seed)
    records = []

    for i in range(n_patients):
        pid = f"BEN_{10_000 + i}"
        comorbidity = rng.choice(COMORBIDITIES, p=COMORBIDITY_WEIGHTS)
        age_band = rng.choice(AGE_BANDS, p=AGE_WEIGHTS)
        adherent = bool(rng.random() < ADHERENCE_RATE)
        risk = (
            COMORBIDITY_RISK[comorbidity]
            * AGE_RISK[age_band]
            * ADHERENCE_URGENCY_FACTOR[adherent]
        )

        index_date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(rng.integers(0, 90)))
        event = rng.choice(EVENTS, p=_adjust_for_risk(ENTRY_PROBS, risk))
        day = 0

        for _ in range(MAX_EVENTS):
            records.append({
                "id_beneficiario": pid,
                "comorbidade": comorbidity,
                "faixa_etaria": age_band,
                "data_atendimento": index_date + pd.Timedelta(days=day),
                "tipo_evento": event,
                "custo_evento": _event_cost(rng, event),
            })

            # Após urgência o paciente sempre volta a ser visto; senão pode abandonar
            if event not in URGENCY_EVENTS and rng.random() < DROPOUT_PROB[adherent]:
                break

            low, high = FOLLOW_UP_GAP_DAYS[adherent]
            day += int(rng.integers(low, high + 1))
            if day > HORIZON_DAYS:
                break
            event = rng.choice(EVENTS, p=_adjust_for_risk(BASE_TRANSITIONS[event], risk))

    df = pd.DataFrame(records)
    return df.sort_values(["id_beneficiario", "data_atendimento"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o dataset sintético de claims.")
    parser.add_argument("--n-patients", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/raw/synthetic_claims.csv"))
    args = parser.parse_args()

    df = generate_synthetic_claims(args.n_patients, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"{len(df):,} registros de {df['id_beneficiario'].nunique():,} beneficiários -> {args.output}")


if __name__ == "__main__":
    main()
