import pytest

from src.journey_transformer import build_journey_waves, generate_sankey_transitions
from src.taxonomy import NO_CARE


@pytest.fixture
def journeys(toy_claims):
    return build_journey_waves(toy_claims).set_index("id_beneficiario")


def test_keeps_every_patient(journeys):
    assert list(journeys.index) == ["A", "B", "C"]


def test_wave_takes_highest_acuity_event_in_window(journeys):
    # Exame de rotina (D10) e PS (D30) caem na Onda 2: PS prevalece
    assert journeys.loc["A", ["Onda_1", "Onda_2", "Onda_3"]].tolist() == [
        "Consulta_APS", "Pronto_Socorro", "Consulta_Especialista",
    ]


def test_empty_window_becomes_no_care(journeys):
    assert journeys.loc["B", "Onda_2"] == NO_CARE
    assert journeys.loc["C", "Onda_3"] == NO_CARE


def test_events_after_horizon_are_ignored(journeys):
    assert journeys.loc["C", "n_eventos"] == 2
    assert journeys.loc["C", "custo_total"] == pytest.approx(330.0)
    assert not journeys.loc["C", "urgencia_no_seguimento"]


def test_urgency_flag_ignores_entry_event(journeys):
    # B entrou pelo PS, mas não voltou à urgência no seguimento
    assert journeys.loc["A", "urgencia_no_seguimento"]
    assert not journeys.loc["B", "urgencia_no_seguimento"]


def test_sankey_flows_are_conserved(toy_claims):
    journeys = build_journey_waves(toy_claims)
    flow_df, nodes_df = generate_sankey_transitions(journeys)

    assert nodes_df["node_id"].is_unique
    assert set(flow_df["source_id"]) | set(flow_df["target_id"]) <= set(nodes_df["node_id"])

    wave_of = nodes_df.set_index("node_id")["onda"]
    for _, links in flow_df.groupby(flow_df["source_id"].map(wave_of)):
        assert links["value"].sum() == len(journeys)

    pct_by_source = flow_df.groupby("source_id")["pct_origem"].sum()
    assert pct_by_source.round(9).eq(1.0).all()
