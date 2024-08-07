import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


def get_control_data():
    url = f'{BASE_API_URL}api/all-control'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            return df
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de controle: {response.status_code}')
    return pd.DataFrame()


def create_control(control_reference, control_type, in_scope, information):
    url = f'{BASE_API_URL}api/control'
    payload = {
        "control_reference": control_reference,
        "control_type": control_type,
        "in_scope": in_scope,
        "information": information
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        st.success('Controle criado com sucesso!')
    else:
        st.error(f'Erro ao criar controle: {response.status_code}')


def update_control(control_id, control_reference, control_type, in_scope, information):
    url = f'{BASE_API_URL}api/control/{control_id}'
    payload = {
        "id": int(control_id),
        "control_reference": control_reference,
        "control_type": control_type,
        "in_scope": in_scope,
        "information": information
    }
    response = requests.put(url, json=payload)
    if response.status_code == 200:
        st.success('Controle atualizado com sucesso!')
    else:
        st.error(f'Erro ao atualizar controle: {response.status_code}, {response.text}')
