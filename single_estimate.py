import streamlit as st
import pandas as pd
import requests

# Função para obter dados de perdas
def get_loss_high():
    url = 'http://3.142.77.137:8080/api/losshigh-singular'
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_response = response.json()
        if 'Response' in json_response and json_response['Response']:
            df = pd.DataFrame(json_response['Response'])
            if 'losses' in df.columns:
                df = df.explode('losses').reset_index(drop=True)
                losses_df = df['losses'].apply(pd.Series)
                df = pd.concat([df.drop(columns=['losses']), losses_df], axis=1)
                return df
            else:
                st.error('Chave "losses" não encontrada nos dados da resposta.')
                return pd.DataFrame()
        else:
            st.error('Recebido JSON vazio ou sem chave "Response".')
            return pd.DataFrame()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'Erro HTTP ao recuperar dados de perdas: {http_err}')
        return pd.DataFrame()
    except Exception as err:
        st.error(f'Erro ao recuperar dados de perdas: {err}')
        return pd.DataFrame()

# Função para atualizar perdas
def update_loss_high(event_id, max_loss, min_loss, most_likely_loss):
    url = f'http://3.142.77.137:8080/api/update-losshigh-singular/{event_id}'
    payload = {
        "maximum_loss": max_loss,
        "minimum_loss": min_loss,
        "most_likely_loss": most_likely_loss
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'Erro HTTP ao atualizar dados de perdas: {http_err}')
        return None
    except Exception as err:
        st.error(f'Erro ao atualizar dados de perdas: {err}')
        return None

def run():
    st.title('Estimado Único')
    all_data = get_loss_high()

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

    # Widget para selecionar o ID do Evento
    event_id_selected = st.selectbox("Selecione o ID do Evento de Ameaça", options=all_data['ID do Evento de Ameaça'].unique())

    # Filtrar dados para o ID selecionado
    selected_data = all_data[all_data['ID do Evento de Ameaça'] == event_id_selected]

    st.write("Dados do Evento Selecionado:")
    st.dataframe(selected_data)

    if not selected_data.empty:
        selected_data = selected_data.iloc[0]
        max_loss = st.number_input("Perda Máxima", value=int(selected_data['Perda Máxima']), format="%d")
        min_loss = st.number_input("Perda Mínima", value=int(selected_data['Perda Mínima']), format="%d")
        most_likely_loss = st.number_input("Perda Mais Provável", value=int(selected_data['Perda Mais Provável']), format="%d")

        if st.button("Atualizar Perdas"):
            result = update_loss_high(event_id_selected, max_loss, min_loss, most_likely_loss)
            if result:
                st.success("Perdas do evento atualizadas com sucesso!")
                updated_data = get_loss_high()  # Atualizar os dados da tabela
                st.write("Dados Atualizados do Evento Selecionado:")
                st.dataframe(updated_data[updated_data['ID do Evento de Ameaça'] == event_id_selected])  # Mostrar apenas dados atualizados para o evento específico
            else:
                st.error("Falha ao atualizar as perdas.")

run()
