import requests
import pandas as pd
import streamlit as st


def fetch_data_from_api():
    url = "http://3.142.77.137:8080/api/all-strength"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()["Response"]
    else:
        st.error(f"Erro ao buscar dados da API: {response.status_code}")
        return []


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


# Função principal
def run():
    global filtered_data
    st.title("Interface de Gestão de Controles e Ataques")

    # Mostrar a tabela combinada original
    data = fetch_data_from_api()
    if data:
        combined_data = display_combined_table(data)

        # Seção para cálculo específico
        st.header("Cálculo Específico")
        calculation_type = st.selectbox("Selecione o tipo de cálculo:", ['Aggregate', 'Control Gap'])

        # Obter a lista de tipos de ataque únicos
        attack_types = combined_data.columns[1:]  # Ignorar a coluna 'Control'
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