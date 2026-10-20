import pytest

from src.journey_transformer import build_journey_waves
from src.metrics import (
    OUTCOME_LOST,
    OUTCOME_RETAINED,
    OUTCOME_URGENCY,
    classify_outcome,
    compute_kpis,
    cost_by_outcome,
    outcome_by_comorbidity,
)
from src.taxonomy import NO_CARE


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        ("Consulta_APS", OUTCOME_RETAINED),
        ("Exame_Complexo", OUTCOME_RETAINED),
        ("Pronto_Socorro", OUTCOME_URGENCY),
        ("Internacao", OUTCOME_URGENCY),
        (NO_CARE, OUTCOME_LOST),
    ],
)
def test_classify_outcome(event, expected):
    assert classify_outcome(event) == expected


def test_compute_kpis(toy_claims):
    kpis = compute_kpis(build_journey_waves(toy_claims))

    assert kpis.beneficiarios == 3
    assert kpis.taxa_urgencia == pytest.approx(1 / 3)
    assert kpis.taxa_abandono == pytest.approx(1 / 3)
    assert kpis.taxa_retencao == pytest.approx(2 / 3)
    # A e C entraram pela APS; só A usou urgência
    assert kpis.fuga_aps_urgencia == pytest.approx(0.5)
    assert kpis.custo_medio_com_urgencia == pytest.approx(1000.0)
    assert kpis.custo_medio_sem_urgencia == pytest.approx((810 + 330) / 2)


def test_outcome_by_comorbidity_rows_sum_to_one(toy_claims):
    table = outcome_by_comorbidity(build_journey_waves(toy_claims))
    assert list(table.columns) == [OUTCOME_RETAINED, OUTCOME_URGENCY, OUTCOME_LOST]
    assert table.sum(axis=1).round(9).eq(1.0).all()


def test_cost_by_outcome_skips_empty_groups(toy_claims):
    summary = cost_by_outcome(build_journey_waves(toy_claims))
    assert summary["desfecho"].tolist() == [OUTCOME_RETAINED, OUTCOME_LOST]
    assert summary["beneficiarios"].sum() == 3
