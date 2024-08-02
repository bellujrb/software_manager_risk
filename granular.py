import streamlit as st
import pandas as pd
import requests
import json
import locale

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

def get_loss_high():
    url = 'http://3.142.77.137:8080/api/losshigh-granuled'
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.json_normalize(json_response['Response'], 'Losses', ['ThreatEventID', 'ThreatEvent', 'Assets'])
            return df
        else:
            st.error('Recebido JSON vazio ou sem chave \'Response\'.')
    else:
        st.error(f'Erro ao recuperar dados de perdas: {response.status_code}')
    return pd.DataFrame()

def update_loss_high(id, data):
    url = f'http://3.142.77.137:8080/api/update-losshigh-singular/{id}'
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 200:
        return True
    else:
        st.error(f"Erro ao atualizar dados: {response.status_code} - {response.text}")
        return False

def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except:
        return value

def run():
    st.title('Granular')

    loss_data = get_loss_high()

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

            # Formatar os valores monetários no DataFrame para exibição
            event_df['Perda Mínima'] = event_df['Perda Mínima'].apply(format_currency)
            event_df['Perda Máxima'] = event_df['Perda Máxima'].apply(format_currency)
            event_df['Perda Mais Provável'] = event_df['Perda Mais Provável'].apply(format_currency)

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
                    original_row = loss_data.loc[index]  # Obtém os dados não formatados para entrada
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
                            st.write(f"Enviando dados: {data}")  # Debugging: Exibir os dados antes de enviar
                            success = update_loss_high(original_row['ID do Evento de Ameaça'], data)
                            if success:
                                st.success("Dados atualizados com sucesso!")
                            else:
                                st.error("Erro ao atualizar os dados.")

if __name__ == "__main__":
    run()
