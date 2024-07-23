import streamlit as st
import pandas as pd
import requests

def get_loss_high():
    url = 'http://3.142.77.137:8080/api/losshigh'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            return pd.DataFrame(json_response['Response']).explode('losses').reset_index(drop=True)
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de perdas: {response.status_code}')
    return pd.DataFrame()

def run():
    st.title('Loss-High')

    if 'loss_data' not in st.session_state:
        st.session_state.loss_data = get_loss_high()

    if st.session_state.loss_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    df = st.session_state.loss_data

    # Expandir a coluna 'losses' em múltiplas colunas
    losses_df = df['losses'].apply(pd.Series)
    df = pd.concat([df.drop(columns=['losses']), losses_df], axis=1)

    df.rename(columns={
        'threat_event_id': 'Threat Event ID',
        'threat_event': 'Threat Event',
        'assets': 'Assets(s)',
        'loss_type': 'Loss Type',
        'minimum_loss': 'Minimum Loss',
        'maximum_loss': 'Maximum Loss',
        'most_likely_loss': 'Most Likely Loss'
    }, inplace=True)

    st.write("Tabela de Perdas:")
    st.dataframe(df)