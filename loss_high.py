import streamlit as st
import pandas as pd
import requests
import locale

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

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

def run():
    st.title('Perda Alta')

    loss_data = get_loss_high()

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

    # Formatar os valores monetários no DataFrame para exibição
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

if __name__ == "__main__":
    run()
