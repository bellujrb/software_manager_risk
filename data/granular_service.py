import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


def get_granular():
    url = f"{BASE_API_URL}api/losshigh-granuled"
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.json_normalize(json_response['Response'], 'Losses', ['ThreatEventID', 'ThreatEvent', 'Assets'])
            return df
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de perdas: {response.status_code}')
    return pd.DataFrame()


def update_granular(id, data):
    url = f"{BASE_API_URL}api/update-losshigh-granuled/{id}"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 200:
        return True
    else:
        st.error(f"Erro ao atualizar dados: {response.status_code} - {response.text}")
        return False
