import streamlit as st
import pandas as pd
import requests

from data.risk_calculation_service import get_risk_data


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
            st.error(
                'Não há dados de riscos disponíveis para a seleção atual. Por favor, selecione uma abordagem de perda '
                'ou reinicie a página e escolha a abordagem novamente.')
    else:
        st.error('Por favor, selecione um modo de perda na página anterior.')


def run():
    display_risk_data()


if __name__ == "__main__":
    run()
