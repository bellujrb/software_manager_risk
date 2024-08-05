import streamlit as st
import requests
import pandas as pd

from data.relevance_service import get_relevance_data, update_relevance_data    


def run():
    st.header("Tabela Control Relevance")

    relevance_data = get_relevance_data()
    if relevance_data is None:
        return

    df_relevance = pd.DataFrame(relevance_data['Response'])

    df_pivot = df_relevance.pivot(index='controlId', columns='type_of_attack', values='porcent').fillna(0)
    df_pivot = df_pivot.reset_index()

    st.subheader("Dados Originais")
    table_placeholder = st.empty()
    table_placeholder.dataframe(df_pivot)
    control_ids = df_pivot['controlId'].unique()
    attack_types = df_pivot.columns[1:]  # Excluir 'controlId' da lista de ataques

    selected_control = st.selectbox("Selecione o Controle ID para editar:", control_ids)
    selected_attack = st.selectbox("Selecione o Tipo de Ataque para editar:", attack_types)

    selected_row = df_pivot[df_pivot['controlId'] == selected_control]

    if not selected_row.empty:
        selected_index = selected_row.index[0]
        new_value = st.number_input(
            f'Relevância do controle {selected_control} para {selected_attack}',
            min_value=0, max_value=4, value=int(selected_row[selected_attack].values[0])
        )

        if st.button("Salvar Alterações"):
            update_relevance_data(selected_control, new_value, selected_attack)
            df_pivot.at[selected_index, selected_attack] = new_value
            table_placeholder.dataframe(df_pivot)  # Atualizar a tabela exibida
    else:
        st.warning("Combinação de Controle ID e Tipo de Ataque não encontrada.")

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