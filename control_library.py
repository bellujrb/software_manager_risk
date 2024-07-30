import streamlit as st
import pandas as pd
import requests


def get_control_data():
    url = 'http://3.142.77.137:8080/api/all-control'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            st.write("Colunas originais:", df.columns.tolist())
            return df
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de controle: {response.status_code}')
    return pd.DataFrame()


def run():
    st.title('Biblioteca de Controles')

    if 'control_data' not in st.session_state:
        st.session_state.control_data = get_control_data()

    if st.session_state.control_data.empty:
        st.error('Não há dados de controles disponíveis.')
        return

    df = st.session_state.control_data

    df.rename(columns={
        'ID': 'ID do Controle',
        'ControlType': 'Tipo de Controle',
        'ControlReference': 'Referência do Controle',
        'Information': 'Informação'
    }, inplace=True)

    st.write("Controles Registrados:")
    st.dataframe(df)
