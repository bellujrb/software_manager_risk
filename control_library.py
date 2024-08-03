import streamlit as st
import pandas as pd
import requests


# Função para buscar dados de controle
def get_control_data():
    url = 'http://3.142.77.137:8080/api/all-control'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            return df
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de controle: {response.status_code}')
    return pd.DataFrame()


# Função para criar um novo controle
def create_control(control_reference, control_type, in_scope, information):
    url = 'http://3.142.77.137:8080/api/control'
    payload = {
        "control_reference": control_reference,
        "control_type": control_type,
        "in_scope": in_scope,
        "information": information
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        st.success('Controle criado com sucesso!')
    else:
        st.error(f'Erro ao criar controle: {response.status_code}')


# Interface do Streamlit
def run():
    st.title('Biblioteca de Controles')

    if 'control_data' not in st.session_state:
        st.session_state.control_data = get_control_data()

    df = st.session_state.control_data

    df.rename(columns={
        'ID': 'ID do Controle',
        'ControlType': 'Tipo de Controle',
        'ControlReference': 'Referência do Controle',
        'Information': 'Informação'
    }, inplace=True)

    st.write("Controles Registrados:")
    st.dataframe(df)

    # Selecionar entre "Criar", "Editar" e "Deletar"
    action = st.selectbox('Selecione uma ação', ['Criar', 'Editar', 'Deletar'])

    if action == 'Criar':
        st.header('Criar Novo Controle')
        with st.form(key='create_control_form'):
            control_reference = st.text_input('Referência do Controle')
            control_type = st.text_input('Tipo de Controle')
            in_scope = st.checkbox('In Scope')
            information = st.text_area('Informação')
            submit_button = st.form_submit_button(label='Criar Controle')

        if submit_button:
            create_control(control_reference, control_type, in_scope, information)

    elif action == 'Editar':
        st.header('Editar Controle Existente')

        # Selecionar controle para editar
        control_id = st.selectbox('Selecione o Controle para Editar', df['ID do Controle'].unique())
        selected_control = df[df['ID do Controle'] == control_id].iloc[0]

        with st.form(key='edit_control_form'):
            control_reference = st.text_input('Referência do Controle',
                                              value=selected_control['Referência do Controle'])
            control_type = st.text_input('Tipo de Controle', value=selected_control['Tipo de Controle'])
            in_scope = st.checkbox('In Scope', value=selected_control['In Scope'])
            information = st.text_area('Informação', value=selected_control['Informação'])
            submit_button = st.form_submit_button(label='Atualizar Controle')

        if submit_button:
            # Lógica de atualização do controle pode ser adicionada aqui
            pass

    elif action == 'Deletar':
        st.header('Deletar Controle Existente')

        # Selecionar controle para deletar
        control_id = st.selectbox('Selecione o Controle para Deletar', df['ID do Controle'].unique())

        # Lógica de deleção do controle pode ser adicionada aqui


if __name__ == '__main__':
    run()
