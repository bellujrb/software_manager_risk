import streamlit as st
import pandas as pd
import requests

def get_loss_high():
    url = 'http://3.142.77.137:8080/api/losshigh-granuled'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            # Converte a resposta JSON em um DataFrame e explodir a coluna 'Losses'
            df = pd.json_normalize(json_response['Response'], 'Losses', ['ThreatEventID', 'ThreatEvent', 'Assets'])
            return df
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de perdas: {response.status_code}')
    return pd.DataFrame()

def run():
    st.title('Granular')

    loss_data = get_loss_high()

    if loss_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    loss_data.rename(columns={
        'ThreatEventID': 'ID do Evento de Ameaça',
        'ThreatEvent': 'Evento de Ameaça',
        'Assets': 'Ativo(s)',
        'LossType': 'Tipo de Perda',
        'Impact': 'Impacto',
        'MinimumLoss': 'Perda Mínima',
        'MaximumLoss': 'Perda Máxima',
        'MostLikelyLoss': 'Perda Mais Provável'
    }, inplace=True)

    st.write("Selecione um evento de ameaça para visualizar as perdas:")

    unique_events = loss_data['Evento de Ameaça'].unique()

    for event in unique_events:
        with st.expander(event):
            event_df = loss_data[loss_data['Evento de Ameaça'] == event]

            granular_data = event_df[event_df['Tipo de Perda'] == 'Granular']
            non_granular_data = event_df[event_df['Tipo de Perda'] != 'Granular']

            display_df = pd.concat([non_granular_data, granular_data]).reset_index(drop=True)

            st.write(f"Tabela de Perdas para {event}:")
            st.dataframe(display_df)

run()
