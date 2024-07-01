import pandas as pd
import streamlit as st


def get_frequency_data():
    if 'freq_data' in st.session_state and not st.session_state.freq_data.empty:
        freq_df = st.session_state.freq_data
        freq_df = freq_df[['ID do evento de ameaça', 'Evento de ameaça', 'Frequência mínima', 'Frequência máxima',
                           'Frequência mais comum (moda)']]
        freq_df.columns = ['Threat event ID', 'Threat event', 'Frequency Min', 'Frequency Max', 'Frequency Mode']
        return freq_df
    else:
        st.session_state.freq_data_error = True
        st.error("Frequência de eventos de ameaça não disponível.")
        return pd.DataFrame()


def get_loss_data():
    if 'loss_data' in st.session_state and not st.session_state.loss_data.empty:
        loss_df = st.session_state.loss_data
        loss_df = loss_df.groupby(['Threat Event ID', 'Threat event']).agg({
            'Minimum Loss': 'sum',
            'Maximum Loss': 'sum',
            'Most likely Loss': 'sum'
        }).reset_index()
        loss_df.columns = ['Threat event ID', 'Threat event', 'Loss Min', 'Loss Max', 'Loss Mode']
        return loss_df
    else:
        st.session_state.loss_data_error = True
        st.error("Dados de perda não disponíveis.")
        return pd.DataFrame()


def generate_data(freq_df, loss_df):
    if freq_df.empty or loss_df.empty:
        return pd.DataFrame()

    data = pd.merge(freq_df, loss_df, on=['Threat event ID', 'Threat event'], how='inner')

    data['Risk Min'] = data['Frequency Min'] * data['Loss Min']
    data['Risk Max'] = data['Frequency Max'] * data['Loss Max']
    data['Risk Mode'] = data['Frequency Mode'] * data['Loss Mode']

    data['Frequency Estimate (PERT)'] = (data['Frequency Min'] + 4 * data['Frequency Mode'] + data['Frequency Max']) / 6
    data['Loss Estimate (PERT)'] = (data['Loss Min'] + 4 * data['Loss Mode'] + data['Loss Max']) / 6
    data['Risk Estimate (PERT)'] = (data['Risk Min'] + 4 * data['Risk Mode'] + data['Risk Max']) / 6

    return data


def run():
    st.title('Risk Calculation')

    st.session_state.freq_data_error = False
    st.session_state.loss_data_error = False

    freq_df = get_frequency_data()
    loss_df = get_loss_data()

    df = generate_data(freq_df, loss_df)

    st.write("Tabela de Cálculo de Risco:")

    metric_choice = st.selectbox('Selecione a Métrica para Visualizar:', ['Frequency', 'Loss', 'Risk'])

    if not st.session_state.freq_data_error and not st.session_state.loss_data_error:
        if st.button('Mostrar Detalhes'):
            if metric_choice == 'Frequency':
                metric_data = df[['Threat event ID', 'Threat event', 'Frequency Min', 'Frequency Max', 'Frequency Mode',
                                  'Frequency Estimate (PERT)']]
            elif metric_choice == 'Loss':
                metric_data = df[
                    ['Threat event ID', 'Threat event', 'Loss Min', 'Loss Max', 'Loss Mode', 'Loss Estimate (PERT)']]
            else:
                metric_data = df[
                    ['Threat event ID', 'Threat event', 'Risk Min', 'Risk Max', 'Risk Mode', 'Risk Estimate (PERT)']]

            st.write(f"Detalhes para {metric_choice}:")
            st.dataframe(metric_data)
