import requests
import pandas as pd
import streamlit as st

from config.settings import BASE_API_URL


def get_catalogues():
    url = f"{BASE_API_URL}api/all-catalogue"
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


def fetch_event_data(event_name, loss_type):
    url = f"{BASE_API_URL}/"
    headers = {
        'Content-Type': 'application/json',
        'ThreatEvent': event_name,
        'Loss': loss_type
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data:
            json_data['FrequencyMin'] = int(float(json_data['FrequencyMin']))
            json_data['FrequencyEstimate'] = int(float(json_data['FrequencyEstimate']))
            json_data['FrequencyMax'] = int(float(json_data['FrequencyMax']))
            json_data['LossMin'] = int(float(json_data['LossMin']))
            json_data['LossEstimate'] = int(float(json_data['LossEstimate']))
            json_data['LossMax'] = int(float(json_data['LossMax']))
        return json_data
    else:
        st.error(f'Falha ao recuperar dados do evento: {response.status_code}')
        return None


def fetch_aggregated_data(loss_type):
    url = f"{BASE_API_URL}simulation-aggregated"
    headers = {
        'Content-Type': 'application/json',
        'Loss': loss_type
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados agregados: {response.status_code}")
        return None


def fetch_appetite_data(loss_type):
    url = f"{BASE_API_URL}simulation-appetite"
    headers = {
        'accept': 'application/json',
        'Loss': loss_type
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados de apetite: {response.status_code}")
        return None
