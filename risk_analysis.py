import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
from scipy.stats import lognorm
import pandas as pd

sims = 10000
STDEV = 3.29


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


def fetch_event_data(event_name, loss_type):
    url = f'http://3.142.77.137:8080/simulation'
    headers = {
        'Content-Type': 'application/json',
        'ThreatEvent': event_name,
        'Loss': loss_type  # Aqui você adiciona o tipo de perda no cabeçalho
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data:
            json_data['FrequencyMin'] = int(float(json_data['FrequencyMin']))
            json_data['FrequencyEstimate'] = int(float(json_data['FrequencyEstimate']))
            json_data['FrequencyMax'] = int(float(json_data['FrequencyMax']))
            json_data['LossMin'] = int(float(json_data['LossMin']))
            json_data['LossEstimate'] = int(float(json_data['LossEstimate']))
            json_data['LossMax'] = int(float(json_data['LossMax']))
        return json_data
    else:
        st.error('Falha ao recuperar dados do evento.')
        return None


def fetch_aggregated_data(loss_type):
    headers = {
        'Content-Type': 'application/json',
        'Loss': loss_type  # Aqui você adiciona o tipo de perda no cabeçalho
    }
    response = requests.get("http://3.142.77.137:8080/simulation-aggregated", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados agregados: {response.status_code}")
        return None


def fetch_appetite_data(loss_type):
    url = "http://3.142.77.137:8080/simulation-appetite"
    response = requests.get(url, headers={
        'accept': 'application/json',
        'Loss': loss_type
    })
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados de apetite: {response.status_code}")
        return None


def plot_loss_exceedance_curve(appetite_data, monte_carlo_data):
    risks = [100 - float(point['risk'].strip('%')) for point in appetite_data["LossExceedance"]]
    losses = [point['loss'] / 1e6 for point in appetite_data["LossExceedance"]]

    no_of_bins = int(np.ceil(np.sqrt(sims)))
    freqs, edges = get_histogram_data(monte_carlo_data, no_of_bins)
    lec_x = edges[:-1] / 1e6
    lec_y = (100 - (np.cumsum(freqs) / sims * 100))

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=losses, y=risks, mode='lines+markers', name='Apetite de Risco',
                             marker=dict(color='blue', size=5), line=dict(color='blue', width=2)))

    fig.add_trace(go.Scatter(x=lec_x, y=lec_y, mode='lines', name='Risco Agregado',
                             line=dict(color='red', width=2)))

    fig.update_layout(
        title='Curva de Excedência de Perda',
        xaxis_title='Perda (milhões)',
        yaxis_title='Probabilidade(%)',
        xaxis=dict(type='linear', tickmode='array', tickvals=list(range(0, int(max(lec_x)) + 2, 2))),
        yaxis=dict(tickmode='array', tickvals=[i for i in range(0, 101, 10)],
                   showgrid=True, gridcolor='gray'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='black'),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='black')
    )
    st.plotly_chart(fig)


def run():
    st.title("Análise de Risco")

    chart_type = st.selectbox("Selecione o tipo de gráfico:", ["Histograma Agregado", "Curva de Excedência de Perda"])

    if chart_type == "Histograma Agregado":
        if st.button("Gerar Dados"):
            aggregated_data = fetch_aggregated_data(loss_type="Granular")
            if aggregated_data:
                rdata = {
                    'minfreq': 1,
                    'pertfreq': 1.5,
                    'maxfreq': 2,
                    'minloss': aggregated_data['LossMin'],
                    'pertloss': aggregated_data['LossEstimate'],
                    'maxloss': aggregated_data['LossMax']
                }
                sim_results = generate_sim_data(rdata)
                no_of_bins = int(np.ceil(np.sqrt(sims)))
                freqs, edges = get_histogram_data(sim_results, no_of_bins)
                bins = edges[:-1]

                fig1 = go.Figure()
                fig1.add_trace(go.Bar(x=bins, y=freqs, name='Histograma'))
                fig1.add_trace(
                    go.Scatter(x=bins, y=np.cumsum(freqs) / sum(freqs), name='Pareto', mode='lines+markers',
                               yaxis='y2'))
                fig1.update_layout(title='Histograma de Riscos Agregados com Linha de Pareto',
                                   xaxis_title='Perda', yaxis_title='Frequência',
                                   yaxis2=dict(overlaying='y', side='right', title='Frequência Acumulada'))

                st.plotly_chart(fig1)

    elif chart_type == "Curva de Excedência de Perda":
        appetite_data = fetch_appetite_data(loss_type="Granular")
        if appetite_data and "LossExceedance" in appetite_data:
            rdata = {
                'minfreq': 1,
                'pertfreq': 1.5,
                'maxfreq': 2,
                'minloss': appetite_data['LossMin'],
                'pertloss': appetite_data['LossEstimate'],
                'maxloss': appetite_data['LossMax']
            }
            monte_carlo_data = generate_sim_data(rdata)
            plot_loss_exceedance_curve(appetite_data, monte_carlo_data)

    df_catalogues = get_catalogues()
    if not df_catalogues.empty:
        events = df_catalogues['ThreatEvent'].tolist()
        selected_event = st.selectbox("Selecione o Evento de Ameaça", options=events)

        if st.button("Carregar Dados do Evento e Simular Riscos"):
            event_data = fetch_event_data(selected_event, "Granular")
            if event_data:
                rdata = {
                    'minfreq': float(event_data['FrequencyMin']),
                    'pertfreq': float(event_data['FrequencyEstimate']),
                    'maxfreq': float(event_data['FrequencyMax']),
                    'minloss': float(event_data['LossMin']),
                    'pertloss': float(event_data['LossEstimate']),
                    'maxloss': float(event_data['LossMax'])
                }
                sim_results = generate_sim_data(rdata)
                no_of_bins = int(np.ceil(np.sqrt(sims)))
                freqs, edges = get_histogram_data(sim_results, no_of_bins)
                bins = edges[:-1]

                fig1 = go.Figure()
                fig1.add_trace(go.Bar(x=bins, y=freqs, name='Histograma'))
                fig1.add_trace(go.Scatter(x=bins, y=np.cumsum(freqs) / sum(freqs), name='Pareto', mode='lines+markers',
                                          yaxis='y2'))
                fig1.update_layout(title='Histograma de Riscos Agregados com Linha de Pareto',
                                   xaxis_title='Perda', yaxis_title='Frequência',
                                   yaxis2=dict(overlaying='y', side='right', title='Frequência Acumulada'))

                st.plotly_chart(fig1)

    else:
        st.error(
            "Falha ao carregar catálogos de eventos. Por favor, verifique a conectividade da API ou os parâmetros da requisição.")
