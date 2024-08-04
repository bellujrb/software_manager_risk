import requests
import pandas as pd
from config.settings import BASE_API_URL
import streamlit as st
import json


def load_assets():
    try:
        response = requests.get(f'{BASE_API_URL}api/assets')
        response.raise_for_status()
        assets_data = response.json()['Response']
        df = pd.DataFrame.from_records(assets_data)
        df['id'] = df['id'].astype(int)
        return df
    except requests.RequestException as e:
        st.error(f"Erro ao fazer a chamada da API: {e}")
        return pd.DataFrame()


def post_asset(data):
    url = f'{BASE_API_URL}api/create-asset'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response


def update_asset(asset_id, data):
    url = f'{BASE_API_URL}api/asset/{asset_id}'
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response


def delete_asset(asset_id):
    url = f'{BASE_API_URL}api/asset/{asset_id}'
    response = requests.delete(url)
    return response


def reload_assets():
    st.session_state.data = load_assets()
