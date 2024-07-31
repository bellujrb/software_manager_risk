# risk_data_display.py
import streamlit as st
import pandas as pd
import requests

def get_risk_data(loss_mode):
    url = 'http://3.142.77.137:8080/api/risk'
    headers = {'Loss': loss_mode}  # Configura o header com o tipo de perda selecionado
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            return pd.DataFrame(json_response['Response'])
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de riscos: {response.status_code}')
    return pd.DataFrame()

def display_risk_data():
    if 'loss_mode' in st.session_state:
        st.write(f"Modo de perda atual: {st.session_state['loss_mode']}")
        risk_data = get_risk_data(st.session_state['loss_mode'])
        if not risk_data.empty:
            st.dataframe(risk_data)
        else:
            st.error('Não há dados de riscos disponíveis para a seleção atual.')
    else:
        st.error('Por favor, selecione um modo de perda na página anterior.')

def run():
    display_risk_data()

run()
