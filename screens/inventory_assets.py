import streamlit as st
from data.inventory_assets_service import post_asset, update_asset, delete_asset, load_assets
from utils.helpers import show_error, show_success
import pandas as pd


def reload_assets():
    assets_data = load_assets()
    if assets_data is None:
        st.session_state.data = pd.DataFrame()
    else:
        st.session_state.data = pd.DataFrame.from_records(assets_data)
        st.session_state.data.rename(columns={
            'name': 'Nome',
            'description': 'Descrição',
            'location': 'Local',
            'responsible': 'Responsável',
            'business_value': 'Valor para o negócio (R$)',
            'replacement_cost': 'Custo de reposição (R$)',
            'criticality': 'Criticidade',
            'users': 'Usuários',
            'roleInTargetEnvironment': 'Ambiente Alvo'
        }, inplace=True)
        st.session_state.data['Valor para o negócio (R$)'] = st.session_state.data['Valor para o negócio (R$)'].apply(lambda x: f"R$ {x:,.2f}")
        st.session_state.data['Custo de reposição (R$)'] = st.session_state.data['Custo de reposição (R$)'].apply(lambda x: f"R$ {x:,.2f}")


def enter_asset_fields(asset=None):
    criticality_options = ['Alta', 'Média', 'Baixa']
    if asset is not None and asset['criticality'] in criticality_options:
        criticality_index = criticality_options.index(asset['criticality'])
    else:
        criticality_index = 0

    return {
        'name': st.text_input("Nome", value=asset['name'] if asset is not None else ''),
        'description': st.text_area("Descrição", value=asset['description'] if asset is not None else ''),
        'location': st.text_input("Local", value=asset['location'] if asset is not None else ''),
        'responsible': st.text_input("Responsável", value=asset['responsible'] if asset is not None else ''),
        'business_value': st.number_input("Valor para o negócio (R$)",
                                          value=float(asset['business_value']) if asset is not None else 0.0,
                                          format='%.2f'),
        'replacement_cost': st.number_input("Custo de reposição (R$)",
                                            value=float(asset['replacement_cost']) if asset is not None else 0.0,
                                            format='%.2f'),
        'criticality': st.selectbox("Criticidade", criticality_options, index=criticality_index),
        'users': st.text_input("Usuários", value=asset['users'] if asset is not None else ''),
        'roleInTargetEnvironment': st.text_input("Ambiente Alvo",
                                                 value=asset['roleInTargetEnvironment'] if asset is not None else '')
    }


def run():
    st.title('Inventário de Assets')

    if 'data' not in st.session_state:
        reload_assets()

    st.write("Inventário de Assets Registrados:")
    st.dataframe(st.session_state.data)

    operation = st.selectbox("Escolha a operação:", ['Criar', 'Editar', 'Excluir'])

    if operation == 'Criar':
        with st.form("form_create_asset"):
            fields = enter_asset_fields()
            if st.form_submit_button("Registrar Asset"):
                response = post_asset(fields)
                if response.status_code == 200:
                    reload_assets()
                    show_success("Asset registrado com sucesso!")
                else:
                    show_error(f"Falha ao registrar o asset: {response.status_code} - {response.text}")

    elif operation == 'Editar':
        asset_ids = st.session_state.data['id'].tolist()
        asset_id_selected = st.selectbox("Selecione o ID do Asset para editar:", asset_ids)
        asset_to_edit = st.session_state.data.loc[st.session_state.data['id'] == asset_id_selected].iloc[0]
        with st.form("form_edit_asset"):
            fields = enter_asset_fields(asset_to_edit)
            if st.form_submit_button("Salvar Alterações"):
                response = update_asset(asset_id_selected, fields)
                if response.status_code == 200:
                    reload_assets()
                    show_success("Asset atualizado com sucesso!")
                else:
                    show_error(f"Falha ao atualizar o asset: {response.status_code} - {response.text}")

    elif operation == 'Excluir':
        asset_ids = st.session_state.data['id'].tolist()
        asset_id_to_delete = st.selectbox("Selecione o ID do Asset para excluir:", asset_ids)
        if st.button("Excluir Asset"):
            response = delete_asset(asset_id_to_delete)
            if response.status_code == 200:
                reload_assets()
                show_success("Asset excluído com sucesso!")
            else:
                show_error(f"Falha ao excluir o asset: {response.status_code} - {response.text}")


