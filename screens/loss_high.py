import streamlit as st
import pandas as pd
import requests
import locale


def get_loss_high():
    url = 'http://3.142.77.137:8080/api/losshigh'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção para respostas com erro (4xx e 5xx)
        json_response = response.json()

        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            if 'losses' in df.columns:
                df = df.explode('losses').reset_index(drop=True)
                losses_df = df['losses'].apply(pd.Series)
                df = pd.concat([df.drop(columns=['losses']), losses_df], axis=1)
                return df
            else:
                st.error('Chave "losses" não encontrada nos dados da resposta.')
                return pd.DataFrame()
        else:
            st.error('Recebido JSON vazio ou sem chave "Response".')
            return pd.DataFrame()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'Erro HTTP ao recuperar dados de perdas: {http_err}')
        return pd.DataFrame()
    except Exception as err:
        st.error(f'Erro ao recuperar dados de perdas: {err}')
        return pd.DataFrame()


def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except:
        return value


def update_loss_high(event_id, assets, loss_type, max_loss, min_loss, most_likely_loss, threat_event):
    url = f'http://3.142.77.137:8080/api/update-losshigh/{event_id}'
    payload = {
        "assets": [assets],  # Enviar como lista
        "loss_type": loss_type,
        "maximum_loss": max_loss,
        "minimum_loss": min_loss,
        "most_likely_loss": most_likely_loss,
        "threat_event": threat_event
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'Erro HTTP ao atualizar dados de perdas: {http_err}')
        return None
    except Exception as err:
        st.error(f'Erro ao atualizar dados de perdas: {err}')
        return None


def run():
    st.title('Perda Alta')

    if 'loss_data' not in st.session_state:
        st.session_state.loss_data = get_loss_high()

    loss_data = st.session_state.loss_data

    if loss_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    loss_data.rename(columns={
        'threat_event_id': 'ID do Evento de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'assets': 'Ativo(s)',
        'loss_type': 'Tipo de Perda',
        'minimum_loss': 'Perda Mínima',
        'maximum_loss': 'Perda Máxima',
        'most_likely_loss': 'Perda Mais Provável'
    }, inplace=True)

    loss_data['Perda Mínima'] = loss_data['Perda Mínima'].apply(format_currency)
    loss_data['Perda Máxima'] = loss_data['Perda Máxima'].apply(format_currency)
    loss_data['Perda Mais Provável'] = loss_data['Perda Mais Provável'].apply(format_currency)

    st.write("Selecione uma categoria para visualizar os ataques:")

    unique_events = loss_data['Evento de Ameaça'].unique()

    for event in unique_events:
        with st.expander(event):
            event_df = loss_data[loss_data['Evento de Ameaça'] == event]
            st.write(f"Tabela de Perdas para {event}:")
            st.dataframe(event_df)

            st.write("Atualizar Perdas:")
            threat_event_id = event_df['ID do Evento de Ameaça'].iloc[0]
            assets = event_df['Ativo(s)'].iloc[0]
            threat_event = event_df['Evento de Ameaça'].iloc[0]
            loss_type = st.selectbox('Tipo de Perda', options=['Direct', 'Indirect'], key=f'{event}_loss_type')

            selected_loss = event_df[event_df['Tipo de Perda'] == loss_type]

            if not selected_loss.empty:
                max_loss = selected_loss['Perda Máxima'].iloc[0]
                min_loss = selected_loss['Perda Mínima'].iloc[0]
                most_likely_loss = selected_loss['Perda Mais Provável'].iloc[0]
            else:
                max_loss = 0.0
                min_loss = 0.0
                most_likely_loss = 0.0

            st.text_input("Ativo(s)", value=assets, disabled=True, key=f'assets_{event}')
            max_loss_input = st.number_input('Perda Máxima', min_value=0.0, value=float(max_loss),
                                             key=f'max_loss_{event}')
            min_loss_input = st.number_input('Perda Mínima', min_value=0.0, value=float(min_loss),
                                             key=f'min_loss_{event}')
            most_likely_loss_input = st.number_input('Perda Mais Provável', min_value=0.0,
                                                     value=float(most_likely_loss), key=f'most_likely_loss_{event}')

            update_button = st.button('Atualizar', key=f'update_button_{event}')

            if update_button:
                st.write(f'Atualizando dados para o evento {threat_event_id}:')
                st.write({
                    "assets": [assets],  # Enviar como lista
                    "loss_type": loss_type,
                    "maximum_loss": max_loss_input,
                    "minimum_loss": min_loss_input,
                    "most_likely_loss": most_likely_loss_input,
                    "threat_event": threat_event
                })
                response = update_loss_high(threat_event_id, assets, loss_type, max_loss_input, min_loss_input,
                                            most_likely_loss_input, threat_event)
                if response:
                    st.success('Dados de perda atualizados com sucesso!')
                    st.session_state.loss_data = get_loss_high()
