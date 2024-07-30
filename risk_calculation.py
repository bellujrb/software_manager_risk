import streamlit as st
import pandas as pd
import requests


def get_risk_data():
    url = 'http://3.142.77.137:8080/api/risk'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            return pd.DataFrame(json_response['Response'])
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de riscos: {response.status_code}')
    return pd.DataFrame()


def run():
    st.title('Cálculo de Risco')

    if 'risk_data' not in st.session_state:
        st.session_state.risk_data = get_risk_data()

    if st.session_state.risk_data.empty:
        st.error('Não há dados de riscos disponíveis.')
        return

    df = st.session_state.risk_data

    df.rename(columns={
        'threat_event_id': 'ID do Evento de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'risk_type': 'Tipo de Risco',
        'min': 'Mínimo',
        'max': 'Máximo',
        'mode': 'Moda',
        'estimate': 'Estimativa'
    }, inplace=True)

    st.write("Tabela de Riscos:")

    metric_choice = st.selectbox('Selecione o Tipo de Risco para Visualizar:', ['Frequency', 'Loss', 'Risk'])

    if st.button('Mostrar Detalhes'):
        metric_data = df[df['Tipo de Risco'] == metric_choice]

        if not metric_data.empty:
            st.write(f"Detalhes para {metric_choice}:")
            st.dataframe(metric_data)
        else:
            st.warning(f"Não há dados disponíveis para {metric_choice}.")
