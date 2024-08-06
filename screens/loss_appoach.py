import streamlit as st

from data.loss_appoach_service import post_losshigh_specific


def send_request(loss_type):
    with st.spinner('Enviando solicitação...'):
        response = post_losshigh_specific(loss_type)
    if response.status_code == 200:
        st.success(f"Você selecionou '{loss_type}' e a solicitação foi bem-sucedida.")
    else:
        st.error(f"Erro ao enviar solicitação: {response.status_code} - {response.text}")


def run():
    st.title("Página de Abordagem de Perda")

    options = {
        "Estimativas Únicas": {
            "description": "O praticante deve fornecer estimativas para cada evento de ameaça, considerando todos os "
                           "ativos e tipos de perda. Usar os materiais padrão ISF requer até 70 estimativas.",
            "type": "Singular"
        },
        "Nível Alto": {
            "description": "O praticante deve determinar os tipos de perda em escopo e fornecer uma estimativa para "
                           "os custos diretos e indiretos associados a um evento de ameaça. Usar os materiais padrão "
                           "ISF requer até 140 estimativas.",
            "type": "LossHigh"
        },
        "Granular": {
            "description": "O praticante deve determinar os tipos de perda em escopo e fornecer uma estimativa para "
                           "cada tipo de perda que impacta cada ativo associado a um evento de ameaça. Usar os "
                           "materiais padrão ISF requer até 90 estimativas por ativo, por evento de ameaça.",
            "type": "Granular"
        }
    }

    for option, details in options.items():
        with st.expander(option):
            st.write(details["description"])
            if st.button(f'Selecionar "{option}"'):
                st.session_state['loss_mode'] = details["type"]
                send_request(details["type"])
                st.rerun()
