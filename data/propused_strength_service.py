import requests
import streamlit as st

from config.settings import BASE_API_URL


def fetch_data_from_api():
    url = f'{BASE_API_URL}api/all-proposed'
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()["Response"]
    else:
        st.error(f"Erro ao buscar dados da API: {response.status_code}")
        return []
