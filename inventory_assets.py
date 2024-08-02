import streamlit as st
import pandas as pd
import requests
import json
import locale

# Configurando locale para exibir os valores monetários em reais
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def post_asset(data):
    url = 'http://3.142.77.137:8080/api/create-asset'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response

def format_currency(value):
    return locale.currency(value, grouping=True)

def run():
    st.title('Inventário de Assets')

    if 'data' not in st.session_state:
        try:
            response = requests.get('http://3.142.77.137:8080/api/assets')
            response.raise_for_status()
            assets_data = response.json()['Response']

            st.session_state.data = pd.DataFrame.from_records(assets_data, columns=[
                'id', 'name', 'description', 'location', 'responsible',
                'business_value', 'replacement_cost', 'criticality',
                'users', 'roleInTargetEnvironment'
            ])
            st.session_state.data.columns = [
                'ID', 'Nome', 'Descrição', 'Local', 'Responsável',
                'Valor para o Negócio', 'Custo de Reposição', 'Criticidade',
                'Usuários', 'Ambiente Alvo'
            ]
            if st.session_state.data.empty:
                st.error("Os dados carregados estão vazios.")
        except requests.RequestException as e:
            st.error(f"Erro ao fazer a chamada da API: {e}")

    with st.form("form_assets"):
        st.write("Preencha as informações do asset a seguir:")

        nome = st.text_input("Nome")
        descricao = st.text_area("Descrição")
        local = st.text_input("Local")
        responsavel = st.text_input("Responsável")
        valor_negocio = st.number_input("Valor para o negócio (R$)", min_value=0.0, format='%f')
        custo_reposicao = st.number_input("Custo de reposição (R$)", min_value=0.0, format='%f')
        criticidade = st.selectbox("Criticidade", ['Alta', 'Média', 'Baixa'])
        usuarios = st.text_input("Usuários")
        ambiente_alvo = st.text_input("Ambiente Alvo")

        submitted = st.form_submit_button("Registrar Asset")
        if submitted:
            new_asset = {
                'name': nome,
                'description': descricao,
                'location': local,
                'responsible': responsavel,
                'business_value': valor_negocio,
                'replacement_cost': custo_reposicao,
                'criticality': criticidade,
                'users': usuarios,
                'roleInTargetEnvironment': ambiente_alvo
            }
            response = post_asset(new_asset)
            if response.status_code == 200:
                st.success("Asset registrado com sucesso!")
                new_asset['business_value'] = valor_negocio
                new_asset['replacement_cost'] = custo_reposicao
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_asset])], ignore_index=True)
            else:
                st.error(f"Falha ao registrar o asset: {response.status_code} - {response.text}")

    # Formatar os valores monetários no DataFrame
    st.session_state.data['Valor para o Negócio'] = st.session_state.data['Valor para o Negócio'].apply(format_currency)
    st.session_state.data['Custo de Reposição'] = st.session_state.data['Custo de Reposição'].apply(format_currency)

    st.write("Inventário de Assets Registrados:")
    st.write(st.session_state.data)