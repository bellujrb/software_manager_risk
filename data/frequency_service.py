import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


def get_threat_link_data():
    url = f'{BASE_API_URL}api/all-frequency'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json()["Response"])
    else:
        st.error("Falha ao obter dados de ameaças")
        return pd.DataFrame()


def update_threat_link_data(data, id):
    url = f'{BASE_API_URL}api/frequency/{id}'
    response = requests.put(url, json=data)
    if response.status_code == 200:
        st.success("Dados atualizados com sucesso")
    else:
        st.error("Falha ao atualizar dados")
