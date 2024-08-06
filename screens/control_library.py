import streamlit as st

from data.control_library_service import get_control_data, create_control


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
            st.rerun()

    elif action == 'Editar':
        st.header('Editar Controle Existente')

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
            pass

    elif action == 'Deletar':
        st.header('Deletar Controle Existente')

        control_id = st.selectbox('Selecione o Controle para Deletar', df['ID do Controle'].unique())


