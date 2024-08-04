import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


def update_threat_event(event_id, affected_assets):
    url = f'{BASE_API_URL}/event/{event_id}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "affected_asset": affected_assets
    }
    response = requests.put(url, headers=headers, json=payload)
    return response


def get_catalogues():
    url = f'{BASE_API_URL}/all-catalogue'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            return df.fillna("")
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar catálogos: {response.status_code}')
    return pd.DataFrame()


def get_assets():
    url = f'{BASE_API_URL}/assets'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            return pd.DataFrame(json_response['Response']).fillna("")
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar ativos: {response.status_code}')
    return pd.DataFrame()


def post_catalogue(data):
    url = f'{BASE_API_URL}/catalogue'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    return response
