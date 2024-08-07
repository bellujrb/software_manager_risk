import streamlit as st
from data.granular_service import get_granular


def format_number(value):
    try:
        return f"R$ {int(value):,}".replace(",", ".")
    except ValueError:
        return value


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

    loss_data['Perda Mínima'] = loss_data['Perda Mínima'].apply(format_number)
    loss_data['Perda Máxima'] = loss_data['Perda Máxima'].apply(format_number)
    loss_data['Perda Mais Provável'] = loss_data['Perda Mais Provável'].apply(format_number)

    st.write("Selecione uma categoria para visualizar os ataques:")

    unique_events = loss_data['Evento de Ameaça'].unique()

    for event in unique_events:
        with st.expander(event):
            event_df = loss_data[loss_data['Evento de Ameaça'] == event]
            st.dataframe(event_df)