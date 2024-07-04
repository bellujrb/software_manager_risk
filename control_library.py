import streamlit as st
import pandas as pd


def run():
    st.title('Control Library')

    if 'control_data' not in st.session_state:
        st.session_state.control_data = pd.DataFrame(columns=[
            'Control ID', 'Control Type', 'Control Reference', 'Information', 'In Scope?'
        ])

    with st.form("form_controls"):
        st.write("Preencha as informações do controle a seguir:")

        control_id = st.text_input("Control ID")
        control_type = st.text_input("Control Type")
        control_reference = st.text_input("Control Reference")
        information = st.text_area("Information")
        in_scope = st.checkbox("In Scope?")

        submitted = st.form_submit_button("Registrar Controle")
        if submitted:
            new_control = pd.DataFrame([{
                'Control ID': control_id,
                'Control Type': control_type,
                'Control Reference': control_reference,
                'Information': information,
                'In Scope?': in_scope
            }])
            st.session_state.control_data = pd.concat([st.session_state.control_data, new_control], ignore_index=True)

    st.write("Controles Registrados:")
    st.write(st.session_state.control_data)
