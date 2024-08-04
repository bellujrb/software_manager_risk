import streamlit as st

from data.inventory_threat_service import get_assets, get_catalogues, post_catalogue


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

    st.subheader("Catálogos de Ameaça")
    st.session_state.catalogue_data.columns = [
        'ID', 'Grupo de Ameaça', 'Evento de Ameaça', 'Descrição', 'Em Escopo'
    ]
    st.dataframe(st.session_state.catalogue_data)

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
                st.session_state.catalogue_data = get_catalogues()
                st.session_state.catalogue_data.columns = [
                    'ID', 'Grupo de Ameaça', 'Evento de Ameaça', 'Descrição', 'Em Escopo'
                ]
                st.experimental_rerun()
            else:
                st.error(f"Erro ao adicionar catálogo: {response.status_code} - {response.text}")