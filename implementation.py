import pandas as pd
import streamlit as st


def fetch_control_data():
    if 'control_data' in st.session_state:
        return st.session_state.control_data[['Control ID']]
    else:
        return pd.DataFrame(columns=['Control ID'])


def fetch_threat_data():
    if 'threat_data' in st.session_state:
        return st.session_state.threat_data
    else:
        return pd.DataFrame(columns=['ID', 'Evento de Ameaça'])


def generate_control_implementation_data():
    control_data = fetch_control_data()
    implementation_data = pd.DataFrame(columns=[
        'Control ID', 'Current Implementation', 'Current Percent Value', 'Proposed Implementation',
        'Proposed Percent Value', 'Projected Cost'
    ])

    if not control_data.empty:
        implementation_data['Control ID'] = control_data['Control ID']
        implementation_data['Current Implementation'] = ''
        implementation_data['Current Percent Value'] = 0
        implementation_data['Proposed Implementation'] = ''
        implementation_data['Proposed Percent Value'] = 0
        implementation_data['Projected Cost'] = 0

    return implementation_data


def generate_aggregated_control_strength():
    threat_data = fetch_threat_data()
    aggregated_data = pd.DataFrame(columns=[
        'Threat Event ID', 'Threat Event', 'Current Control Strength', 'Proposed Control Strength'
    ])

    if not threat_data.empty:
        for _, threat_row in threat_data.iterrows():
            new_row = pd.DataFrame([{
                'Threat Event ID': threat_row['ID'],
                'Threat Event': threat_row['Evento de Ameaça'],
                'Current Control Strength': 'N/A',
                'Proposed Control Strength': 'N/A'
            }])
            aggregated_data = pd.concat([aggregated_data, new_row], ignore_index=True)

    return aggregated_data


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
    st.title('Control Management')

    view_type = st.selectbox("Select view type:", ["Control Implementation", "Aggregated Control Strength"])

    if view_type == "Control Implementation":
        control_impl_df = generate_control_implementation_data()

        st.subheader("Control Implementation Details (Edit the fields):")

        if not control_impl_df.empty:
            control_ids = control_impl_df['Control ID'].unique()

            for control_id in control_ids:
                control_data = control_impl_df[control_impl_df['Control ID'] == control_id].iloc[0]

                with st.expander(f"Edit Control ID: {control_id}"):
                    if f"current_impl_{control_id}" not in st.session_state:
                        st.session_state[f"current_impl_{control_id}"] = control_data['Current Implementation']
                    if f"proposed_impl_{control_id}" not in st.session_state:
                        st.session_state[f"proposed_impl_{control_id}"] = control_data['Proposed Implementation']

                    current_impl = st.text_input(f"Current Implementation (Control ID: {control_id})",
                                                 value=st.session_state[f"current_impl_{control_id}"],
                                                 key=f"current_impl_{control_id}")
                    current_percent = get_percent_value(int(current_impl)) if current_impl.isdigit() else 0
                    st.text(f"Current Percent Value (Control ID: {control_id}): {current_percent}%")

                    proposed_impl = st.text_input(f"Proposed Implementation (Control ID: {control_id})",
                                                  value=st.session_state[f"proposed_impl_{control_id}"],
                                                  key=f"proposed_impl_{control_id}")
                    proposed_percent = get_percent_value(int(proposed_impl)) if proposed_impl.isdigit() else 0
                    st.text(f"Proposed Percent Value (Control ID: {control_id}): {proposed_percent}%")

                    projected_cost = st.number_input(f"Projected Cost (Control ID: {control_id})",
                                                     value=control_data['Projected Cost'], min_value=0,
                                                     key=f"projected_cost_{control_id}")

                    if st.button(f"Update Control ID: {control_id}", key=f"update_{control_id}"):
                        idx = control_impl_df[control_impl_df['Control ID'] == control_id].index[0]
                        st.session_state.control_data.at[idx, 'Current Implementation'] = current_impl
                        st.session_state.control_data.at[idx, 'Current Percent Value'] = current_percent
                        st.session_state.control_data.at[idx, 'Proposed Implementation'] = proposed_impl
                        st.session_state.control_data.at[idx, 'Proposed Percent Value'] = proposed_percent
                        st.session_state.control_data.at[idx, 'Projected Cost'] = projected_cost

            st.write("Control Implementation Records:")
            st.dataframe(st.session_state.control_data[
                             ['Control ID', 'Current Implementation', 'Current Percent Value',
                              'Proposed Implementation',
                              'Proposed Percent Value', 'Projected Cost']])

        else:
            st.write("No controls found. Please add controls in the Control Library first.")

        st.header("Tabela de Security Ratings")

        data_ratings = {
            'Score': [0, 1, 2, 3, 4],
            'Range': ['N/A', '1-35%', '36-65%', '66-95%', '96-100%'],
            'Min': ['N/A', '1%', '36%', '66%', '96%'],
            'Max': ['N/A', '35%', '65%', '95%', '100%'],
            'Average': ['N/A', '18%', '51%', '81%', '98%']
        }

        df_ratings = pd.DataFrame(data_ratings)

        st.dataframe(df_ratings)

    elif view_type == "Aggregated Control Strength":
        aggregated_df = generate_aggregated_control_strength()

        st.subheader("Aggregated Control Strength")

        if not aggregated_df.empty:
            for _, row in aggregated_df.iterrows():
                threat_event_id = row['Threat Event ID']
                threat_event = row['Threat Event']
                current_strength = row['Current Control Strength']
                proposed_strength = row['Proposed Control Strength']

                with st.expander(f"Threat Event ID: {threat_event_id}"):
                    st.text(f"Threat Event: {threat_event}")
                    st.text(f"Current Control Strength: {current_strength}")
                    st.text(f"Proposed Control Strength: {proposed_strength}")

            st.write("Aggregated Control Strength Records:")
            st.dataframe(aggregated_df)

        else:
            st.write("No threats found. Please add threats in the Threat Inventory first.")
