import streamlit as st
import pandas as pd
import requests

def get_loss_high():
    url = 'http://3.142.77.137:8080/api/losshigh-singular'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
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

def run():
    st.title('Estimado Unico')

    if 'loss_data' not in st.session_state:
        st.session_state.loss_data = get_loss_high()

    if st.session_state.loss_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    df = st.session_state.loss_data

    df.rename(columns={
        'threat_event_id': 'ID do Evento de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'assets': 'Ativo(s)',
        'minimum_loss': 'Perda Mínima',
        'maximum_loss': 'Perda Máxima',
        'most_likely_loss': 'Perda Mais Provável'
    }, inplace=True)

    st.write("Tabela de Perdas:")
    st.dataframe(df)

if __name__ == '__main__':
    run()
