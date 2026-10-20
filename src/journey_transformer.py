"""Transforma claims em jornadas por ondas temporais e em transições para o Sankey."""

from __future__ import annotations

from typing import NamedTuple

import pandas as pd

from src.taxonomy import DISPLAY_ORDER, EVENT_PRIORITY, NO_CARE, URGENCY_EVENTS


class Wave(NamedTuple):
    name: str
    start_day: int
    end_day: int


# Dias contados a partir do primeiro atendimento do beneficiário (data índice)
DEFAULT_WAVES = (
    Wave("Onda_1", 0, 0),    # Porta de entrada
    Wave("Onda_2", 1, 45),   # Conduta / investigação
    Wave("Onda_3", 46, 90),  # Desfecho / longitudinalidade
)

PATIENT_ATTRIBUTES = ["comorbidade", "faixa_etaria"]


def build_journey_waves(df: pd.DataFrame, waves: tuple[Wave, ...] = DEFAULT_WAVES) -> pd.DataFrame:
    """Consolida os eventos de cada beneficiário em uma coluna por onda temporal.

    Cada onda recebe o evento de maior acuidade ocorrido na sua janela de dias, ou
    ``Sem_Atendimento`` quando não houve contato — assim nenhum paciente é descartado
    e a descontinuidade do cuidado fica explícita no fluxo.
    """
    attributes = [c for c in PATIENT_ATTRIBUTES if c in df.columns]
    horizon = max(w.end_day for w in waves)

    events = df.copy()
    index_date = events.groupby("id_beneficiario")["data_atendimento"].transform("min")
    events["dia"] = (events["data_atendimento"] - index_date).dt.days
    events = events[events["dia"] <= horizon]
    events["prioridade"] = events["tipo_evento"].map(EVENT_PRIORITY)

    journeys = events.groupby("id_beneficiario")[attributes].first()

    for wave in waves:
        in_window = events[events["dia"].between(wave.start_day, wave.end_day)]
        top_event = (
            in_window.sort_values("prioridade")
            .groupby("id_beneficiario")["tipo_evento"]
            .last()
        )
        journeys[wave.name] = top_event.reindex(journeys.index).fillna(NO_CARE)

    totals = events.groupby("id_beneficiario").agg(
        n_eventos=("tipo_evento", "size"),
        custo_total=("custo_evento", "sum"),
    )
    followup = events[events["dia"] > 0]
    used_urgency = followup.groupby("id_beneficiario")["tipo_evento"].agg(
        lambda s: s.isin(URGENCY_EVENTS).any()
    )

    journeys = journeys.join(totals)
    journeys["custo_total"] = journeys["custo_total"].round(2)
    journeys["urgencia_no_seguimento"] = used_urgency.reindex(journeys.index, fill_value=False).astype(bool)
    return journeys.reset_index()


def wave_columns(journey_df: pd.DataFrame) -> list[str]:
    return [c for c in journey_df.columns if c.startswith("Onda_")]


def generate_sankey_transitions(journey_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera nós e links (source -> target -> value) entre ondas consecutivas.

    Retorna ``(flow_df, nodes_df)``. Os nós são identificados por (onda, evento), então o
    mesmo evento aparece uma vez por onda.
    """
    cols = wave_columns(journey_df)

    nodes = [
        (wave, event)
        for wave in cols
        for event in DISPLAY_ORDER
        if (journey_df[wave] == event).any()
    ]
    nodes_df = pd.DataFrame(nodes, columns=["onda", "evento"])
    nodes_df["node_id"] = range(len(nodes_df))
    node_id = {(n.onda, n.evento): n.node_id for n in nodes_df.itertuples()}

    links = []
    for source_wave, target_wave in zip(cols, cols[1:], strict=False):
        pair = journey_df.groupby([source_wave, target_wave]).size().reset_index(name="value")
        pair["source_id"] = [node_id[(source_wave, e)] for e in pair[source_wave]]
        pair["target_id"] = [node_id[(target_wave, e)] for e in pair[target_wave]]
        pair["source_event"] = pair[source_wave]
        pair["target_event"] = pair[target_wave]
        links.append(pair[["source_id", "target_id", "source_event", "target_event", "value"]])

    flow_df = pd.concat(links, ignore_index=True)
    flow_df["pct_origem"] = flow_df["value"] / flow_df.groupby("source_id")["value"].transform("sum")
    return flow_df, nodes_df
