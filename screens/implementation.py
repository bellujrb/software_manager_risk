import pandas as pd
import streamlit as st

from data.implementation_service import fetch_control_implementation_data, update_control_implementation


def get_percent_value(implementation):
    if implementation == 0:
        return 3
    elif implementation == 1:
        return 21
    elif implementation == 2:
        return 51
    elif implementation == 3:
        return 81
    elif implementation == 4:
        return 98
    else:
        return 0


def run():
    st.title('Gerenciamento de Controles')

    view_type = st.selectbox("Selecione o tipo de visualização:",
                             ["Implementação de Controle", "Força de Controle Agregada"])

    if view_type == "Implementação de Controle":
        control_impl_df = fetch_control_implementation_data()

        st.subheader("Detalhes da Implementação de Controle (Edite os campos):")

        if not control_impl_df.empty:
            control_id = st.selectbox(
                "Selecione o ID do Controle para editar:",
                options=control_impl_df['controlId'].unique()
            )

            control_data = control_impl_df[control_impl_df['controlId'] == control_id].iloc[0]

            with st.expander(f"Editar ID do Controle: {control_id}"):
                current_impl = st.text_input(f"Implementação Atual (ID do Controle: {control_id})",
                                             value=control_data['current'],
                                             key=f"current_impl_{control_id}")
                current_percent = get_percent_value(int(current_impl)) if current_impl.isdigit() else 0
                st.text(f"Valor Percentual Atual (ID do Controle: {control_id}): {current_percent}%")

                proposed_impl = st.text_input(f"Implementação Proposta (ID do Controle: {control_id})",
                                              value=control_data['proposed'],
                                              key=f"proposed_impl_{control_id}")
                proposed_percent = get_percent_value(int(proposed_impl)) if proposed_impl.isdigit() else 0
                st.text(f"Valor Percentual Proposto (ID do Controle: {control_id}): {proposed_percent}%")

                projected_cost = st.number_input(f"Custo Projetado (ID do Controle: {control_id})",
                                                 value=control_data['cost'], min_value=0,
                                                 key=f"projected_cost_{control_id}")

                if st.button(f"Atualizar ID do Controle: {control_id}", key=f"update_{control_id}"):
                    status_code, response = update_control_implementation(control_id, current_impl, proposed_impl,
                                                                          projected_cost)
                    if status_code == 200:
                        st.success(f"ID do Controle {control_id} atualizado com sucesso!")
                    else:
                        st.error(f"Falha ao atualizar ID do Controle {control_id}. Código de status: {status_code}")
                        st.json(response)  # Exibir a resposta de erro para depuração

            st.write("Registros de Implementação de Controle:")
            st.dataframe(control_impl_df[
                             ['controlId', 'current', 'percentCurrent',
                              'proposed', 'percentProposed', 'cost']])

        else:
            st.write("Nenhum controle encontrado. Por favor, adicione controles na Biblioteca de Controles primeiro.")

        st.header("Tabela de Classificações de Segurança")

        data_ratings = {
            'Pontuação': [0, 1, 2, 3, 4],
            'Intervalo': ['N/A', '1-35%', '36-65%', '66-95%', '96-100%'],
            'Mínimo': ['N/A', '1%', '36%', '66%', '96%'],
            'Máximo': ['N/A', '35%', '65%', '95%', '100%'],
            'Média': ['N/A', '18%', '51%', '81%', '98%']
        }

        df_ratings = pd.DataFrame(data_ratings)

        st.dataframe(df_ratings)

    elif view_type == "Força de Controle Agregada":
        threat_data = ()
        aggregated_data = pd.DataFrame(columns=[
            'ID do Evento de Ameaça', 'Evento de Ameaça', 'Força de Controle Atual', 'Força de Controle Proposta'
        ])

        if not threat_data.empty:
            for _, threat_row in threat_data.iterrows():
                new_row = pd.DataFrame([{
                    'ID do Evento de Ameaça': threat_row['ID'],
                    'Evento de Ameaça': threat_row['Evento de Ameaça'],
                    'Força de Controle Atual': 'N/A',
                    'Força de Controle Proposta': 'N/A'
                }])
                aggregated_data = pd.concat([aggregated_data, new_row], ignore_index=True)

        st.subheader("Força de Controle Agregada")

        if not aggregated_data.empty:
            for _, row in aggregated_data.iterrows():
                threat_event_id = row['ID do Evento de Ameaça']
                threat_event = row['Evento de Ameaça']
                current_strength = row['Força de Controle Atual']
                proposed_strength = row['Força de Controle Proposta']

                with st.expander(f"ID do Evento de Ameaça: {threat_event_id}"):
                    st.text(f"Evento de Ameaça: {threat_event}")
                    st.text(f"Força de Controle Atual: {current_strength}")
                    st.text(f"Força de Controle Proposta: {proposed_strength}")

            st.write("Registros de Força de Controle Agregada:")
            st.dataframe(aggregated_data)

        else:
            st.write("Nenhuma ameaça encontrada. Por favor, adicione ameaças no Inventário de Ameaças primeiro.")
