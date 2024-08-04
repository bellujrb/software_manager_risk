import streamlit as st
import pandas as pd
import requests

from data.link_threat_service import get_threat_events, get_available_assets, update_threat_event


def run():
    st.title('Vinculação de ativos de eventos de ameaça')

    threat_data = get_threat_events()
    available_assets = get_available_assets()

    if threat_data.empty:
        st.error('Nenhum dado de evento de ameaça disponível.')
    else:
        st.write("Eventos de ameaça:")
        st.dataframe(threat_data[['threat_id', 'threat_event', 'affected_asset']])

        st.write("Atualizar Evento de Ameaça")

        # Select box for threat_id
        threat_id = st.selectbox("Threat Event ID", threat_data['threat_id'])

        # Automatically fill threat_event based on selected threat_id
        selected_event = threat_data[threat_data['threat_id'] == threat_id].iloc[0]
        threat_event = selected_event['threat_event']
        affected_asset = [asset.strip() for asset in selected_event['affected_asset'].split(', ') if
                          asset.strip() in available_assets]

        st.text_input("Threat Event", value=threat_event, disabled=True)
        new_affected_asset = st.multiselect("Affected Asset", options=available_assets, default=affected_asset)

        if st.button("Atualizar Evento"):
            update_threat_event(threat_id, threat_event, new_affected_asset)
