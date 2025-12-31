import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.analysis.relatorios.fechamento_tecnicos import (
    relatorio_fechamento_tecnicos_df
)


# ======================================================
# CONFIG
# ======================================================
st.set_page_config(page_title="Relatório de Fechamento", layout="wide")


# ======================================================
# TELA
# ======================================================
def render_relatorio_fechamento_tecnico():
    st.title("📋 Relatório de Fechamento Técnico")

    # =========================
    # SIDEBAR - FILTROS BASE
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filtros")

        contas = st.multiselect(
            "Contas",
            ["mania", "amazonet"],
            default=["mania"],
        )

        hoje = date.today()

        periodo = st.radio(
            "Período",
            ["Semanal", "Mensal", "Período livre"],
        )

        if periodo == "Semanal":
            #data_inicio = hoje - timedelta(days=7)
            #data_fim = hoje
            data_inicio = st.date_input("Data início")
            data_fim = st.date_input("Data fim")

        elif periodo == "Mensal":
            #data_inicio = hoje.replace(day=1)
            #data_fim = hoje
            data_inicio = st.date_input("Data início")
            data_fim = st.date_input("Data fim")

        else:
            data_inicio = st.date_input("Data início")
            data_fim = st.date_input("Data fim")

        estados = st.multiselect(
            "Estado",
            ["AM", "PA"],
            default=["AM", "PA"],
        )

        gerar = st.button("📊 Gerar relatório")

    # =========================
    # CARREGA DADOS UMA VEZ
    # =========================
    if gerar:
        with st.spinner("Carregando ordens de serviço..."):
            df_base = relatorio_fechamento_tecnicos_df(
                contas=contas,
                data_inicio=data_inicio,
                data_fim=data_fim,
                estados=estados,
            )

        if df_base.empty:
            st.warning("Nenhuma ordem encontrada.")
            return

        st.session_state["df_base"] = df_base

    if "df_base" not in st.session_state:
        st.info("Selecione os filtros e clique em **📊 Gerar relatório**")
        return

    df = st.session_state["df_base"].copy()

    # ======================================================
    # DEFINIÇÃO ÚNICA DE TÉCNICO (ANTI-PERDA)
    # ======================================================
    if "usuario_fechamento.name" in df.columns:
        df["tecnico"] = df["usuario_fechamento.name"]
    elif "tecnico" in df.columns:
        df["tecnico"] = df["tecnico"]
    else:
        df["tecnico"] = None

    # ======================================================
    # BUSCA TIPO EXCEL (TEXT INPUT)
    # ======================================================
    st.subheader("🔍 Buscar técnico")

    busca = st.text_input(
        "Digite parte do nome (ex: Edinelson, Moura, TEC)",
        placeholder="Busca estilo Excel",
    )

    if busca:
        df = df[
            df["tecnico"]
            .astype(str)
            .str.contains(busca, case=False, na=False)
        ]

    # ======================================================
    # MULTISELECT (COM LISTA FILTRADA)
    # ======================================================
    tecnicos = sorted(
        df["tecnico"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    tecnicos_selecionados = st.multiselect(
        "👷 Selecionar técnicos",
        options=tecnicos,
        default=tecnicos,
    )

    if tecnicos_selecionados:
        df = df[df["tecnico"].isin(tecnicos_selecionados)]

    # ======================================================
    # ORGANIZA COLUNAS
    # ======================================================
    colunas = [
        "id_ordem_servico",
        "numero",
        "conta",
        "dados_endereco_instalacao.estado",
        "dados_endereco_instalacao.cidade",
        "tecnico",
        "tipo_ordem_servico.descricao",
        "status",
        "motivo_fechamento",
        "data_termino_executado",
    ]

    df = df[[c for c in colunas if c in df.columns]]

    # ======================================================
    # RESULTADO
    # ======================================================
    st.success(f"✅ {len(df)} ordens encontradas")

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Exportar CSV",
        df.to_csv(index=False),
        file_name="relatorio_fechamento_tecnico.csv",
        mime="text/csv",
    )
