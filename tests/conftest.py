import pandas as pd
import pytest


def _claims(rows):
    columns = ["id_beneficiario", "comorbidade", "faixa_etaria", "data_atendimento", "tipo_evento", "custo_evento"]
    df = pd.DataFrame(rows, columns=columns)
    df["data_atendimento"] = pd.to_datetime(df["data_atendimento"])
    return df


@pytest.fixture
def toy_claims() -> pd.DataFrame:
    """Três jornadas conhecidas, escritas à mão.

    A: APS -> exame (D10) + PS (D30) -> especialista (D60)   [urgência no seguimento]
    B: PS -> nada até D45 -> APS (D70)
    C: APS -> especialista (D20) -> nada; evento em D120 fica fora do horizonte
    """
    return _claims([
        ("A", "Diabetes", "40-59", "2026-01-01", "Consulta_APS", 100.0),
        ("A", "Diabetes", "40-59", "2026-01-11", "Exame_Rotina", 50.0),
        ("A", "Diabetes", "40-59", "2026-01-31", "Pronto_Socorro", 600.0),
        ("A", "Diabetes", "40-59", "2026-03-02", "Consulta_Especialista", 250.0),
        ("B", "DPOC", "60+", "2026-02-01", "Pronto_Socorro", 700.0),
        ("B", "DPOC", "60+", "2026-04-12", "Consulta_APS", 110.0),
        ("C", "Hipertensão", "18-39", "2026-01-05", "Consulta_APS", 90.0),
        ("C", "Hipertensão", "18-39", "2026-01-25", "Consulta_Especialista", 240.0),
        ("C", "Hipertensão", "18-39", "2026-05-05", "Internacao", 9000.0),
    ])
