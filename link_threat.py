import streamlit as st
import pandas as pd
import requests


def get_threat_events():
    url = 'http://3.142.77.137:8080/api/all-event'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            required_columns = ['threat_id', 'threat_event', 'affected_asset']
            # Adicionar colunas ausentes com valores vazios
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            return df.fillna("")
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar eventos de ameaça: {response.status_code}')
    # Retornar DataFrame com colunas necessárias vazias se ocorrer erro
    return pd.DataFrame(columns=['threat_id', 'threat_event', 'affected_asset'])


def run():
    st.title('Vinculação de Eventos de Ameaça a Ativos')

    if 'threat_data' not in st.session_state:
        st.session_state.threat_data = get_threat_events()

    if st.session_state.threat_data.empty:
        st.error('Não há dados de eventos de ameaça disponíveis.')
        return

    st.write("Eventos de Ameaça:")
    if not st.session_state.threat_data.empty:
        st.dataframe(st.session_state.threat_data[['threat_id', 'threat_event', 'affected_asset']])