import streamlit as st
import pandas as pd
from data.frequency_service import get_threat_link_data, update_threat_link_data


def run():
    st.subheader('Análise de frequência de eventos de ameaça')

    threat_data = get_threat_link_data()

    if not threat_data.empty:
        st.session_state.threat_data = threat_data
        eventos_ameaca = st.session_state.threat_data['ThreatEvent'].tolist()

        if 'freq_data' not in st.session_state:
            st.session_state.freq_data = pd.DataFrame({
                'ID do evento de ameaça': threat_data['ID'],
                'Evento de ameaça': eventos_ameaca,
                'Frequência mínima': threat_data['MinFrequency'],
                'Frequência máxima': threat_data['MaxFrequency'],
                'Frequência mais comum (moda)': threat_data['MostLikelyFrequency'],
                'Informação de suporte': threat_data['SupportingInformation']
            })

        for idx, row in st.session_state.freq_data.iterrows():
            with st.expander(f"Editar {row['Evento de ameaça']}"):
                f_min = st.number_input(f"Frequência Mínima ({row['Evento de ameaça']})",
                                        value=row['Frequência mínima'], key=f"min{idx}")
                f_max = st.number_input(f"Frequência Máxima ({row['Evento de ameaça']})",
                                        value=row['Frequência máxima'], key=f"max{idx}")
                f_moda = st.number_input(f"Frequência Mais Comum (Moda) ({row['Evento de ameaça']})",
                                         value=row['Frequência mais comum (moda)'], key=f"moda{idx}")
                supp_info = st.text_area(f"Informação de Suporte ({row['Evento de ameaça']})",
                                         value=row['Informação de suporte'], key=f"supp{idx}")
                if st.button(f"Atualizar {row['Evento de ameaça']}", key=f"update{idx}"):
                    st.session_state.freq_data.at[idx, 'Frequência mínima'] = f_min
                    st.session_state.freq_data.at[idx, 'Frequência máxima'] = f_max
                    st.session_state.freq_data.at[idx, 'Frequência mais comum (moda)'] = f_moda
                    st.session_state.freq_data.at[idx, 'Informação de suporte'] = supp_info

                    update_data = {
                        "max_frequency": f_max,
                        "min_frequency": f_min,
                        "most_common_frequency": f_moda,
                        "support_information": supp_info,
                        "threat_event": row['Evento de ameaça']
                    }
                    update_threat_link_data(update_data, str(row['ID do evento de ameaça']))

        st.write("Registro de Frequências de Eventos de Ameaça:")
        st.dataframe(st.session_state.freq_data)

    else:
        st.write("Por favor, registre eventos de ameaça na página de Registro de Ameaças antes de proceder.")
