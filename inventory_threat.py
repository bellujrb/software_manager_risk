import streamlit as st
import pandas as pd


def run():
    st.title('Inventário de Ameaças')

    if 'threat_data' not in st.session_state:
        st.session_state.threat_data = pd.DataFrame(columns=[
            'ID', 'Grupo de Ameaça', 'Evento de Ameaça', 'Descrição', 'No Escopo'
        ])

    with st.form("form_threats_unique_key"):
        st.write("Preencha as informações da ameaça a seguir:")

        grupo_ameaca = st.selectbox("Grupo de Ameaça", ['Adversarial', 'Accidental', 'Environmental'])
        evento_ameaca = st.text_input("Evento de Ameaça")
        descricao = st.text_area("Descrição")
        no_escopo = st.selectbox("No Escopo", ['Sim', 'Não'])

        submitted = st.form_submit_button("Registrar Ameaça")
        if submitted:
            new_threat = pd.DataFrame([{
                'ID': len(st.session_state.threat_data) + 1,
                'Grupo de Ameaça': grupo_ameaca,
                'Evento de Ameaça': evento_ameaca,
                'Descrição': descricao,
                'No Escopo': no_escopo
            }])
            st.session_state.threat_data = pd.concat([st.session_state.threat_data, new_threat], ignore_index=True)

    st.write("Inventário de Ameaças Registradas:")
    st.write(st.session_state.threat_data)
