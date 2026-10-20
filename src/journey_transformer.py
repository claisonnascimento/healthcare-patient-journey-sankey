import pandas as pd

def build_journey_waves(df: pd.DataFrame, max_waves: int = 3) -> pd.DataFrame:
    """Transforma eventos sequenciais em colunas de Ondas de atendimento por paciente."""
    df_sorted = df.sort_values(by=['id_beneficiario', 'data_atendimento']).copy()
    
    # Define a ordem do atendimento para cada beneficiário
    df_sorted['onda_num'] = df_sorted.groupby('id_beneficiario').cumcount() + 1
    
    # Filtra até a quantidade máxima de ondas desejada
    df_filtered = df_sorted[df_sorted['onda_num'] <= max_waves]
    
    # Pivot de linhas para colunas (Onda_1, Onda_2, Onda_3)
    pivoted = df_filtered.pivot(
        index=['id_beneficiario', 'comorbidade'],
        columns='onda_num',
        values='tipo_evento'
    ).reset_index()
    
    # Renomeia colunas
    cols = ['id_beneficiario', 'comorbidade'] + [f'Onda_{i}' for i in range(1, max_waves + 1)]
    pivoted.columns = cols
    
    return pivoted.dropna().reset_index(drop=True)

def generate_sankey_transitions(journey_df: pd.DataFrame):
    """Gera a matriz de adjacência (Source -> Target -> Value) para o Plotly Sankey."""
    transitions = []
    
    # Transição Onda 1 -> Onda 2
    t1 = journey_df.groupby(['Onda_1', 'Onda_2']).size().reset_index(name='value')
    t1.columns = ['source_label', 'target_label', 'value']
    t1['source_label'] = 'O1: ' + t1['source_label']
    t1['target_label'] = 'O2: ' + t1['target_label']
    transitions.append(t1)
    
    # Transição Onda 2 -> Onda 3
    t2 = journey_df.groupby(['Onda_2', 'Onda_3']).size().reset_index(name='value')
    t2.columns = ['source_label', 'target_label', 'value']
    t2['source_label'] = 'O2: ' + t2['source_label']
    t2['target_label'] = 'O3: ' + t2['target_label']
    transitions.append(t2)
    
    flow_df = pd.concat(transitions, ignore_index=True)
    
    # Mapeamento de rótulos únicos para índices numéricos
    unique_labels = list(pd.concat([flow_df['source_label'], flow_df['target_label']]).unique())
    label_map = {label: i for i, label in enumerate(unique_labels)}
    
    flow_df['source_id'] = flow_df['source_label'].map(label_map)
    flow_df['target_id'] = flow_df['target_label'].map(label_map)
    
    return flow_df, unique_labels