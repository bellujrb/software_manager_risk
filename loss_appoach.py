import streamlit as st

def run():
    st.write("Página de Abordagem de Perda")

    if st.button('Estimativas Únicas'):
        st.session_state['loss_mode'] = 'single_estimate'
        st.success("Você selecionou 'Estimativas Únicas'.")

    if st.button('Nível Alto'):
        st.session_state['loss_mode'] = 'high_loss'
        st.success("Você selecionou 'Nível Alto'.")

    if st.button('Granular'):
        st.session_state['loss_mode'] = 'granular'
        st.success("Você selecionou 'Granular'.")
