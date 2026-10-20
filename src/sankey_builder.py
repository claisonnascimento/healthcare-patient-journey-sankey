import plotly.graph_objects as go
import pandas as pd

def create_sankey_chart(flow_df: pd.DataFrame, labels: list):
    """Gera uma figura do Plotly Sankey pronta para exibição."""
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="#1f77b4"
        ),
        link=dict(
            source=flow_df['source_id'],
            target=flow_df['target_id'],
            value=flow_df['value'],
            color="rgba(180, 180, 180, 0.4)"
        )
    )])
    
    fig.update_layout(
        title_text="Percurso do Paciente em Ondas de Atendimento",
        font_size=12,
        height=550
    )
    return fig