import streamlit as st
from data.link_threat_service import get_threat_events, get_available_assets, update_threat_event


def run():
    st.title('Vinculação de Ativos de Eventos de Ameaça')

    threat_data = get_threat_events()
    available_assets = get_available_assets()

    if threat_data.empty:
        st.error('Nenhum dado de evento de ameaça disponível.')
        return

    st.write("Eventos de Ameaça:")
    st.dataframe(threat_data[['threat_id', 'threat_event', 'affected_asset']].rename(columns={
        'threat_id': 'ID de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'affected_asset': 'Ativo Afetado'
    }))

    st.write("Atualizar Evento de Ameaça")

    if 'selected_threat_id' not in st.session_state:
        st.session_state.selected_threat_id = threat_data['threat_id'].iloc[0]

    threat_id = st.selectbox("ID do Evento de Ameaça", threat_data['threat_id'],
                             index=threat_data['threat_id'].tolist().index(st.session_state.selected_threat_id))
    st.session_state.selected_threat_id = threat_id

    selected_event = threat_data[threat_data['threat_id'] == threat_id].iloc[0]
    threat_event = selected_event['threat_event']
    affected_asset = [asset.strip() for asset in selected_event['affected_asset'].split(', ') if
                      asset.strip() in available_assets]

    st.text_input("Evento de Ameaça", value=threat_event, disabled=True)
    new_affected_asset = st.multiselect("Ativo Afetado", options=available_assets, default=affected_asset)

    if st.button("Atualizar Evento"):
        update_threat_event(threat_id, threat_event, new_affected_asset)
        st.success("Evento atualizado com sucesso!")
        st.rerun()
