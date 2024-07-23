import streamlit as st
import pandas as pd
import requests


def update_threat_event(event_id, affected_assets):
    url = f'http://3.142.77.137:8080/api/event/{event_id}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "affected_asset": affected_assets
    }
    response = requests.put(url, headers=headers, json=payload)
    return response


def get_catalogues():
    url = 'http://3.142.77.137:8080/api/all-catalogue'
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
    url = 'http://3.142.77.137:8080/api/assets'
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
    url = 'http://3.142.77.137:8080/api/catalogue'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    return response


def run():
    st.title('Gerenciamento de Ameaças e Ativos')

    if 'assets' not in st.session_state:
        st.session_state.assets = get_assets()

    if 'threat_data' not in st.session_state:
        st.session_state.threat_data = get_catalogues()

    if 'catalogue_data' not in st.session_state:
        st.session_state.catalogue_data = get_catalogues()

    if st.session_state.assets.empty or st.session_state.threat_data.empty or st.session_state.catalogue_data.empty:
        st.error('Não há dados de ativos, eventos de ameaça ou catálogos disponíveis.')
        return

    # Exibir catálogos de ameaça
    st.subheader("Catálogos de Ameaça")
    st.dataframe(st.session_state.catalogue_data)

    # Formulário para adicionar novo catálogo
    with st.form("new_catalogue"):
        st.write("Adicionar Novo Catálogo de Ameaça")
        threat_group = st.text_input("Grupo de Ameaça")
        threat_event = st.text_input("Evento de Ameaça")
        description = st.text_area("Descrição")
        in_scope = st.checkbox("Em Escopo", value=True)

        submitted = st.form_submit_button("Adicionar Catálogo")
        if submitted:
            new_catalogue = {
                "threat_group": threat_group,
                "threat_event": threat_event,
                "description": description,
                "in_scope": in_scope
            }
            response = post_catalogue(new_catalogue)
            if response.status_code == 200:
                st.success("Catálogo adicionado com sucesso!")
                st.session_state.catalogue_data = get_catalogues()  # Atualiza os dados do catálogo
                st.experimental_rerun()
            else:
                st.error(f"Erro ao adicionar catálogo: {response.status_code} - {response.text}")