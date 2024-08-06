import streamlit as st
from screens import (target, inventory_assets, inventory_threat, frequency, link_threat,
                     loss_appoach, risk_calculation, single_estimate, loss_high, granular, risk_analysis,
                     control_library, relevance,
                     implementation, control_strength, proposed_strength, report
                     )


def main():
    st.title('Sistema de Gerenciamento de Eventos de Ameaça e Ativos')

    st.write("""
        Bem-vindo ao Sistema de Gerenciamento de Eventos de Ameaça e Ativos! Este sistema permite:
        - Registrar eventos de ameaças potenciais.
        - Analisar a frequência com que esses eventos podem ocorrer.
        - Associar esses eventos a ativos específicos dentro da organização.
        Utilize a barra lateral para navegar entre as diferentes funcionalidades do aplicativo.
        """)

    if 'loss_mode' not in st.session_state:
        st.session_state['loss_mode'] = 'default'

    if 'page' not in st.session_state:
        st.session_state['page'] = "Ambiente Alvo"

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
        ("Relatório", report.run),
    ]

    index = next((i for i, (title, _) in enumerate(pages) if title == "Abordagem de Perda"), None) + 1

    if st.session_state['loss_mode'] == "Singular":
        pages.insert(index, ("Estimativa Única (R$)", single_estimate.run))
    elif st.session_state['loss_mode'] == "LossHigh":
        pages.insert(index, ("Perda Alta (R$)", loss_high.run))
    elif st.session_state['loss_mode'] == "Granular":
        pages.insert(index, ("Granular (R$)", granular.run))

    pages_dict = dict(pages)

    selection = st.sidebar.radio("Ir para", list(pages_dict.keys()),
                                 index=list(pages_dict.keys()).index(st.session_state['page']))

    if selection != st.session_state['page']:
        st.session_state['page'] = selection
        st.experimental_rerun()

    page_function = pages_dict.get(st.session_state['page'])
    if page_function:
        page_function()

    st.sidebar.title("Sobre")
    st.sidebar.info(
        "QIRA ISF é uma ferramenta desenvolvida para fornecer insights. "
        "Ela oferece análises detalhadas e recursos interativos para ajudar os usuários a tomar decisões informadas.\n"
        "Para saber mais sobre o projeto e suas funcionalidades, acesse a documentação completa [aqui]("
        "https://github.com/bellujrb)."
    )


if __name__ == "__main__":
    main()
