import pandas as pd
import streamlit as st

from data.propused_strength_service import fetch_data_from_api


def display_combined_table(data):
    df = pd.DataFrame(data)

    df = df[df['controlId'] >= 0]

    df_pivot = df.pivot_table(index='controlId', columns='type_of_attack', values='porcent',
                              aggfunc='first').reset_index()
    df_pivot.fillna('-', inplace=True)

    df_pivot.columns.name = None
    df_pivot.rename(columns={'controlId': 'Control'}, inplace=True)

    columns_order = ['Control'] + [col for col in df_pivot.columns if col != 'Control']
    df_pivot = df_pivot[columns_order]

    st.write("Tabela Combinada de Controles e Eventos de Ataque:")
    st.dataframe(df_pivot)
    return df_pivot


def display_specific_calculation(data, calculation_type):
    df = pd.DataFrame(data)

    if calculation_type == 'Aggregate':
        df = df[['type_of_attack', 'aggregate']]
        df.rename(columns={'aggregate': 'Porcentagem'}, inplace=True)
    elif calculation_type == 'Control Gap':
        df = df[['type_of_attack', 'controlGap']]
        df.rename(columns={'controlGap': 'Porcentagem'}, inplace=True)

    df_pivot = df.pivot_table(index='type_of_attack', values='Porcentagem', aggfunc='first').reset_index()
    df_pivot.fillna('-', inplace=True)

    df_pivot.columns.name = None
    df_pivot.rename(columns={'type_of_attack': 'Ataque'}, inplace=True)

    st.write(f"Tabela Combinada de {calculation_type}:")
    st.dataframe(df_pivot)
    return df_pivot


def run():
    global filtered_data
    st.title("Interface de Gestão de Controles e Ataques")

    data = fetch_data_from_api()
    if data:
        combined_data = display_combined_table(data)

        st.header("Cálculo Específico")
        calculation_type = st.selectbox("Selecione o tipo de cálculo:", ['Aggregate', 'Control Gap'])

        attack_types = combined_data.columns[1:]
        attack_type = st.selectbox("Selecione o tipo de ataque:", attack_types)

        if st.button("Mostrar Calculo"):
            specific_data = fetch_data_from_api()

            if specific_data:
                if calculation_type == 'Aggregate':
                    filtered_data = [item for item in specific_data if
                                     item['type_of_attack'] == attack_type and item['controlId'] == -1]
                elif calculation_type == 'Control Gap':
                    filtered_data = [item for item in specific_data if
                                     item['type_of_attack'] == attack_type and item['controlId'] == -2]

                if filtered_data:
                    display_specific_calculation(filtered_data, calculation_type)
                else:
                    st.write("Nenhum dado encontrado para o tipo de ataque especificado.")
