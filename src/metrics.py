"""Indicadores de linha de cuidado calculados sobre a tabela de jornadas."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.taxonomy import NO_CARE, URGENCY_EVENTS

OUTCOME_RETAINED = "Retido no cuidado"
OUTCOME_URGENCY = "Urgência / internação"
OUTCOME_LOST = "Sem atendimento"
OUTCOME_ORDER = [OUTCOME_RETAINED, OUTCOME_URGENCY, OUTCOME_LOST]


@dataclass(frozen=True)
class JourneyKPIs:
    beneficiarios: int
    taxa_urgencia: float
    taxa_abandono: float
    taxa_retencao: float
    fuga_aps_urgencia: float
    custo_medio: float
    custo_medio_com_urgencia: float
    custo_medio_sem_urgencia: float


def classify_outcome(event: str) -> str:
    """Agrupa o evento da última onda em um desfecho de negócio."""
    if event == NO_CARE:
        return OUTCOME_LOST
    if event in URGENCY_EVENTS:
        return OUTCOME_URGENCY
    return OUTCOME_RETAINED


def _rate(mask: pd.Series) -> float:
    return float(mask.mean()) if len(mask) else 0.0


def _mean(values: pd.Series) -> float:
    return float(values.mean()) if len(values) else 0.0


def compute_kpis(journey_df: pd.DataFrame, final_wave: str = "Onda_3") -> JourneyKPIs:
    urgency = journey_df["urgencia_no_seguimento"]
    outcome = journey_df[final_wave].map(classify_outcome)
    entered_aps = journey_df["Onda_1"] == "Consulta_APS"

    return JourneyKPIs(
        beneficiarios=len(journey_df),
        taxa_urgencia=_rate(urgency),
        taxa_abandono=_rate(outcome == OUTCOME_LOST),
        taxa_retencao=_rate(outcome == OUTCOME_RETAINED),
        fuga_aps_urgencia=_rate(urgency[entered_aps]),
        custo_medio=_mean(journey_df["custo_total"]),
        custo_medio_com_urgencia=_mean(journey_df.loc[urgency, "custo_total"]),
        custo_medio_sem_urgencia=_mean(journey_df.loc[~urgency, "custo_total"]),
    )


def outcome_by_comorbidity(journey_df: pd.DataFrame, final_wave: str = "Onda_3") -> pd.DataFrame:
    """Distribuição percentual dos desfechos da última onda por comorbidade."""
    outcome = journey_df[final_wave].map(classify_outcome)
    table = pd.crosstab(journey_df["comorbidade"], outcome, normalize="index")
    return table.reindex(columns=OUTCOME_ORDER, fill_value=0.0)


def cost_by_outcome(journey_df: pd.DataFrame, final_wave: str = "Onda_3") -> pd.DataFrame:
    """Beneficiários e custo médio em 90 dias por desfecho."""
    outcome = journey_df[final_wave].map(classify_outcome).rename("desfecho")
    summary = journey_df.groupby(outcome)["custo_total"].agg(beneficiarios="size", custo_medio="mean")
    return summary.reindex(OUTCOME_ORDER).dropna().reset_index()
