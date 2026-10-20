import pandas as pd
import numpy as np

def generate_synthetic_claims(n_patients: int = 500, seed: int = 42) -> pd.DataFrame:
    """Gera um dataset sintético de sinistros/atendimentos de saúde."""
    np.random.seed(seed)
    
    patient_ids = [f"BEN_{1000 + i}" for i in range(n_patients)]
    comorbidities = ['Hipertensão', 'Diabetes', 'Obesidade', 'Cardiopatia', 'DPOC']
    events = ['Consulta_APS', 'Consulta_Especialista', 'Exame_Rotina', 'Exame_Complexo', 'Pronto_Socorro', 'Internacao']
    event_weights = [0.35, 0.25, 0.20, 0.10, 0.07, 0.03]
    
    records = []
    
    for pid in patient_ids:
        c_type = np.random.choice(comorbidities)
        n_events = np.random.randint(2, 6) # Cada paciente tem entre 2 e 5 eventos
        
        base_date = pd.Timestamp('2026-01-01') + pd.Timedelta(days=int(np.random.randint(0, 30)))
        
        for e in range(n_events):
            event_date = base_date + pd.Timedelta(days=int(e * np.random.randint(7, 30)))
            records.append({
                'id_beneficiario': pid,
                'comorbidade': c_type,
                'data_atendimento': event_date,
                'tipo_evento': np.random.choice(events, p=event_weights),
                'custo_evento': round(float(np.random.uniform(80, 1500)), 2)
            })
            
    df = pd.DataFrame(records)
    return df.sort_values(by=['id_beneficiario', 'data_atendimento']).reset_index(drop=True)

if __name__ == "__main__":
    df_raw = generate_synthetic_claims()
    df_raw.to_csv("data/raw/synthetic_claims.csv", index=False)
    print(f"Dataset sintético criado com sucesso! Total de registros: {len(df_raw)}")