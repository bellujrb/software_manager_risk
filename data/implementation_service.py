import pandas as pd
import streamlit as st
import requests

from config.settings import BASE_API_URL


def fetch_control_implementation_data():
    url = f'{BASE_API_URL}api/all-implementation'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["Response"]
        return pd.DataFrame(data)
    else:
        st.error("Falha ao buscar dados de implementação de controle")
        return pd.DataFrame(columns=[
            'id', 'controlId', 'current', 'proposed', 'percentCurrent', 'percentProposed', 'cost'
        ])


def update_control_implementation(control_id, current, proposed, cost):
    url = f'{BASE_API_URL}api/implementation/{control_id}'
    data = {
        "current": int(current),
        "proposed": int(proposed),
        "cost": int(cost)
    }
    response = requests.put(url, json=data)
    return response.status_code, response.json()