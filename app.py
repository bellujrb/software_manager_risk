import streamlit as st

import control_library
import control_strength
import granular
import implementation
import inventory_assets
import loss_appoach
import loss_high
import proposed_strength
import relevance
import report
import risk_calculation
import link_threat
import inventory_threat
import frequency
import risk_analysis
import single_estimate
import target


def main():
    st.title('Sistema de Gerenciamento de Eventos de Ameaça e Ativos')

    if 'loss_mode' not in st.session_state:
        st.session_state['loss_mode'] = 'default'

    st.sidebar.title("Navegação")

    pages = [
        ("Ambiente Alvo", target.run),
        ("Inventário de Ativos", inventory_assets.run),
        ("Catálogo de Ameaça", inventory_threat.run),
        ("Frequência", frequency.run),
        ("Linkar Eventos e Ativos", link_threat.run),
        ("Abordagem de Perda", loss_appoach.run),
        ("Cálculo de Risco", risk_calculation.run),
        ("Análise de Risco", risk_analysis.run),
        ("Biblioteca de Controles", control_library.run),
        ("Relevância", relevance.run),
        ("Implementação", implementation.run),
        ("Força de Controle", control_strength.run),
        ("Força de Controle Proposta", proposed_strength.run),
        ("Relatório", report.run)
    ]

    index = next((i for i, (title, _) in enumerate(pages) if title == "Abordagem de Perda"), None) + 1

    if st.session_state['loss_mode'] == "Singular":
        pages.insert(index, ("Estimativa Única (R$)", single_estimate.run))
    elif st.session_state['loss_mode'] == "LossHigh":
        pages.insert(index, ("Perda Alta (R$)", loss_high.run))
    elif st.session_state['loss_mode'] == "Granular":
        pages.insert(index, ("Granular (R$)", granular.run))

    pages_dict = dict(pages)

    selection = st.sidebar.radio("Ir para", list(pages_dict.keys()))

    page_function = pages_dict.get(selection)
    if page_function:
        page_function()


if __name__ == "__main__":
    main()
