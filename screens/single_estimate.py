import streamlit as st
from data.single_estimate_service import get_single_estimate, update_single_estimate


def format_number(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except ValueError:
        return value


def parse_number(value):
    try:
        return int(value.replace(".", "").replace(",", ""))
    except ValueError:
        return 0


def run():
    st.title('Estimado Único')
    all_data = get_single_estimate()

    if all_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    # Renomear as colunas
    all_data.rename(columns={
        'threat_event_id': 'ID do Evento de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'assets': 'Ativo(s)',
        'loss_type': 'Tipo de Perda',
        'minimum_loss': 'Perda Mínima',
        'maximum_loss': 'Perda Máxima',
        'most_likely_loss': 'Perda Mais Provável'
    }, inplace=True)

    if 'ID do Evento de Ameaça' not in all_data.columns:
        st.error("A coluna 'ID do Evento de Ameaça' não está presente nos dados.")
        return

    event_id_selected = st.selectbox("Selecione o ID do Evento de Ameaça",
                                     options=all_data['ID do Evento de Ameaça'].unique())

    selected_data = all_data[all_data['ID do Evento de Ameaça'] == event_id_selected]

    st.write("Dados do Evento Selecionado:")
    st.dataframe(selected_data)

    if not selected_data.empty:
        selected_data = selected_data.iloc[0]

        max_loss_input = st.text_input("Perda Máxima", value=format_number(selected_data['Perda Máxima']))
        min_loss_input = st.text_input("Perda Mínima", value=format_number(selected_data['Perda Mínima']))
        most_likely_loss_input = st.text_input("Perda Mais Provável",
                                               value=format_number(selected_data['Perda Mais Provável']))

        max_loss = parse_number(max_loss_input)
        min_loss = parse_number(min_loss_input)
        most_likely_loss = parse_number(most_likely_loss_input)

        if st.button("Atualizar Perdas"):
            result = update_single_estimate(event_id_selected, max_loss, min_loss, most_likely_loss)
            if result:
                st.success("Perdas do evento atualizadas com sucesso!")
                updated_data = get_single_estimate()
                updated_data.rename(columns={
                    'threat_event_id': 'ID do Evento de Ameaça',
                    'threat_event': 'Evento de Ameaça',
                    'assets': 'Ativo(s)',
                    'loss_type': 'Tipo de Perda',
                    'minimum_loss': 'Perda Mínima',
                    'maximum_loss': 'Perda Máxima',
                    'most_likely_loss': 'Perda Mais Provável'
                }, inplace=True)

                st.write("Dados Atualizados do Evento Selecionado:")
                st.dataframe(updated_data[updated_data['ID do Evento de Ameaça'] == event_id_selected])
            else:
                st.error("Falha ao atualizar as perdas.")
