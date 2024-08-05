import streamlit as st
import requests

from config.settings import BASE_API_URL


def get_relevance_data():
    url = f'{BASE_API_URL}api/revelance'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f'Erro ao recuperar dados de relevância: {response.status_code}')
        return None


def update_relevance_data(control_id, porcent, type_of_attack):
    url = f'{BASE_API_URL}api/update-revelance'
    payload = {
        "controlId": int(control_id),
        "porcent": int(porcent),
        "type_of_attack": type_of_attack
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        st.success('Relevância atualizada com sucesso!')
        return response.json()
    else:
        st.error(f'Erro ao atualizar relevância: {response.status_code}')
        return None
