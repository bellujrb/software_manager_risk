import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


def get_risk_data(loss_mode):
    url = f"{BASE_API_URL}api/risk"
    headers = {'Loss': loss_mode}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            return pd.DataFrame(json_response['Response'])
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    elif response.status_code == 500:
        st.error(
            'Erro 500: Problema no servidor. Por favor, selecione uma abordagem de perda ou reinicie a página e '
            'escolha a abordagem novamente.')
    else:
        st.error(f'Erro ao recuperar dados de riscos: {response.status_code}')
    return pd.DataFrame()