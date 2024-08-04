import streamlit as st


def run():
    st.title("Página de Abordagem de Perda")

    if st.button('Estimativas Únicas\n\nO praticante deve fornecer estimativas para cada evento de ameaça, '
                 'considerando todos os ativos e tipos de perda.\n\nUsar os materiais padrão ISF requer até 70 '
                 'estimativas.'):
        st.session_state['loss_mode'] = 'Singular'
        st.success("Você selecionou 'Estimativas Únicas'.")

    if st.button('Nível Alto\n\nO praticante deve determinar os tipos de perda em escopo e fornecer uma estimativa '
                 'para os custos diretos e indiretos associados a um evento de ameaça.\n\nUsar os materiais padrão '
                 'ISF requer até 140 estimativas.'):
        st.session_state['loss_mode'] = 'LossHigh'
        st.success("Você selecionou 'Nível Alto'.")

    if st.button('Granular\n\nO praticante deve determinar os tipos de perda em escopo e fornecer uma estimativa para '
                 'cada tipo de perda que impacta cada ativo associado a um evento de ameaça.\n\nUsar os materiais '
                 'padrão ISF requer até 90 estimativas por ativo, por evento de ameaça.'):
        st.session_state['loss_mode'] = 'Granular'
        st.success("Você selecionou 'Granular'.")
