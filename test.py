import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
from scipy.stats import lognorm
import pandas as pd

# Constantes
sims = 10000
STDEV = 3.29

# Funções de Utilidade
def lognorminvpert(min_val, pert, max_val):
    mean = np.log(pert)
    sigma = (np.log(max_val) - np.log(min_val)) / STDEV
    return lognorm.ppf(np.random.rand(), s=sigma, scale=np.exp(mean))

def lognorm_risk_pert(minfreq, pertfreq, maxfreq, minloss, pertloss, maxloss):
    freq = lognorminvpert(minfreq, pertfreq, maxfreq)
    loss = lognorminvpert(minloss, pertloss, maxloss)
    return freq * loss

def generate_sim_data(rdata):
    sim_data = np.zeros(sims)
    for sim_ctr in range(sims):
        sim_data[sim_ctr] = lognorm_risk_pert(
            rdata['minfreq'], rdata['pertfreq'], rdata['maxfreq'],
            rdata['minloss'], rdata['pertloss'], rdata['maxloss']
        )
    return sim_data

def get_histogram_data(values, bins):
    freqs, edges = np.histogram(values, bins=bins)
    return freqs, edges

def get_lecs(freqs, edges):
    cumulative_freqs = np.cumsum(freqs)
    lecs = (len(freqs) - cumulative_freqs + freqs) / len(freqs)
    return edges[:-1], lecs

def get_catalogues():
    url = 'http://3.142.77.137:8080/api/all-catalogue'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            return df.fillna("")
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar catálogos: {response.status_code}')
    return pd.DataFrame()

def fetch_event_data(event_name):
    url = f'http://3.142.77.137:8080/simulation'
    headers = {'Content-Type': 'application/json', 'ThreatEvent': event_name}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        st.error('Falha ao recuperar dados do evento.')
        return None

def run():
    st.title("Análise de Risco")

    # Carregar catálogos de eventos
    df_catalogues = get_catalogues()
    if not df_catalogues.empty:
        events = df_catalogues['ThreatEvent'].tolist()
        selected_event = st.selectbox("Selecione o Evento de Ameaça", options=events)

        if st.button("Carregar Dados do Evento"):
            event_data = fetch_event_data(selected_event)
            if event_data:
                st.session_state.minfreq = float(event_data['FrequencyMin'])
                st.session_state.pertfreq = float(event_data['FrequencyEstimate'])
                st.session_state.maxfreq = float(event_data['FrequencyMax'])
                st.session_state.minloss = float(event_data['LossMin'])
                st.session_state.pertloss = float(event_data['LossEstimate'])
                st.session_state.maxloss = float(event_data['LossMax'])

    if 'minfreq' in st.session_state:
        minfreq = st.number_input("Frequência mínima", value=st.session_state.minfreq, format="%.2f")
        pertfreq = st.number_input("Frequência perturbativa", value=st.session_state.pertfreq, format="%.2f")
        maxfreq = st.number_input("Frequência máxima", value=st.session_state.maxfreq, format="%.2f")
        minloss = st.number_input("Perda mínima", value=st.session_state.minloss, format="%.2f")
        pertloss = st.number_input("Perda perturbativa", value=st.session_state.pertloss, format="%.2f")
        maxloss = st.number_input("Perda máxima", value=st.session_state.maxloss, format="%.2f")

        rdata = {'minfreq': minfreq, 'pertfreq': pertfreq, 'maxfreq': maxfreq,
                 'minloss': minloss, 'pertloss': pertloss, 'maxloss': maxloss}

        if st.button("Gerar Análise de Risco"):
            sim_results = generate_sim_data(rdata)

            # Verifique se há valores NaN ou infinitos em sim_results
            if np.any(np.isnan(sim_results)) or np.any(np.isinf(sim_results)):
                st.error("Os dados de simulação contêm valores inválidos (NaN ou infinito).")
            else:
                no_of_bins = int(np.ceil(np.sqrt(sims)))
                freqs, edges = get_histogram_data(sim_results, no_of_bins)
                bins = edges[:-1]

                # Histograma com linha de Pareto
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(x=bins, y=freqs, name='Histograma'))
                fig1.add_trace(go.Scatter(x=bins, y=np.cumsum(freqs) / sum(freqs), name='Pareto', mode='lines+markers', yaxis='y2'))
                fig1.update_layout(title='Histograma de Riscos Agregados com Linha de Pareto',
                                   xaxis_title='Perda', yaxis_title='Frequência',
                                   yaxis2=dict(overlaying='y', side='right', title='Frequência Acumulada'))

                # Curva de Excedência de Perda (LEC)
                lec_x, lec_y = get_lecs(freqs, edges)
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=lec_x, y=lec_y, mode='lines+markers', name='LEC'))
                fig2.update_layout(title='Curva de Excedência de Perda (LEC)',
                                   xaxis_title='Perda', yaxis_title='Probabilidade de Excedência')

                st.plotly_chart(fig1)
                st.plotly_chart(fig2)
