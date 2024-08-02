import streamlit as st
import pandas as pd
import requests

def get_risk_data(loss_mode):
    url = 'http://3.142.77.137:8080/api/risk'
    headers = {'Loss': loss_mode}  # Configura o header com o tipo de perda selecionado
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            return pd.DataFrame(json_response['Response'])
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    elif response.status_code == 500:
        st.error('Erro 500: Problema no servidor. Por favor, selecione uma abordagem de perda ou reinicie a página e escolha a abordagem novamente.')
    else:
        st.error(f'Erro ao recuperar dados de riscos: {response.status_code}')
    return pd.DataFrame()

def format_as_currency(df, columns):
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')  # Convert to numeric, set errors to NaN
            df.loc[df['risk_type'] != 'Frequency', column] = df.loc[df['risk_type'] != 'Frequency', column].apply(
                lambda x: f'R${x:,.2f}' if pd.notnull(x) else 'NaN'
            )  # Format as currency if not NaN and risk_type is not Frequency
    return df

def display_risk_data():
    if 'loss_mode' in st.session_state:
        st.write(f"Modo de perda atual: {st.session_state['loss_mode']}")
        risk_data = get_risk_data(st.session_state['loss_mode'])
        if not risk_data.empty:
            columns_to_format = ['min', 'max', 'mode', 'estimate']  # Apenas as colunas 'min' e 'max'
            risk_data = format_as_currency(risk_data, columns_to_format)
            st.dataframe(risk_data)
        else:
            st.error('Não há dados de riscos disponíveis para a seleção atual. Por favor, selecione uma abordagem de perda ou reinicie a página e escolha a abordagem novamente.')
    else:
        st.error('Por favor, selecione um modo de perda na página anterior.')

def run():
    display_risk_data()

if __name__ == "__main__":
    run()
