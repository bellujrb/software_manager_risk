import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import lognorm

from data.risk_analysis_service import get_catalogues, fetch_event_data, fetch_aggregated_data, fetch_appetite_data

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
    values = np.array(values)
    if len(values) == 0 or np.any(np.isnan(values)):
        st.error("Os dados de simulação contêm valores inválidos.")
        return np.array([]), np.array([])
    freqs, edges = np.histogram(values, bins=bins)
    return freqs, edges


def plot_loss_exceedance_curve(appetite_data, monte_carlo_data):
    risks = [point['risk'] for point in appetite_data["LossExceedance"]]  # Corrigindo aqui
    losses = [point['loss'] / 1e6 for point in appetite_data["LossExceedance"]]

    no_of_bins = int(np.ceil(np.sqrt(sims)))
    freqs, edges = get_histogram_data(monte_carlo_data, no_of_bins)
    if len(freqs) == 0 or len(edges) == 0:
        st.error("Erro ao gerar dados do histograma.")
        return

    lec_x = edges[:-1] / 1e6
    lec_y = 100 - (np.cumsum(freqs) / sims * 100)  # Ajustando a probabilidade de excedência

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=losses, y=risks, mode='lines+markers', name='Apetite de Risco',
                             marker=dict(color='blue', size=5), line=dict(color='blue', width=2)))

    fig.add_trace(go.Scatter(x=lec_x, y=lec_y, mode='lines', name='Risco Agregado',
                             line=dict(color='red', width=2)))

    max_value = max(lec_x)
    tick_step = max_value / 5

    fig.update_layout(
        title='Curva de Excedência de Perda',
        xaxis_title='Perda (milhões)',
        yaxis_title='Probabilidade(%)',
        xaxis=dict(
            type='linear',
            tickmode='array',
            tickvals=[i for i in np.arange(0, max_value + tick_step, tick_step)]
        ),
        yaxis=dict(
            type='linear',
            tickmode='array',
            tickvals=list(range(0, 101, 10)),
            showgrid=True,
            gridcolor='gray'
        ),
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
                    'minfreq': float(aggregated_data['FrequencyMin']),
                    'pertfreq': float(aggregated_data['FrequencyEstimate']),
                    'maxfreq': float(aggregated_data['FrequencyMax']),
                    'minloss': float(aggregated_data['LossMin']),
                    'pertloss': float(aggregated_data['LossEstimate']),
                    'maxloss': float(aggregated_data['LossMax'])
                }
                sim_results = generate_sim_data(rdata)
                no_of_bins = int(np.ceil(np.sqrt(sims)))
                freqs, edges = get_histogram_data(sim_results, no_of_bins)
                if len(freqs) == 0 or len(edges) == 0:
                    st.error("Erro ao gerar dados do histograma.")
                    return
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
                'minfreq': float(appetite_data['FrequencyMin']),
                'pertfreq': float(appetite_data['FrequencyEstimate']),
                'maxfreq': float(appetite_data['FrequencyMax']),
                'minloss': float(appetite_data['LossMin']),
                'pertloss': float(appetite_data['LossEstimate']),
                'maxloss': float(appetite_data['LossMax'])
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
                if len(freqs) == 0 or len(edges) == 0:
                    st.error("Erro ao gerar dados do histograma.")
                    return
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
            "Falha ao carregar catálogos de eventos. Por favor, verifique a conectividade da API ou os parâmetros da "
            "requisição.")
