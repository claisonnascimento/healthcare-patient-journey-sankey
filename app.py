import pandas as pd
import streamlit as st

from src.data_generator import AGE_BANDS, COMORBIDITIES, generate_synthetic_claims
from src.journey_transformer import build_journey_waves, generate_sankey_transitions
from src.metrics import compute_kpis, cost_by_outcome, outcome_by_comorbidity
from src.sankey_builder import (
    create_cost_by_outcome_chart,
    create_outcome_by_comorbidity_chart,
    create_sankey_chart,
)
from src.taxonomy import EVENT_LABELS

st.set_page_config(page_title="Patient Journey Analytics", page_icon="🏥", layout="wide")


@st.cache_data
def load_journeys(n_patients: int, seed: int) -> pd.DataFrame:
    claims = generate_synthetic_claims(n_patients=n_patients, seed=seed)
    return build_journey_waves(claims)


def brl(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def pct(value: float) -> str:
    return f"{value:.1%}".replace(".", ",")


def sidebar_filters(journeys: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtros")
    comorbidities = st.sidebar.multiselect("Comorbidade", COMORBIDITIES, default=COMORBIDITIES)
    age_bands = st.sidebar.multiselect("Faixa etária", AGE_BANDS, default=AGE_BANDS)
    entry_points = st.sidebar.multiselect(
        "Porta de entrada (Onda 1)",
        options=sorted(journeys["Onda_1"].unique()),
        default=sorted(journeys["Onda_1"].unique()),
        format_func=EVENT_LABELS.get,
    )
    return journeys[
        journeys["comorbidade"].isin(comorbidities)
        & journeys["faixa_etaria"].isin(age_bands)
        & journeys["Onda_1"].isin(entry_points)
    ]


def render_kpis(journeys: pd.DataFrame) -> None:
    kpis = compute_kpis(journeys)
    cols = st.columns(5)
    cols[0].metric("Beneficiários", f"{kpis.beneficiarios:,}".replace(",", "."))
    cols[1].metric(
        "Uso de urgência", pct(kpis.taxa_urgencia),
        help="% com Pronto-Socorro ou internação entre D1 e D90.",
    )
    cols[2].metric(
        "Fuga APS → urgência", pct(kpis.fuga_aps_urgencia),
        help="Entre quem entrou pela APS, % que usou urgência no seguimento.",
    )
    cols[3].metric(
        "Perda de seguimento", pct(kpis.taxa_abandono),
        help="% sem nenhum contato entre D46 e D90 — sinal de descontinuidade do cuidado.",
    )
    cols[4].metric(
        "Custo médio em 90 dias", brl(kpis.custo_medio),
        help=(
            f"Com urgência: {brl(kpis.custo_medio_com_urgencia)} · "
            f"Sem urgência: {brl(kpis.custo_medio_sem_urgencia)}"
        ),
    )


def main() -> None:
    st.title("🏥 Patient Journey & Care Pathway Analytics")
    st.caption(
        "Jornada de beneficiários crônicos em três ondas temporais a partir do primeiro "
        "atendimento. Dados 100% sintéticos, gerados com lógica clínica de adesão e risco."
    )

    with st.sidebar.expander("Simulação", expanded=False):
        n_patients = st.slider("Beneficiários simulados", 300, 5000, 1500, step=100)
        seed = st.number_input("Semente aleatória", value=42, step=1)

    journeys = sidebar_filters(load_journeys(n_patients, int(seed)))
    if journeys.empty:
        st.warning("Nenhum beneficiário corresponde aos filtros selecionados.")
        return

    render_kpis(journeys)

    tab_flow, tab_outcomes, tab_data = st.tabs(["Fluxo em ondas", "Desfechos e custo", "Dados"])

    with tab_flow:
        flow_df, nodes_df = generate_sankey_transitions(journeys)
        st.plotly_chart(create_sankey_chart(flow_df, nodes_df), width="stretch")
        st.caption(
            "Cada onda mostra o evento de maior acuidade na janela. Links assumem a cor do "
            "destino: tons quentes indicam descompensação, cinza indica perda de seguimento."
        )

    with tab_outcomes:
        left, right = st.columns(2)
        with left:
            st.subheader("Desfecho na Onda 3 por comorbidade")
            st.plotly_chart(
                create_outcome_by_comorbidity_chart(outcome_by_comorbidity(journeys)), width="stretch"
            )
        with right:
            st.subheader("Custo médio por desfecho")
            st.plotly_chart(create_cost_by_outcome_chart(cost_by_outcome(journeys)), width="stretch")

    with tab_data:
        st.dataframe(journeys, width="stretch", hide_index=True)
        st.download_button(
            "Baixar jornadas (CSV)",
            journeys.to_csv(index=False).encode("utf-8"),
            file_name="jornadas_beneficiarios.csv",
            mime="text/csv",
        )


main()
