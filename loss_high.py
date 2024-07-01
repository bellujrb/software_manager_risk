import streamlit as st
import pandas as pd


def run():
    st.title('Loss-High')

    if 'threat_data' not in st.session_state or st.session_state.threat_data.empty:
        st.error(
            'Não há dados de eventos de ameaça registrados. Certifique-se de que os eventos de ameaça foram '
            'registrados no inventário de ameaças.')
        return

    if 'threat_asset_data' not in st.session_state or st.session_state.threat_asset_data.empty:
        st.error(
            'Não há dados de vinculação de ameaças a assets. Certifique-se de que as ameaças foram vinculadas aos '
            'assets.')
        return

    def merge_cells(s):
        return s.where(s != s.shift()).fillna('')

    if 'loss_data' not in st.session_state:
        st.session_state.loss_data = pd.DataFrame(columns=[
            "Threat Event ID", "Threat event", "Assets(s)", "Loss type", "Minimum Loss", "Maximum Loss",
            "Most likely Loss"
        ])

    st.header("Adicionar/Editar Dados de Perda")

    eventos_ameaca = st.session_state.threat_data[['ID', 'Evento de Ameaça']]
    selected_evento = st.selectbox("Selecionar Evento de Ameaça", eventos_ameaca['Evento de Ameaça'].unique())
    evento_id = eventos_ameaca[eventos_ameaca['Evento de Ameaça'] == selected_evento]['ID'].values[0]

    vinculados_assets = \
    st.session_state.threat_asset_data[st.session_state.threat_asset_data['ID do evento de ameaça'] == evento_id][
        'Asset afetado'].unique()

    for asset in vinculados_assets:
        st.subheader(f"Asset: {asset}")
        for loss_type in ["Direct", "Indirect"]:
            existing_record = st.session_state.loss_data[
                (st.session_state.loss_data["Threat Event ID"] == evento_id) &
                (st.session_state.loss_data["Assets(s)"] == asset) &
                (st.session_state.loss_data["Loss type"] == loss_type)
                ]

            if not existing_record.empty:
                min_loss = st.number_input(f"Minimum Loss ({loss_type})", min_value=0,
                                           value=int(existing_record["Minimum Loss"].values[0]),
                                           key=f"min_{asset}_{loss_type}")
                max_loss = st.number_input(f"Maximum Loss ({loss_type})", min_value=0,
                                           value=int(existing_record["Maximum Loss"].values[0]),
                                           key=f"max_{asset}_{loss_type}")
                most_likely_loss = st.number_input(f"Most Likely Loss ({loss_type})", min_value=0,
                                                   value=int(existing_record["Most likely Loss"].values[0]),
                                                   key=f"likely_{asset}_{loss_type}")
                if st.button(f"Atualizar Perda ({loss_type})", key=f"update_{asset}_{loss_type}"):
                    st.session_state.loss_data.loc[
                        (st.session_state.loss_data["Threat Event ID"] == evento_id) &
                        (st.session_state.loss_data["Assets(s)"] == asset) &
                        (st.session_state.loss_data["Loss type"] == loss_type),
                        ["Minimum Loss", "Maximum Loss", "Most likely Loss"]
                    ] = [min_loss, max_loss, most_likely_loss]
            else:
                min_loss = st.number_input(f"Minimum Loss ({loss_type})", min_value=0, key=f"min_{asset}_{loss_type}")
                max_loss = st.number_input(f"Maximum Loss ({loss_type})", min_value=0, key=f"max_{asset}_{loss_type}")
                most_likely_loss = st.number_input(f"Most Likely Loss ({loss_type})", min_value=0,
                                                   key=f"likely_{asset}_{loss_type}")
                if st.button(f"Adicionar Perda ({loss_type})", key=f"add_{asset}_{loss_type}"):
                    new_data = {
                        "Threat Event ID": evento_id,
                        "Threat event": selected_evento,
                        "Assets(s)": asset,
                        "Loss type": loss_type,
                        "Minimum Loss": min_loss,
                        "Maximum Loss": max_loss,
                        "Most likely Loss": most_likely_loss
                    }
                    st.session_state.loss_data = pd.concat([st.session_state.loss_data, pd.DataFrame([new_data])],
                                                           ignore_index=True)

    df = st.session_state.loss_data

    totals = df.groupby(['Threat Event ID', 'Threat event']).agg({
        'Minimum Loss': 'sum',
        'Maximum Loss': 'sum',
        'Most likely Loss': 'sum'
    }).reset_index()

    totals['Assets(s)'] = ''
    totals['Loss type'] = 'Total'

    df = pd.concat([df, totals]).sort_values(by=['Threat Event ID', 'Loss type'], ascending=[True, True]).reset_index(
        drop=True)

    df['Threat Event ID'] = merge_cells(df['Threat Event ID']).astype(str).replace('.0', '', regex=True)
    df['Threat event'] = merge_cells(df['Threat event'])

    styled_df = df.style.set_properties(**{
        'background-color': '#0e1117',
        'color': 'white',
        'border-color': 'white',
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#0e1117'), ('color', 'white')]},
        {'selector': 'td', 'props': [('background-color', '#0e1117'), ('color', 'white')]}
    ])

    st.write("Tabela de Perdas:")
    st.dataframe(df)
