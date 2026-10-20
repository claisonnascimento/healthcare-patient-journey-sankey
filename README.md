# 🏥 Patient Journey & Care Pathway Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Sankey-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Plataforma analítica para mapeamento da jornada do paciente e rastreamento de linhas de cuidado em operadoras de saúde suplementar usando gráficos de Sankey em ondas.**

---

## 📌 Visão Geral do Projeto

Na **Gestão de Saúde Populacional (GSP)**, o acompanhamento contínuo da trajetória de beneficiários crônicos (com condições como Hipertensão, Diabetes, Obesidade, Cardiopatias e DPOC) é o pilar central para evitar a fragmentação do cuidado e conter a sinistralidade elevada.

Este projeto simula e resolve um problema real de saúde suplementar: **transformar registros brutos de utilização/sinistro (*claims*) em um mapa de fluxo sequencial por ondas de atendimento**. A ferramenta identifica visualmente gargalos na atenção primária, descontinuidades de tratamento e a taxa de fuga de pacientes para serviços de urgência (Pronto-Socorro e Internações).

---

## 🎯 Caso de Uso de Negócio (*Business Case*)

* **Prevenção de Sinistralidade Evitável:** Identificação precoce de beneficiários que abandonam o acompanhamento eletivo (APS/Especialista) e descompensam no Pronto-Socorro.
* **Eficiência Operacional:** Mapeamento do percurso real (*real-world care path*) comparado à linha de cuidado ideal recomendada pelas diretrizes clínicas.
* **Segmentação Epidemiológica:** Análise granular do comportamento de transição filtrado por comorbidade crônica específica.

---

## 📐 Estrutura da Análise em Ondas (Care Pathways)

A jornada do paciente é processada e categorizada em 3 ondas temporais de transição:

1. **Onda 1 (Ponto de Entrada / Diagnóstico):** Primeiro atendimento registrado no período (Ex: Consulta APS, Especialista ou Pronto-Socorro).
2. **Onda 2 (Conduta / Exames / Acompanhamento):** Desfecho intermediário nos primeiros 30 a 60 dias (Ex: Realização de exames de rotina/complexos ou retorno especialista).
3. **Onda 3 (Desfecho / Longitudinalidade):** Status do paciente em 90 dias (Ex: Retenção no programa preventivo vs. reuso de urgência/internação).

---

## 🛠️ Arquitetura e Engenharia de Dados

A solução foi desenvolvida com arquitetura modularizada para facilitar a manutenção e escalabilidade: