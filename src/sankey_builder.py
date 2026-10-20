"""Figuras Plotly do dashboard: Sankey de ondas e gráficos de desfecho."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.metrics import OUTCOME_LOST, OUTCOME_RETAINED, OUTCOME_URGENCY
from src.taxonomy import EVENT_COLORS, EVENT_LABELS, NO_CARE

FONT_FAMILY = "Inter, Segoe UI, Helvetica, Arial, sans-serif"

WAVE_TITLES = {
    "Onda_1": "Onda 1 · Entrada (D0)",
    "Onda_2": "Onda 2 · Conduta (D1–D45)",
    "Onda_3": "Onda 3 · Desfecho (D46–D90)",
}

OUTCOME_COLORS = {
    OUTCOME_RETAINED: EVENT_COLORS["Consulta_APS"],
    OUTCOME_URGENCY: EVENT_COLORS["Internacao"],
    OUTCOME_LOST: EVENT_COLORS[NO_CARE],
}


def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"


def create_sankey_chart(flow_df: pd.DataFrame, nodes_df: pd.DataFrame, height: int = 620) -> go.Figure:
    """Sankey com nós coloridos pelo tipo de evento e links pela cor do destino."""
    node_titles = nodes_df["onda"].map(lambda w: WAVE_TITLES.get(w, w))

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        valueformat=",d",
        node=dict(
            pad=16,
            thickness=18,
            line=dict(width=0),
            label=nodes_df["evento"].map(EVENT_LABELS).tolist(),
            color=nodes_df["evento"].map(EVENT_COLORS).tolist(),
            customdata=node_titles.tolist(),
            hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{value} beneficiários<extra></extra>",
        ),
        link=dict(
            source=flow_df["source_id"],
            target=flow_df["target_id"],
            value=flow_df["value"],
            color=[_rgba(EVENT_COLORS[e], 0.35) for e in flow_df["target_event"]],
            customdata=flow_df["pct_origem"],
            hovertemplate=(
                "%{source.label} → %{target.label}<br>"
                "<b>%{value}</b> beneficiários (%{customdata:.0%} da origem)<extra></extra>"
            ),
        ),
    ))

    waves = list(dict.fromkeys(nodes_df["onda"]))
    positions = [i / (len(waves) - 1) for i in range(len(waves))] if len(waves) > 1 else [0.5]
    anchors = ["left"] + ["center"] * (len(waves) - 2) + ["right"] if len(waves) > 1 else ["center"]
    for wave, x, anchor in zip(waves, positions, anchors, strict=True):
        fig.add_annotation(
            x=x, y=1.06, xref="paper", yref="paper", xanchor=anchor, showarrow=False,
            text=f"<b>{WAVE_TITLES.get(wave, wave)}</b>", font=dict(size=13),
        )

    fig.update_layout(
        height=height,
        font=dict(family=FONT_FAMILY, size=13),
        margin=dict(l=8, r=8, t=56, b=8),
    )
    return fig


def create_outcome_by_comorbidity_chart(outcome_df: pd.DataFrame) -> go.Figure:
    """Barras 100% empilhadas: desfecho na Onda 3 por comorbidade."""
    ordered = outcome_df.sort_values(OUTCOME_URGENCY)
    fig = go.Figure()
    for outcome in outcome_df.columns:
        fig.add_bar(
            y=ordered.index,
            x=ordered[outcome],
            name=outcome,
            orientation="h",
            marker=dict(color=OUTCOME_COLORS[outcome]),
            text=ordered[outcome].map("{:.0%}".format),
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate="%{y} · " + outcome + ": <b>%{x:.1%}</b><extra></extra>",
        )
    fig.update_layout(
        barmode="stack",
        bargap=0.35,
        height=340,
        font=dict(family=FONT_FAMILY, size=13),
        xaxis=dict(tickformat=".0%", range=[0, 1.005], tickvals=[0, 0.25, 0.5, 0.75, 1], showgrid=False),
        yaxis=dict(title=None),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, traceorder="normal"),
        margin=dict(l=8, r=28, t=40, b=8),
    )
    return fig


def create_cost_by_outcome_chart(cost_df: pd.DataFrame) -> go.Figure:
    """Custo médio em 90 dias por desfecho na última onda."""
    fig = go.Figure(go.Bar(
        x=cost_df["desfecho"],
        y=cost_df["custo_medio"],
        marker=dict(color=[OUTCOME_COLORS[d] for d in cost_df["desfecho"]], cornerradius=4),
        text=cost_df["custo_medio"].map(lambda v: f"R$ {v:,.0f}".replace(",", ".")),
        textposition="outside",
        customdata=cost_df["beneficiarios"],
        hovertemplate="%{x}<br>Custo médio: <b>R$ %{y:,.0f}</b><br>%{customdata} beneficiários<extra></extra>",
    ))
    fig.update_layout(
        height=340,
        font=dict(family=FONT_FAMILY, size=13),
        yaxis=dict(title="Custo médio em 90 dias (R$)", tickprefix="R$ ", separatethousands=True),
        xaxis=dict(title=None),
        bargap=0.45,
        margin=dict(l=8, r=8, t=40, b=8),
        separators=",.",
    )
    return fig
