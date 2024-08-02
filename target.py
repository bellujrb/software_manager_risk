import streamlit as st
import pandas as pd
import locale

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

def run():
    st.title("Avaliação de Risco Corporativo")

    def format_currency(value):
        return locale.currency(value, grouping=True)

    with st.form("general_info"):
        st.subheader("Geral")
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_assessment_name = st.text_input("Nome da avaliação de risco", value="POC - TCAP")
            sponsor = st.text_input("Patrocinador", value="Títulos de Capitalização")
        with col2:
            practitioner = st.text_input("Praticante", value="Romulo")
            assessment_date = st.date_input("Data da avaliação", value=pd.to_datetime("07/06/2024", dayfirst=True))
        with col3:
            start_date = st.date_input("Início da janela de avaliação", value=pd.to_datetime("16/06/2024", dayfirst=True))
            end_date = st.date_input("Fim da janela de avaliação", value=pd.to_datetime("16/07/2024", dayfirst=True))

        submitted_general = st.form_submit_button("Salvar Informações Gerais")
        if submitted_general:
            st.success("Informações Gerais Salvas!")

    with st.form("org_profile"):
        st.subheader("Perfil Organizacional")
        col1, col2, col3 = st.columns(3)
        with col1:
            target_environment = st.text_input("Ambiente-alvo", value="Capitalização")
            annual_turnover = st.text_input("Faturamento anual", value=format_currency(9134000000))
        with col2:
            profit = st.text_input("Lucro", value=format_currency(732405000))
            share_price = st.text_input("Valor da ação", value=format_currency(12.51))
        with col3:
            industry_sector = st.text_input("Setor da indústria", value="Health Care and Social Assistance")
            geographic_region = st.text_input("Região geográfica", value="South America")
            number_of_operational_sites = st.text_input("Número de locais operacionais", value="4")
            staff_size = st.text_input("Número de funcionários no ambiente", value="Grande (250+)")

        submitted_org = st.form_submit_button("Salvar Perfil Organizacional")
        if submitted_org:
            st.success("Perfil Organizacional Salvo!")

if __name__ == "__main__":
    run()
