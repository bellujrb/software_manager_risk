import streamlit as st
import pandas as pd
import requests

from data.risk_calculation_service import get_risk_data


def format_as_currency(value, risk_type):
    if pd.notnull(value) and risk_type != 'Frequency':
        return f'R${value:,.2f}'
    return value


def display_risk_data():
    if 'loss_mode' in st.session_state:
        st.write(f"Modo de perda atual: {st.session_state['loss_mode']}")
        risk_data = get_risk_data(st.session_state['loss_mode'])
        if not risk_data.empty:
            columns_to_format = ['min', 'max', 'mode', 'estimate']

            # Converter colunas para numérico
            for column in columns_to_format:
                if column in risk_data.columns:
                    risk_data[column] = pd.to_numeric(risk_data[column], errors='coerce')  # Converter para numérico

            # Aplicar a formatação condicionalmente usando applymap com lambda
            for column in columns_to_format:
                if column in risk_data.columns:
                    risk_data[column] = risk_data.apply(
                        lambda row: format_as_currency(row[column], row['risk_type']),
                        axis=1
                    )

            st.dataframe(risk_data)
        else:
            st.error(
                'Não há dados de riscos disponíveis para a seleção atual. Por favor, selecione uma abordagem de perda '
                'ou reinicie a página e escolha a abordagem novamente.'
            )
    else:
        st.error('Por favor, selecione um modo de perda na página anterior.')


def run():
    display_risk_data()


if __name__ == "__main__":
    run()
