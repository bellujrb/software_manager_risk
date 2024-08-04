import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


# Função para obter dados de perdas
def get_single_estimate():
    url = f"{BASE_API_URL}api/losshigh-singular"
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            if 'losses' in df.columns:
                df = df.explode('losses').reset_index(drop=True)
                losses_df = df['losses'].apply(pd.Series)
                df = pd.concat([df.drop(columns=['losses']), losses_df], axis=1)
                return df
            else:
                st.error('Chave "losses" não encontrada nos dados da resposta.')
                return pd.DataFrame()
        else:
            st.error('Recebido JSON vazio ou sem chave "Response".')
            return pd.DataFrame()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'Erro HTTP ao recuperar dados de perdas: {http_err}')
        return pd.DataFrame()
    except Exception as err:
        st.error(f'Erro ao recuperar dados de perdas: {err}')
        return pd.DataFrame()


# Função para atualizar perdas
def update_single_estimate(event_id, max_loss, min_loss, most_likely_loss):
    url = f"{BASE_API_URL}api/update-losshigh-singular/{event_id}"
    payload = {
        "maximum_loss": max_loss,
        "minimum_loss": min_loss,
        "most_likely_loss": most_likely_loss
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'Erro HTTP ao atualizar dados de perdas: {http_err}')
        return None
    except Exception as err:
        st.error(f'Erro ao atualizar dados de perdas: {err}')
        return None
