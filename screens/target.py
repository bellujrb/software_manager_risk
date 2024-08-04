import streamlit as st
import pandas as pd


def run():
    st.title("Avaliação de Risco Corporativo")

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

    if st.button("Salvar Informações Gerais"):
        st.success("Informações Gerais Salvas!")

    st.subheader("Perfil Organizacional")
    col1, col2, col3 = st.columns(3)
    with col1:
        target_environment = st.text_input("Ambiente-alvo", value="Capitalização")
        annual_turnover = st.text_input("Faturamento anual", value="R$ 9,134,000,000")
    with col2:
        profit = st.text_input("Lucro", value="R$ 732,405,000")
        share_price = st.text_input("Valor da ação", value="R$ 12.51")
    with col3:
        industry_sector = st.text_input("Setor da indústria", value="Health Care and Social Assistance")
        geographic_region = st.text_input("Região geográfica", value="South America")
        number_of_operational_sites = st.text_input("Número de locais operacionais", value="4")
        staff_size = st.text_input("Número de funcionários no ambiente", value="Grande (250+)")

    if st.button("Salvar Perfil Organizacional"):
        st.success("Perfil Organizacional Salvo!")