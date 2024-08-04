import streamlit as st

from data.single_estimate_service import get_single_estimate, update_single_estimate

def run():
    st.title('Estimado Único')
    all_data = get_single_estimate()

    if all_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    all_data.rename(columns={
        'threat_event_id': 'ID do Evento de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'assets': 'Ativo(s)',
        'loss_type': 'Tipo de Perda',
        'minimum_loss': 'Perda Mínima',
        'maximum_loss': 'Perda Máxima',
        'most_likely_loss': 'Perda Mais Provável'
    }, inplace=True)

    event_id_selected = st.selectbox("Selecione o ID do Evento de Ameaça",
                                     options=all_data['ID do Evento de Ameaça'].unique())

    selected_data = all_data[all_data['ID do Evento de Ameaça'] == event_id_selected]

    st.write("Dados do Evento Selecionado:")
    st.dataframe(selected_data)

    if not selected_data.empty:
        selected_data = selected_data.iloc[0]
        max_loss = st.number_input("Perda Máxima", value=int(selected_data['Perda Máxima']), format="%d")
        min_loss = st.number_input("Perda Mínima", value=int(selected_data['Perda Mínima']), format="%d")
        most_likely_loss = st.number_input("Perda Mais Provável", value=int(selected_data['Perda Mais Provável']),
                                           format="%d")

        if st.button("Atualizar Perdas"):
            result = update_single_estimate(event_id_selected, max_loss, min_loss, most_likely_loss)
            if result:
                st.success("Perdas do evento atualizadas com sucesso!")
                updated_data = get_single_estimate()
                st.write("Dados Atualizados do Evento Selecionado:")
                st.dataframe(updated_data[updated_data[
                                              'ID do Evento de Ameaça'] == event_id_selected])  # Mostrar apenas dados atualizados para o evento específico
            else:
                st.error("Falha ao atualizar as perdas.")
