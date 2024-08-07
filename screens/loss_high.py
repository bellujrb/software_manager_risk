import streamlit as st
from data.loss_high_service import get_loss_high, update_loss_high


def format_number(value):
    try:
        return f"R$ {int(value):,}".replace(",", ".")
    except ValueError:
        return value


def parse_number(value):
    try:
        return int(value.replace("R$ ", "").replace(".", "").replace(",", ""))
    except ValueError:
        return 0


def update_number_input(label, key, value):
    formatted_value = st.text_input(label, value=format_number(value), key=key)
    return parse_number(formatted_value)


def run():
    st.title('Perda Alta')

    if 'loss_data' not in st.session_state:
        st.session_state.loss_data = get_loss_high()

    loss_data = st.session_state.loss_data

    if loss_data.empty:
        st.error('Não há dados de perdas disponíveis.')
        return

    loss_data.rename(columns={
        'threat_event_id': 'ID do Evento de Ameaça',
        'threat_event': 'Evento de Ameaça',
        'assets': 'Ativo(s)',
        'loss_type': 'Tipo de Perda',
        'minimum_loss': 'Perda Mínima',
        'maximum_loss': 'Perda Máxima',
        'most_likely_loss': 'Perda Mais Provável'
    }, inplace=True)

    loss_data['Perda Mínima'] = loss_data['Perda Mínima'].apply(format_number)
    loss_data['Perda Máxima'] = loss_data['Perda Máxima'].apply(format_number)
    loss_data['Perda Mais Provável'] = loss_data['Perda Mais Provável'].apply(format_number)

    st.write("Selecione uma categoria para visualizar os ataques:")

    unique_events = loss_data['Evento de Ameaça'].unique()

    for event in unique_events:
        with st.expander(event):
            event_df = loss_data[loss_data['Evento de Ameaça'] == event]
            st.write(f"Tabela de Perdas para {event}:")
            st.dataframe(event_df)

            st.write("Atualizar Perdas:")
            threat_event_id = event_df['ID do Evento de Ameaça'].iloc[0]
            assets = event_df['Ativo(s)'].iloc[0]
            threat_event = event_df['Evento de Ameaça'].iloc[0]
            loss_type = st.selectbox('Tipo de Perda', options=['Direct', 'Indirect'], key=f'{event}_loss_type')

            selected_loss = event_df[event_df['Tipo de Perda'] == loss_type]

            if not selected_loss.empty:
                max_loss = parse_number(selected_loss['Perda Máxima'].iloc[0])
                min_loss = parse_number(selected_loss['Perda Mínima'].iloc[0])
                most_likely_loss = parse_number(selected_loss['Perda Mais Provável'].iloc[0])
            else:
                max_loss = 0
                min_loss = 0
                most_likely_loss = 0

            st.text_input("Ativo(s)", value=assets, disabled=True, key=f'assets_{event}')

            max_loss_input = update_number_input('Perda Máxima', f'max_loss_{event}', max_loss)
            min_loss_input = update_number_input('Perda Mínima', f'min_loss_{event}', min_loss)
            most_likely_loss_input = update_number_input('Perda Mais Provável', f'most_likely_loss_{event}',
                                                         most_likely_loss)

            update_button = st.button('Atualizar', key=f'update_button_{event}')

            if update_button:
                st.write(f'Atualizando dados para o evento {threat_event_id}:')
                st.write({
                    "assets": [assets],
                    "loss_type": loss_type,
                    "maximum_loss": max_loss_input,
                    "minimum_loss": min_loss_input,
                    "most_likely_loss": most_likely_loss_input,
                    "threat_event": threat_event
                })
                response = update_loss_high(threat_event_id, assets, loss_type, max_loss_input, min_loss_input,
                                            most_likely_loss_input, threat_event)
                if response:
                    st.success('Dados de perda atualizados com sucesso!')
                    st.session_state.loss_data = get_loss_high()
                    st.rerun()
                else:
                    st.error("Falha ao atualizar as perdas.")
