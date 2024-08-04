import streamlit as st
import pandas as pd
import requests

from config.settings import BASE_API_URL


def get_threat_events():
    url = f"{BASE_API_URL}api/all-event"
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
    url = f"{BASE_API_URL}api/assets"
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
    url = f"{BASE_API_URL}api/event/{threat_id}"
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
