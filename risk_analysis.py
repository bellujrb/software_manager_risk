import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def generate_data(iterations):
    data = {
        'Evento de Ameaça': [
            'Ataque de Autenticação', 'Ataque de Autorização', 'Ataque de Comunicação',
            'Ataque de Negação de Serviço', 'Vazamento de Informações', 'Ataque de Malware',
            'Ataque de Má Configuração', 'Ataque de Mau Uso', 'Ataque Físico',
            'Atividades de Reconhecimento', 'Ataque de Engenharia Social', 'Exploração de Software',
            'Ataque à Cadeia de Suprimentos', 'Falha Humana', 'Falha de Processo', 'Falha Tecnológica',
            'Evento Meteorológico', 'Evento Hidrológico', 'Falha de Infraestrutura'
        ],
        'Média de Frequência': np.random.lognormal(mean=2, sigma=0.5, size=19),
        'Desvio Padrão de Frequência': np.random.uniform(0.1, 1.0, size=19),
        'Média de Perda': np.random.lognormal(mean=3, sigma=1, size=19),
        'Desvio Padrão de Perda': np.random.uniform(0.5, 2.0, size=19)
    }
    df = pd.DataFrame(data)
    risk_results = []

    for i in range(iterations):
        frequency_samples = np.random.lognormal(mean=np.log(df['Média de Frequência']),
                                                sigma=df['Desvio Padrão de Frequência'])
        loss_samples = np.random.lognormal(mean=np.log(df['Média de Perda']), sigma=df['Desvio Padrão de Perda'])
        risk_results.append(frequency_samples * loss_samples)

    risk_array = np.array(risk_results)
    df['Risco Médio'] = np.mean(risk_array, axis=0)
    df['Percentil 95 do Risco'] = np.percentile(risk_array, 95, axis=0)
    df['Value at Risk'] = np.percentile(risk_array, 99, axis=0)
    df['Erro'] = df['Percentil 95 do Risco'] - df['Risco Médio']

    return df, risk_array


def plot_risk_distribution(risk_array, event):
    plt.figure(figsize=(10, 6))
    plt.hist(risk_array, bins=50, alpha=0.75)
    plt.title(f'Distribuição do Risco para {event}')
    plt.xlabel('Risco')
    plt.ylabel('Frequência')
    st.pyplot(plt)


def plot_lec_curve(risk_array, event):
    sorted_risk = np.sort(risk_array)
    probability = np.arange(len(sorted_risk)) / float(len(sorted_risk))
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_risk, 1 - probability)
    plt.title(f'Curva LEC para {event}')
    plt.xlabel('Perda')
    plt.ylabel('Probabilidade de Excedência')
    st.pyplot(plt)


def run():
    st.title('Aplicativo de Análise de Risco Quantitativo')

    iterations = st.sidebar.number_input('Número de Simulações Monte Carlo', min_value=100, max_value=10000, value=1000,
                                         step=100)

    if st.sidebar.button('Executar Simulação') or 'df' not in st.session_state:
        df, risk_array = generate_data(iterations)
        st.session_state.df = df
        st.session_state.risk_array = risk_array

    st.subheader('Resultados da Análise de Risco')
    st.dataframe(
        st.session_state.df[['Evento de Ameaça', 'Risco Médio', 'Percentil 95 do Risco', 'Value at Risk', 'Erro']])

    event_choice = st.selectbox('Selecione um Evento de Ameaça para Visualizar Gráficos:',
                                st.session_state.df['Evento de Ameaça'])

    if st.button('Mostrar Distribuição do Risco'):
        index_selected = st.session_state.df[st.session_state.df['Evento de Ameaça'] == event_choice].index[0]
        event_risk_array = st.session_state.risk_array[:, index_selected]
        plot_risk_distribution(event_risk_array, event_choice)

    if st.button('Mostrar Curva LEC'):
        index_selected = st.session_state.df[st.session_state.df['Evento de Ameaça'] == event_choice].index[0]
        event_risk_array = st.session_state.risk_array[:, index_selected]
        plot_lec_curve(event_risk_array, event_choice)
