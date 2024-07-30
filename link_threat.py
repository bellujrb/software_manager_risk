import streamlit as st
import pandas as pd


def get_threat_events():
    data = {
        "Response": [
            {
                "threat_id": 1,
                "threat_event": "Malware attack",
                "affected_asset": ["", "Alta Plataforma"]
            },
            {
                "threat_id": 2,
                "threat_event": "Technology failure",
                "affected_asset": ["Alta Plataforma", "Baixa Plataforma",
                                   "API"]
            },
            {
                "threat_id": 3,
                "threat_event": "Infrastructure Failure event",
                "affected_asset": ["Alta Plataforma", "Baixa Plataforma",
                                   "API"]
            },
        ]
    }

    df = pd.DataFrame(data["Response"])
    df['affected_asset'] = df['affected_asset'].apply(lambda x: ', '.join(filter(None, x)))
    return df


def run():
    st.title('Vinculação de ativos de eventos de ameaça')

    threat_data = get_threat_events()

    if threat_data.empty:
        st.error('Nenhum dado de evento de ameaça disponível.')
    else:
        st.write("Eventos de ameaça:")
        st.dataframe(threat_data[['threat_id', 'threat_event', 'affected_asset']])
