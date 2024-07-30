import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import lognorm

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
            rdata['FrequencyMin'], rdata['FrequencyEstimate'], rdata['FrequencyMax'],
            rdata['LossMin'], rdata['LossEstimate'], rdata['LossMax']
        )
    return sim_data


def get_histogram_data(values, bins):
    freqs, edges = np.histogram(values, bins=bins)
    return freqs, edges


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


def fetch_aggregated_data():
    url = "http://3.142.77.137:8080/simulation-aggregated"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados agregados: {response.status_code}")
        return None


def fetch_appetite_data():
    url = "http://3.142.77.137:8080/simulation-appetite"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro ao buscar dados de apetite: {response.status_code}")
        return None


def fetch_strength_data():
    url = "http://3.142.77.137:8080/api/all-strength"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()["Response"]
    else:
        st.error(f"Erro ao buscar dados da API: {response.status_code}")
        return []


def safe_float_conversion(value, default=1.0):
    try:
        return float(value.strip('%')) / 100
    except (ValueError, AttributeError):
        return default


def calculate_inherent_risk(monte_carlo_data, control_gap):
    control_gap = safe_float_conversion(control_gap)
    return monte_carlo_data / control_gap


def calculate_residual_risk(inherent_risk, proposed_control_gap):
    proposed_control_gap = safe_float_conversion(proposed_control_gap)
    return inherent_risk / proposed_control_gap


def plot_loss_exceedance_curve(appetite_data, monte_carlo_data, residual_risk):
    risks = [100 - float(point['risk'].strip('%')) for point in appetite_data["LossExceedance"]]
    losses = [point['loss'] / 1e6 for point in appetite_data["LossExceedance"]]

    no_of_bins = int(np.ceil(np.sqrt(sims)))
    freqs, edges = get_histogram_data(monte_carlo_data, no_of_bins)
    lec_x = edges[:-1] / 1e6
    lec_y = (100 - (np.cumsum(freqs) / sims * 100))

    freqs_residual, edges_residual = get_histogram_data(residual_risk, no_of_bins)
    lec_x_residual = edges_residual[:-1] / 1e6
    lec_y_residual = (100 - (np.cumsum(freqs_residual) / sims * 100))

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=losses, y=risks, mode='lines+markers', name='Risk Appetite', line=dict(color='blue')))

    fig.add_trace(go.Scatter(x=lec_x, y=lec_y, mode='lines', name='Aggregated Risk', line=dict(color='red')))

    fig.add_trace(
        go.Scatter(x=lec_x_residual, y=lec_y_residual, mode='lines', name='Modelled Risk', line=dict(color='white')))

    fig.update_layout(
        title='Loss Exceedance Curve',
        xaxis_title='Loss (millions)',
        yaxis_title='Probability (%)',
        xaxis=dict(tickmode='array', tickvals=np.arange(0, max(lec_x), step=10), range=[0, max(lec_x)]),
        yaxis=dict(tickmode='array', tickvals=np.arange(0, 101, step=10), range=[0, 100]),
        legend=dict(x=0.01, y=0.99, borderwidth=1),
        plot_bgcolor='rgb(17,17,17)',
        paper_bgcolor='rgb(17,17,17)',
        font=dict(color='white')
    )

    st.plotly_chart(fig)


def plot_simulation_lines(sim_results1, sim_results2, title):
    freqs1, edges1 = get_histogram_data(sim_results1, bins=50)
    freqs2, edges2 = get_histogram_data(sim_results2, bins=50)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edges1[:-1], y=freqs1, mode='lines', name='Aggregated Risk', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=edges2[:-1], y=freqs2, mode='lines', name='Modelled Risk', line=dict(color='white')))

    fig.update_layout(
        title=title,
        xaxis_title='Loss',
        yaxis_title='Count of Simulations',
        plot_bgcolor='rgb(17,17,17)',
        paper_bgcolor='rgb(17,17,17)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray')
    )

    st.plotly_chart(fig)


def run():
    st.title("Relatorio")

    chart_type = st.selectbox("Selecione o tipo de gráfico:", ["KDE Plot Agregado", "Curva de Excedência de Perda"])

    if chart_type == "KDE Plot Agregado":
        if st.button("Gerar Dados"):
            aggregated_data = fetch_aggregated_data()
            if aggregated_data:
                rdata = {
                    'FrequencyMin': 1,
                    'FrequencyEstimate': 1.5,
                    'FrequencyMax': 2,
                    'LossMin': aggregated_data['LossMin'],
                    'LossEstimate': aggregated_data['LossEstimate'],
                    'LossMax': aggregated_data['LossMax']
                }
                sim_results = generate_sim_data(rdata)

                # Buscar control gap e proposed control gap
                strength_data = fetch_strength_data()
                control_gap = pd.DataFrame(strength_data).query('controlId == -2')['controlGap'].values[0]
                proposed_control_gap = pd.DataFrame(strength_data).query('controlId == -1')['controlGap'].values[0]

                inherent_risk = calculate_inherent_risk(sim_results, control_gap)
                residual_risk = calculate_residual_risk(inherent_risk, proposed_control_gap)

                plot_simulation_lines(sim_results, residual_risk, "Modelled Risk")

    elif chart_type == "Curva de Excedência de Perda":
        appetite_data = fetch_appetite_data()
        if appetite_data and "LossExceedance" in appetite_data:
            rdata = {
                'FrequencyMin': appetite_data['FrequencyMin'],
                'FrequencyEstimate': appetite_data['FrequencyEstimate'],
                'FrequencyMax': appetite_data['FrequencyMax'],
                'LossMin': appetite_data['LossMin'],
                'LossEstimate': appetite_data['LossEstimate'],
                'LossMax': appetite_data['LossMax']
            }
            monte_carlo_data = generate_sim_data(rdata)

            strength_data = fetch_strength_data()
            control_gap = pd.DataFrame(strength_data).query('controlId == -2')['controlGap'].values[0]
            proposed_control_gap = pd.DataFrame(strength_data).query('controlId == -1')['controlGap'].values[0]

            inherent_risk = calculate_inherent_risk(monte_carlo_data, control_gap)
            residual_risk = calculate_residual_risk(inherent_risk, proposed_control_gap)

            plot_loss_exceedance_curve(appetite_data, monte_carlo_data, residual_risk)

    df_catalogues = get_catalogues()
    if not df_catalogues.empty:
        events = df_catalogues['ThreatEvent'].tolist()
        selected_event = st.selectbox("Selecione o Evento de Ameaça", options=events)

        if st.button("Carregar Dados do Evento e Simular Riscos"):
            event_data = fetch_event_data(selected_event)
            if event_data:
                rdata1 = {
                    'FrequencyMin': float(event_data['FrequencyMin']),
                    'FrequencyEstimate': float(event_data['FrequencyEstimate']),
                    'FrequencyMax': float(event_data['FrequencyMax']),
                    'LossMin': float(event_data['LossMin']),
                    'LossEstimate': float(event_data['LossEstimate']),
                    'LossMax': float(event_data['LossMax'])
                }
                sim_results1 = generate_sim_data(rdata1)

                rdata2 = {
                    'FrequencyMin': float(event_data['FrequencyMin']) * 0.8,
                    'FrequencyEstimate': float(event_data['FrequencyEstimate']) * 0.8,
                    'FrequencyMax': float(event_data['FrequencyMax']) * 0.8,
                    'LossMin': float(event_data['LossMin']) * 0.8,
                    'LossEstimate': float(event_data['LossEstimate']) * 0.8,
                    'LossMax': float(event_data['LossMax']) * 0.8
                }
                sim_results2 = generate_sim_data(rdata2)

                plot_simulation_lines(sim_results1, sim_results2, "Simulation Results for " + selected_event)

    else:
        st.error(
            "Falha ao carregar catálogos de eventos. Por favor, verifique a conectividade da API ou os parâmetros da requisição.")
