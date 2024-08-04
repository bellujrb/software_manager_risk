import streamlit as st

from data.granular_service import get_granular, update_granular


def run():
    st.title('Granular')

    loss_data = get_granular()

    if loss_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    loss_data.rename(columns={
        'ThreatEventID': 'ID do Evento de Ameaça',
        'ThreatEvent': 'Evento de Ameaça',
        'Assets': 'Ativo(s)',
        'LossType': 'Tipo de Perda',
        'Impact': 'Impacto',
        'MinimumLoss': 'Perda Mínima',
        'MaximumLoss': 'Perda Máxima',
        'MostLikelyLoss': 'Perda Mais Provável'
    }, inplace=True)

    st.write("Selecione um evento de ameaça para visualizar as perdas:")

    unique_events = loss_data['Evento de Ameaça'].unique()

    for event in unique_events:
        with st.expander(event):
            event_df = loss_data[loss_data['Evento de Ameaça'] == event].copy()

            st.write(f"Tabela de Perdas para {event}:")
            st.dataframe(event_df)

            for index, row in event_df.iterrows():
                if row['Tipo de Perda'].lower() == "granular":
                    st.write(f"Granular - Linha {index}:")
                    st.write(f"Ativo(s): {row['Ativo(s)']}")
                    st.write(f"Tipo de Perda: {row['Tipo de Perda']}")
                    st.write(f"Perda Máxima: {row['Perda Máxima']}")
                    st.write(f"Perda Mínima: {row['Perda Mínima']}")
                    st.write(f"Perda Mais Provável: {row['Perda Mais Provável']}")
                    st.write(f"Evento de Ameaça: {row['Evento de Ameaça']}")
                else:
                    original_row = loss_data.loc[index]
                    with st.form(f"form_{index}"):
                        st.write(f"Editando a linha {index}")
                        assets = st.text_input("Ativo(s)", value=original_row['Ativo(s)'])
                        loss_type = st.selectbox("Tipo de Perda", ["direct", "indirect"],
                                                 index=["direct", "indirect"].index(original_row['Tipo de Perda'].lower()))
                        maximum_loss = st.number_input("Perda Máxima (R$)", value=original_row['Perda Máxima'])
                        minimum_loss = st.number_input("Perda Mínima (R$)", value=original_row['Perda Mínima'])
                        most_likely_loss = st.number_input("Perda Mais Provável (R$)", value=original_row['Perda Mais Provável'])
                        threat_event = st.text_input("Evento de Ameaça", value=original_row['Evento de Ameaça'], disabled=True)
                        submit_button = st.form_submit_button(label='Salvar')

                        if submit_button:
                            data = {
                                "assets": [assets],
                                "loss_type": loss_type,
                                "maximum_loss": maximum_loss,
                                "minimum_loss": minimum_loss,
                                "most_likely_loss": most_likely_loss,
                                "threat_event": threat_event
                            }
                            st.write(f"Enviando dados: {data}")
                            success = update_granular(original_row['ID do Evento de Ameaça'], data)
                            if success:
                                st.success("Dados atualizados com sucesso!")
                            else:
                                st.error("Erro ao atualizar os dados.")

