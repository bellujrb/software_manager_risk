import streamlit as st
import pandas as pd
import requests
import json

def load_assets():
    try:
        response = requests.get('http://3.142.77.137:8080/api/assets')
        response.raise_for_status()
        assets_data = response.json()['Response']
        df = pd.DataFrame.from_records(assets_data)
        df['id'] = df['id'].astype(int)  # Garante que o ID seja um inteiro
        return df
    except requests.RequestException as e:
        st.error(f"Erro ao fazer a chamada da API: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

def post_asset(data):
    url = 'http://3.142.77.137:8080/api/create-asset'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        reload_assets()
    return response

def update_asset(asset_id, data):
    url = f'http://3.142.77.137:8080/api/asset/{asset_id}'
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        reload_assets()
    return response

def delete_asset(asset_id):
    url = f'http://3.142.77.137:8080/api/asset/{asset_id}'
    response = requests.delete(url)
    if response.status_code == 200:
        reload_assets()
    return response

def reload_assets():
    st.session_state.data = load_assets()

def enter_asset_fields(asset=None):
    return {
        'name': st.text_input("Nome", value=asset['name'] if asset is not None else ''),
        'description': st.text_area("Descrição", value=asset['description'] if asset is not None else ''),
        'location': st.text_input("Local", value=asset['location'] if asset is not None else ''),
        'responsible': st.text_input("Responsável", value=asset['responsible'] if asset is not None else ''),
        'business_value': st.number_input("Valor para o negócio (R$)", value=float(asset['business_value']) if asset is not None else 0.0, format='%f'),
        'replacement_cost': st.number_input("Custo de reposição (R$)", value=float(asset['replacement_cost']) if asset is not None else 0.0, format='%f'),
        'criticality': st.selectbox("Criticidade", ['Alta', 'Média', 'Baixa'], index=['Alta', 'Média', 'Baixa'].index(asset['criticality']) if asset is not None else 0),
        'users': st.text_input("Usuários", value=asset['users'] if asset is not None else ''),
        'roleInTargetEnvironment': st.text_input("Ambiente Alvo", value=asset['roleInTargetEnvironment'] if asset is not None else '')
    }

def run():
    st.title('Inventário de Assets')

    if 'data' not in st.session_state:
        reload_assets()

    operation = st.radio("Escolha a operação:", ['Criar', 'Editar', 'Excluir'])

    if operation == 'Criar':
        with st.form("form_create_asset"):
            fields = enter_asset_fields()
            if st.form_submit_button("Registrar Asset"):
                response = post_asset(fields)
                if response.status_code == 200:
                    st.success("Asset registrado com sucesso!")
                else:
                    st.error(f"Falha ao registrar o asset: {response.status_code} - {response.text}")

    elif operation == 'Editar':
        asset_ids = st.session_state.data['id'].tolist()  # Lista de IDs como inteiros
        asset_id_selected = st.selectbox("Selecione o ID do Asset para editar:", asset_ids)
        asset_to_edit = st.session_state.data.loc[st.session_state.data['id'] == asset_id_selected].iloc[0]
        with st.form("form_edit_asset"):
            fields = enter_asset_fields(asset_to_edit)
            if st.form_submit_button("Salvar Alterações"):
                response = update_asset(asset_id_selected, fields)
                if response.status_code == 200:
                    st.success("Asset atualizado com sucesso!")
                else:
                    st.error(f"Falha ao atualizar o asset: {response.status_code} - {response.text}")

    elif operation == 'Excluir':
        asset_ids = st.session_state.data['id'].tolist()  # Lista de IDs como inteiros
        asset_id_to_delete = st.selectbox("Selecione o ID do Asset para excluir:", asset_ids)
        if st.button("Excluir Asset"):
            response = delete_asset(asset_id_to_delete)
            if response.status_code == 200:
                st.success("Asset excluído com sucesso!")
            else:
                st.error(f"Falha ao excluir o asset: {response.status_code} - {response.text}")

    st.write("Inventário de Assets Registrados:")
    st.dataframe(st.session_state.data)