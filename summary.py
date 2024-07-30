import streamlit as st
import pandas as pd


def get_summary():
    data = {
        'Nome da avaliação': ['0%'],
        'Ativo de informação': [0],
        'Evento de ameaça': ['N/A'],
        'VaR Inicial': ['N/A'],
        'VaR residual': ['N/A'],
        'Eficiência do Controle': ['0%'],
        'Custo do Controle': ['£0.00'],
        'Economia do Controle': ['£0.00'],
        'Retorno do Controle': ['O custo excede a economia']
    }
    df = pd.DataFrame(data)
    return df


def get_control_data():
    data = {
        "Control": ["Control A"],
        "Min (%)": [5],
        "Mode (%)": [10],
        "Max (%)": [15],
        "Average (%)": [12],
        "Comment": [""]
    }
    df = pd.DataFrame(data)
    return df


def run():
    st.title('Resumo dos Dados')

    # Primeiro DataFrame
    st.write("### Resumo da Avaliação")
    summary_data = get_summary()
    st.dataframe(summary_data, use_container_width=True,
                 height=200)  # Agora usando st.dataframe com parâmetros adequados

    # Segundo DataFrame
    st.write("### CONSOLIDATED CONTROL DATA")
    st.write("#### Effectiveness")
    control_data = get_control_data()
    st.dataframe(control_data, use_container_width=True, height=300)  # Igualmente para o segundo DataFrame
