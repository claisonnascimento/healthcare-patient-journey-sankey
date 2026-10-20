"""Taxonomia compartilhada de eventos assistenciais: rótulos, categorias e cores."""

EVENTS = [
    "Consulta_APS",
    "Consulta_Especialista",
    "Exame_Rotina",
    "Exame_Complexo",
    "Pronto_Socorro",
    "Internacao",
]
NO_CARE = "Sem_Atendimento"
URGENCY_EVENTS = {"Pronto_Socorro", "Internacao"}
ELECTIVE_EVENTS = {"Consulta_APS", "Consulta_Especialista"}

# Quando há mais de um evento na mesma janela, o de maior acuidade representa a onda
EVENT_PRIORITY = {
    "Consulta_APS": 1,
    "Exame_Rotina": 2,
    "Consulta_Especialista": 3,
    "Exame_Complexo": 4,
    "Pronto_Socorro": 5,
    "Internacao": 6,
}

EVENT_LABELS = {
    "Consulta_APS": "Consulta APS",
    "Consulta_Especialista": "Especialista",
    "Exame_Rotina": "Exame de rotina",
    "Exame_Complexo": "Exame complexo",
    "Pronto_Socorro": "Pronto-Socorro",
    "Internacao": "Internação",
    NO_CARE: "Sem atendimento",
}

# Cores semânticas: azul/violeta = cuidado eletivo, verdes = apoio diagnóstico,
# âmbar/vermelho = urgência, cinza = ausência de cuidado
EVENT_COLORS = {
    "Consulta_APS": "#2a78d6",
    "Consulta_Especialista": "#6250d6",
    "Exame_Rotina": "#1baf7a",
    "Exame_Complexo": "#008300",
    "Pronto_Socorro": "#eda100",
    "Internacao": "#e34948",
    NO_CARE: "#9a9893",
}

# Ordem de exibição dos nós (de cima para baixo) em cada onda
DISPLAY_ORDER = EVENTS + [NO_CARE]
