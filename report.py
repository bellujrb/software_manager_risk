import streamlit as st
import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

def calculate_inherent_risk(monte_carlo_data, control_gap):
    return monte_carlo_data / control_gap

def calculate_residual_risk(inherent_risk, proposed_control_gap):
    return inherent_risk / proposed_control_gap

def plot_loss_exceedance_curve(appetite_data, monte_carlo_data, residual_risk):
    # Convertendo dados de apetite de risco para listas
    risks = [100 - float(point['risk'].strip('%')) for point in appetite_data["LossExceedance"]]
    losses = [point['loss'] / 1e6 for point in appetite_data["LossExceedance"]]  # Convertendo para milhões

    # Calculando dados da curva Monte Carlo
    no_of_bins = int(np.ceil(np.sqrt(sims)))
    freqs, edges = get_histogram_data(monte_carlo_data, no_of_bins)
    lec_x = edges[:-1] / 1e6  # Convertendo para milhões
    lec_y = (100 - (np.cumsum(freqs) / sims * 100))  # Convertendo frequências para porcentagens

    # Configurando o tamanho da figura
    plt.figure(figsize=(14, 8))

    # Plotando a curva de apetite de risco
    sns.lineplot(x=losses, y=risks, marker='o', color='blue', label='Risk Appetite')

    # Plotando a curva de Monte Carlo
    sns.lineplot(x=lec_x, y=lec_y, color='red', label='Aggregated Risk')

    # Plotando a curva de Risco Residual
    sns.kdeplot(residual_risk / 1e6, cumulative=True, color='green', label='Residual Risk')

    # Configurando títulos e rótulos dos eixos
    plt.title('Loss Exceedance Curve')
    plt.xlabel('Loss (millions)')
    plt.ylabel('Probability (%)')

    # Ajustando os limites e ticks do eixo X
    plt.xticks(np.arange(0, max(lec_x), step=10))
    plt.xlim(0, max(lec_x))

    # Ajustando os limites e ticks do eixo Y
    plt.yticks(np.arange(0, 101, step=10))
    plt.ylim(0, 100)

    # Adicionando grid
    plt.grid(True, linestyle='--', alpha=0.6)

    # Adicionando legenda
    plt.legend(loc='upper right')

    # Exibindo o gráfico no Streamlit
    st.pyplot(plt)

def run():
    st.title("Relatorio")
    # Carregar catálogos de eventos
    df_catalogues = get_catalogues()
    if not df_catalogues.empty:
        events = df_catalogues['ThreatEvent'].tolist()
        selected_event = st.selectbox("Selecione o Evento de Ameaça", options=events)

        if st.button("Carregar Dados do Evento e Simular Riscos"):
            event_data = fetch_event_data(selected_event)
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

                # Buscar control gap e proposed control gap
                strength_data = fetch_strength_data()
                control_gap = pd.DataFrame(strength_data).query('controlId == -2')['controlGap'].values[0]
                proposed_control_gap = pd.DataFrame(strength_data).query('controlId == -1')['controlGap'].values[0]

                # Calcular inherent e residual risk
                inherent_risk = calculate_inherent_risk(sim_results, control_gap)
                residual_risk = calculate_residual_risk(inherent_risk, proposed_control_gap)

                # KDE plot ajustado para frequência
                plt.figure(figsize=(10, 6))
                sns.histplot(sim_results, bins=int(np.sqrt(sims)), kde=True, stat="frequency", label='Aggregated Risk')
                sns.histplot(residual_risk, bins=int(np.sqrt(sims)), kde=True, stat="frequency", color='green', label='Residual Risk')
                plt.title('KDE Plot de Riscos do Evento e Residual')
                plt.xlabel('Perda')
                plt.ylabel('Frequência')
                plt.grid(True, linestyle='--', alpha=0.6)
                plt.legend(loc='upper right')

                # Exibindo o gráfico no Streamlit
                st.pyplot(plt)

    else:
        st.error("Falha ao carregar catálogos de eventos. Por favor, verifique a conectividade da API ou os parâmetros da requisição.")
    # Selecionar o tipo de gráfico
    chart_type = st.selectbox("Selecione o tipo de gráfico:", ["KDE Plot Agregado", "Curva de Excedência de Perda"])

    if chart_type == "KDE Plot Agregado":
        if st.button("Gerar Dados"):
            # Carregar dados agregados
            aggregated_data = fetch_aggregated_data()
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

                # Buscar control gap e proposed control gap
                strength_data = fetch_strength_data()
                control_gap = pd.DataFrame(strength_data).query('controlId == -2')['controlGap'].values[0]
                proposed_control_gap = pd.DataFrame(strength_data).query('controlId == -1')['controlGap'].values[0]

                # Calcular inherent e residual risk
                inherent_risk = calculate_inherent_risk(sim_results, control_gap)
                residual_risk = calculate_residual_risk(inherent_risk, proposed_control_gap)

                # KDE plot ajustado para frequência
                plt.figure(figsize=(10, 6))
                sns.histplot(sim_results, bins=int(np.sqrt(sims)), kde=True, stat="frequency", label='Aggregated Risk')
                sns.histplot(residual_risk, bins=int(np.sqrt(sims)), kde=True, stat="frequency", color='green', label='Residual Risk')
                plt.title('KDE Plot de Riscos Agregados e Residual')
                plt.xlabel('Perda')
                plt.ylabel('Frequência')
                plt.grid(True, linestyle='--', alpha=0.6)
                plt.legend(loc='upper right')

                # Exibindo o gráfico no Streamlit
                st.pyplot(plt)

    elif chart_type == "Curva de Excedência de Perda":
        # Carregar dados de apetite
        appetite_data = fetch_appetite_data()
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

            # Buscar control gap e proposed control gap
            strength_data = fetch_strength_data()
            control_gap = pd.DataFrame(strength_data).query('controlId == -2')['controlGap'].values[0]
            proposed_control_gap = pd.DataFrame(strength_data).query('controlId == -1')['controlGap'].values[0]

            # Calcular inherent e residual risk
            inherent_risk = calculate_inherent_risk(monte_carlo_data, control_gap)
            residual_risk = calculate_residual_risk(inherent_risk, proposed_control_gap)

            plot_loss_exceedance_curve(appetite_data, monte_carlo_data, residual_risk)

    

if __name__ == "__main__":
    run()
