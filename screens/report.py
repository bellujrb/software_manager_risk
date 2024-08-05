import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import lognorm

from data.report_service import fetch_event_data, fetch_aggregated_data, fetch_appetite_data, fetch_strength_data, get_catalogues

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
    try:
        risks = [float(str(point['risk']).strip('%')) for point in appetite_data["LossExceedance"]]
        losses = [point['loss'] / 1e6 for point in appetite_data["LossExceedance"]]

        sims = len(monte_carlo_data)
        no_of_bins = int(np.ceil(np.sqrt(sims)))
        freqs, edges = get_histogram_data(monte_carlo_data, no_of_bins)
        lec_x = edges[:-1] / 1e6
        lec_y = (100 - (np.cumsum(freqs) / sims * 100))

        freqs_residual, edges_residual = get_histogram_data(residual_risk, no_of_bins)
        lec_x_residual = edges_residual[:-1] / 1e6
        lec_y_residual = (100 - (np.cumsum(freqs_residual) / sims * 100))

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=losses, y=risks, mode='lines+markers', name='Apetite de Risco', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=lec_x, y=lec_y, mode='lines', name='Risco Agregado', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=lec_x_residual, y=lec_y_residual, mode='lines', name='Risco Modelado',
                                 line=dict(color='green')))

        max_value = max(max(lec_x), max(lec_x_residual), max(losses))
        tick_step = round(max_value / 5, 2)

        fig.update_layout(
            title='Curva de Excedência de Perdas',
            xaxis_title='Perda (milhões)',
            yaxis_title='Probabilidade (%)',
            xaxis=dict(
                tickmode='array',
                tickvals=np.arange(0, max_value + tick_step, tick_step),
                tickformat=".2f"
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=np.arange(0, 101, step=10),
                range=[0, 100]
            ),
            legend=dict(x=0.01, y=0.99, borderwidth=1),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black')
        )

        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar o gráfico: {e}")


def plot_simulation_lines(sim_results1, sim_results2, title):
    freqs1, edges1 = get_histogram_data(sim_results1, bins=50)
    freqs2, edges2 = get_histogram_data(sim_results2, bins=50)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edges1[:-1], y=freqs1, mode='lines', name='Risco Agregado', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=edges2[:-1], y=freqs2, mode='lines', name='Risco Modelado', line=dict(color='green')))

    fig.update_layout(
        title=title,
        xaxis_title='Perda',
        yaxis_title='Contagem de Simulações',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray')
    )

    st.plotly_chart(fig)


def run():
    st.title("Relatório")

    chart_type = st.selectbox("Selecione o tipo de gráfico:", ["KDE Plot Agregado", "Curva de Excedência de Perda"])

    if chart_type == "KDE Plot Agregado":
        if st.button("Gerar Dados"):
            aggregated_data = fetch_aggregated_data(loss_type="Granular")
            if aggregated_data:
                rdata = {
                    'FrequencyMin': float(aggregated_data['FrequencyMin']),
                    'FrequencyEstimate': float(aggregated_data['FrequencyEstimate']),
                    'FrequencyMax': float(aggregated_data['FrequencyMax']),
                    'LossMin': float(aggregated_data['LossMin']),
                    'LossEstimate': float(aggregated_data['LossEstimate']),
                    'LossMax': float(aggregated_data['LossMax'])
                }
                sim_results = generate_sim_data(rdata)

                strength_data = fetch_strength_data()
                control_gap = pd.DataFrame(strength_data).query('controlId == -2')['controlGap'].values[0]
                proposed_control_gap = pd.DataFrame(strength_data).query('controlId == -1')['controlGap'].values[0]

                inherent_risk = calculate_inherent_risk(sim_results, control_gap)
                residual_risk = calculate_residual_risk(inherent_risk, proposed_control_gap)

                plot_simulation_lines(sim_results, residual_risk, "KDE Plot Agregado")

    elif chart_type == "Curva de Excedência de Perda":
        appetite_data = fetch_appetite_data(loss_type="Granular")
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
            event_data = fetch_event_data(selected_event, loss_type="Granular")
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

                plot_simulation_lines(sim_results1, sim_results2, selected_event)

    else:
        st.error(
            "Falha ao carregar catálogos de eventos. Por favor, verifique a conectividade da API ou os parâmetros da "
            "requisição.")

