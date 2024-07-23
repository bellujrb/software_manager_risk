import requests
import pandas as pd
import streamlit as st


# Função para carregar os dados da API para a tabela original
def fetch_data_from_api():
    url = "http://3.142.77.137:8080/api/all-strength"
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        return response.json()["Response"]
    else:
        st.error(f"Erro ao buscar dados da API: {response.status_code}")
        return []


# Função para exibir a tabela combinada
def display_combined_table(data):
    # Criando um DataFrame organizado
    df = pd.DataFrame(data)

    # Filtrando controles com controlId menor que 0
    df = df[df['controlId'] >= 0]

    df_pivot = df.pivot_table(index='controlId', columns='type_of_attack', values='porcent',
                              aggfunc='first').reset_index()
    df_pivot.fillna('-', inplace=True)

    # Renomear colunas para legibilidade
    df_pivot.columns.name = None
    df_pivot.rename(columns={'controlId': 'Control'}, inplace=True)

    # Ordenando as colunas para manter o design esperado
    columns_order = ['Control'] + [col for col in df_pivot.columns if col != 'Control']
    df_pivot = df_pivot[columns_order]

    st.write("Tabela Combinada de Controles e Eventos de Ataque:")
    st.dataframe(df_pivot)
    return df_pivot


# Função para exibir a tabela de cálculo específico
def display_specific_calculation(data, calculation_type):
    # Criando um DataFrame organizado
    df = pd.DataFrame(data)

    # Selecionando a coluna apropriada baseado no tipo de cálculo
    if calculation_type == 'Aggregate':
        df = df[['type_of_attack', 'aggregate']]
        df.rename(columns={'aggregate': 'Porcentagem'}, inplace=True)
    elif calculation_type == 'Control Gap':
        df = df[['type_of_attack', 'controlGap']]
        df.rename(columns={'controlGap': 'Porcentagem'}, inplace=True)

    df_pivot = df.pivot_table(index='type_of_attack', values='Porcentagem', aggfunc='first').reset_index()
    df_pivot.fillna('-', inplace=True)

    # Renomear colunas para legibilidade
    df_pivot.columns.name = None
    df_pivot.rename(columns={'type_of_attack': 'Ataque'}, inplace=True)

    st.write(f"Tabela Combinada de {calculation_type}:")
    st.dataframe(df_pivot)
    return df_pivot


# Função principal
def run():
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