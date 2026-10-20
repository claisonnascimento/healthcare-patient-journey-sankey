import pandas as pd

from src.data_generator import COMORBIDITIES, HORIZON_DAYS, generate_synthetic_claims
from src.journey_transformer import build_journey_waves
from src.taxonomy import EVENTS


def test_schema_and_domains():
    df = generate_synthetic_claims(n_patients=200, seed=1)

    assert list(df.columns) == [
        "id_beneficiario", "comorbidade", "faixa_etaria", "data_atendimento", "tipo_evento", "custo_evento",
    ]
    assert df["id_beneficiario"].nunique() == 200
    assert set(df["tipo_evento"]) <= set(EVENTS)
    assert set(df["comorbidade"]) <= set(COMORBIDITIES)
    assert (df["custo_evento"] > 0).all()


def test_events_stay_within_horizon():
    df = generate_synthetic_claims(n_patients=300, seed=2)
    span = df.groupby("id_beneficiario")["data_atendimento"].agg(lambda s: (s.max() - s.min()).days)
    assert span.max() <= HORIZON_DAYS


def test_is_reproducible():
    pd.testing.assert_frame_equal(
        generate_synthetic_claims(n_patients=100, seed=7),
        generate_synthetic_claims(n_patients=100, seed=7),
    )


def test_urgency_raises_cost():
    """O mecanismo de negócio que o projeto demonstra precisa existir nos dados."""
    journeys = build_journey_waves(generate_synthetic_claims(n_patients=2000, seed=3))
    cost = journeys.groupby("urgencia_no_seguimento")["custo_total"].mean()
    assert cost[True] > 3 * cost[False]
