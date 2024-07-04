import streamlit as st
import pandas as pd


def run():
    st.header("Tabela Control Relevance")

    if 'control_data' not in st.session_state:
        st.warning("Por favor, registre os controles primeiro na biblioteca de controles.")
        return

    if 'threat_data' not in st.session_state:
        st.warning("Por favor, registre as ameaças primeiro no inventário de ameaças.")
        return

    control_data = st.session_state.control_data
    threat_data = st.session_state.threat_data

    unique_threats = threat_data['Evento de Ameaça'].unique()

    data_relevance = {'Control ID': control_data['Control ID']}

    for threat in unique_threats:
        data_relevance[threat] = [0] * len(control_data)

    df_relevance = pd.DataFrame(data_relevance)

    control_ids = df_relevance['Control ID'].tolist()
    selected_control = st.selectbox("Selecione o Controle ID para editar:", control_ids)
    selected_threat = st.selectbox("Selecione o Evento de Ameaça para editar:", unique_threats)

    selected_index = control_ids.index(selected_control)
    new_value = st.number_input(
        f'Relevância do controle {selected_control} para {selected_threat}',
        min_value=0, max_value=4, value=int(df_relevance.at[selected_index, selected_threat])
    )
    df_relevance.at[selected_index, selected_threat] = new_value

    st.dataframe(df_relevance)

    st.header("Tabela de Security Ratings")

    data_ratings = {
        'Score': [0, 1, 2, 3, 4],
        'Range': ['N/A', '1-35%', '36-65%', '66-95%', '96-100%'],
        'Min': ['N/A', '1%', '36%', '66%', '96%'],
        'Max': ['N/A', '35%', '65%', '95%', '100%'],
        'Average': ['N/A', '18%', '51%', '81%', '98%']
    }

    df_ratings = pd.DataFrame(data_ratings)

    st.dataframe(df_ratings)