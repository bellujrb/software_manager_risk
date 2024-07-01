import streamlit as st

import inventory_assets
import loss_high
import risk_calculation
import link_threat
import inventory_threat
import frequency
import risk_analysis


def main():
    st.title('Sistema de Gerenciamento de Eventos de Ameaça e Ativos')

    st.write("""
    Bem-vindo ao Sistema de Gerenciamento de Eventos de Ameaça e Ativos! Este sistema permite:
    - Registrar eventos de ameaças potenciais.
    - Analisar a frequência com que esses eventos podem ocorrer.
    - Associar esses eventos a ativos específicos dentro da organização.
    - Visualizar as perdas associadas a esses eventos.
    Utilize a barra lateral para navegar entre as diferentes funcionalidades do aplicativo.
    """)

    PAGES = {
        "Inventário de Assets": inventory_assets,
        "Threat Event Catalogue": inventory_threat,
        "Frequency": frequency,
        "Threat Events & Assets": link_threat,
        "Loss-High": loss_high,
        "Risk Calculation": risk_calculation,
        "Risk Analysis": risk_analysis,
    }
    st.sidebar.title('Navegação')
    selection = st.sidebar.radio("Ir para", list(PAGES.keys()))

    if st.sidebar.button('Restaurar Sessão'):
        keys_to_remove = ['threat_data', 'freq_data', 'data', 'threat_asset_data']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

    page = PAGES[selection]
    page.run()


if __name__ == "__main__":
    main()
