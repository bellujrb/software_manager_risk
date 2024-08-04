import streamlit as st

from data.inventory_assets_service import reload_assets, post_asset, update_asset, delete_asset
from utils.helpers import show_error, show_success


def enter_asset_fields(asset=None):
    return {
        'name': st.text_input("Nome", value=asset['name'] if asset else ''),
        'description': st.text_area("Descrição", value=asset['description'] if asset else ''),
        'location': st.text_input("Local", value=asset['location'] if asset else ''),
        'responsible': st.text_input("Responsável", value=asset['responsible'] if asset else ''),
        'business_value': st.number_input("Valor para o negócio (R$)",
                                          value=float(asset['business_value']) if asset else 0.0,
                                          format='%f'),
        'replacement_cost': st.number_input("Custo de reposição (R$)",
                                            value=float(asset['replacement_cost']) if asset else 0.0,
                                            format='%f'),
        'criticality': st.selectbox("Criticidade", ['Alta', 'Média', 'Baixa'],
                                    index=['Alta', 'Média', 'Baixa'].index(asset['criticality']) if asset else 0),
        'users': st.text_input("Usuários", value=asset['users'] if asset else ''),
        'roleInTargetEnvironment': st.text_input("Ambiente Alvo",
                                                 value=asset['roleInTargetEnvironment'] if asset else '')
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

    st.write("Inventário de Assets Registrados:")
    st.dataframe(st.session_state.data)