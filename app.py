import streamlit as st
from src.data_generator import generate_synthetic_claims
from src.journey_transformer import build_journey_waves, generate_sankey_transitions
from src.sankey_builder import create_sankey_chart

st.set_page_config(page_title="Patient Journey Analytics", layout="wide")

st.title("🏥 Patient Journey & Care Pathway Analytics")
st.markdown("Visualização da jornada do paciente crônico em ondas de atendimento.")

@st.cache_data
def load_data():
    return generate_synthetic_claims()

df_raw = load_data()

comorbidities = ['Todas'] + list(df_raw['comorbidade'].unique())
selected_c = st.sidebar.selectbox("Filtrar por Comorbidade", comorbidities)

if selected_c != 'Todas':
    df_filtered = df_raw[df_raw['comorbidade'] == selected_c]
else:
    df_filtered = df_raw.copy()

journey_df = build_journey_waves(df_filtered)
flow_df, labels = generate_sankey_transitions(journey_df)

fig = create_sankey_chart(flow_df, labels)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Ver Amostra dos Dados Transformados"):
    st.dataframe(journey_df.head(20))