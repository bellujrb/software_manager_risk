import streamlit as st
import pandas as pd
import requests

API_BASE_URL = "http://3.142.77.137:8080"  # Replace with your actual API base URL


def get_threat_events():
    url = f"{API_BASE_URL}/api/all-event"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()  # Assuming the response is in JSON format

        # Adjust DataFrame creation based on the actual structure
        if 'Response' in data:
            df = pd.DataFrame(data['Response'])
            if 'affected_asset' in df.columns:
                df['affected_asset'] = df['affected_asset'].apply(lambda x: ', '.join(filter(None, x)))
            return df
        else:
            st.error("Unexpected JSON structure. 'Response' key not found.")
            return pd.DataFrame()  # Return an empty DataFrame on unexpected structure
    except requests.RequestException as e:
        st.error(f"Failed to fetch data from the API: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error


def get_available_assets():
    url = f"{API_BASE_URL}/api/assets"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()  # Assuming the response is in JSON format

        # Extract the list of asset names
        if 'Response' in data:
            asset_names = [asset['name'] for asset in data['Response']]
            return asset_names
        else:
            st.error("Unexpected JSON structure.")
            return []
    except requests.RequestException as e:
        st.error(f"Failed to fetch assets from the API: {e}")
        return []  # Return an empty list on error


def update_threat_event(threat_id, threat_event, affected_asset):
    url = f"{API_BASE_URL}/api/event/{threat_id}"
    payload = {
        "threat_event": threat_event,
        "affected_asset": affected_asset
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        st.success(f"Successfully updated threat event with ID {threat_id}")
    except requests.RequestException as e:
        st.error(f"Failed to update threat event: {e}")


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
