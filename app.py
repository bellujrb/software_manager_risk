import streamlit as st

# Importação dos módulos de cada página
import control_library
import control_strength
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

    # Configuração inicial das páginas
    pages = [
        ("Ambiente Alvo", target.run),
        ("Inventário de Ativos", inventory_assets.run),
        ("Catálogo de Ameaça", inventory_threat.run),
        ("Frequência", frequency.run),
        ("Linkar Eventos e Ativos", link_threat.run),
        ("LossAppoach", loss_appoach.run),
        ("Cálculo de Risco", risk_calculation.run),
        ("Análise de Risco", risk_analysis.run),
        ("Biblioteca de Controles", control_library.run),
        ("Relevância", relevance.run),
        ("Implementação", implementation.run),
        ("Força de controle", control_strength.run),
        ("Força de controle Proposta", proposed_strength.run),
        ("Relatório", report.run)
    ]

    # Encontrar a posição correta para inserir as novas páginas
    index = next((i for i, (title, _) in enumerate(pages) if title == "LossAppoach"), None) + 1

    # Inserir páginas dinamicamente baseadas no 'loss_mode'
    if st.session_state['loss_mode'] == "single_estimate":
        pages.insert(index, ("Estimativa Única", single_estimate.run))
    elif st.session_state['loss_mode'] == "high_loss":
        pages.insert(index, ("Perda Alta", loss_high.run))
    elif st.session_state['loss_mode'] == "granular":
        pages.insert(index, ("Granular", risk_analysis.run))

    # Transformar lista de páginas em dicionário para o radio
    pages_dict = dict(pages)

    # Seleção da página na sidebar
    selection = st.sidebar.radio("Ir para", list(pages_dict.keys()))

    # Executar a função da página selecionada
    page_function = pages_dict.get(selection)
    if page_function:
        page_function()


if __name__ == "__main__":
    main()
