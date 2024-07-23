import pandas as pd
import streamlit as st
import requests


# Function to fetch control implementation data from API
def fetch_control_implementation_data():
    url = 'http://3.142.77.137:8080/api/all-implementation'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["Response"]
        return pd.DataFrame(data)
    else:
        st.error("Failed to fetch control implementation data")
        return pd.DataFrame(columns=[
            'id', 'controlId', 'current', 'proposed', 'percentCurrent', 'percentProposed', 'cost'
        ])


# Function to update control implementation data via PUT request
def update_control_implementation(control_id, current, proposed, cost):
    url = f'http://3.142.77.137:8080/api/implementation/{control_id}'
    data = {
        "current": int(current),
        "proposed": int(proposed),
        "cost": int(cost)
    }
    response = requests.put(url, json=data)
    return response.status_code, response.json()


# Function to get percent value based on implementation
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


# Main application function
def run():
    st.title('Control Management')

    view_type = st.selectbox("Select view type:", ["Control Implementation", "Aggregated Control Strength"])

    if view_type == "Control Implementation":
        control_impl_df = fetch_control_implementation_data()

        st.subheader("Control Implementation Details (Edit the fields):")

        if not control_impl_df.empty:
            control_id = st.selectbox(
                "Select Control ID to edit:",
                options=control_impl_df['controlId'].unique()
            )

            control_data = control_impl_df[control_impl_df['controlId'] == control_id].iloc[0]

            with st.expander(f"Edit Control ID: {control_id}"):
                current_impl = st.text_input(f"Current Implementation (Control ID: {control_id})",
                                             value=control_data['current'],
                                             key=f"current_impl_{control_id}")
                current_percent = get_percent_value(int(current_impl)) if current_impl.isdigit() else 0
                st.text(f"Current Percent Value (Control ID: {control_id}): {current_percent}%")

                proposed_impl = st.text_input(f"Proposed Implementation (Control ID: {control_id})",
                                              value=control_data['proposed'],
                                              key=f"proposed_impl_{control_id}")
                proposed_percent = get_percent_value(int(proposed_impl)) if proposed_impl.isdigit() else 0
                st.text(f"Proposed Percent Value (Control ID: {control_id}): {proposed_percent}%")

                projected_cost = st.number_input(f"Projected Cost (Control ID: {control_id})",
                                                 value=control_data['cost'], min_value=0,
                                                 key=f"projected_cost_{control_id}")

                if st.button(f"Update Control ID: {control_id}", key=f"update_{control_id}"):
                    status_code, response = update_control_implementation(control_id, current_impl, proposed_impl,
                                                                          projected_cost)
                    if status_code == 200:
                        st.success(f"Control ID {control_id} updated successfully!")
                    else:
                        st.error(f"Failed to update Control ID {control_id}. Status code: {status_code}")
                        st.json(response)  # Print the error response for debugging

            st.write("Control Implementation Records:")
            st.dataframe(control_impl_df[
                             ['controlId', 'current', 'percentCurrent',
                              'proposed', 'percentProposed', 'cost']])

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
        threat_data = ()
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

        st.subheader("Aggregated Control Strength")

        if not aggregated_data.empty:
            for _, row in aggregated_data.iterrows():
                threat_event_id = row['Threat Event ID']
                threat_event = row['Threat Event']
                current_strength = row['Current Control Strength']
                proposed_strength = row['Proposed Control Strength']

                with st.expander(f"Threat Event ID: {threat_event_id}"):
                    st.text(f"Threat Event: {threat_event}")
                    st.text(f"Current Control Strength: {current_strength}")
                    st.text(f"Proposed Control Strength: {proposed_strength}")

            st.write("Aggregated Control Strength Records:")
            st.dataframe(aggregated_data)

        else:
            st.write("No threats found. Please add threats in the Threat Inventory first.")