import streamlit as st
import pandas as pd
from app.analysis.google_sheets import read_sheet_as_dataframe

# =========================
# CARREGAMENTO DE PLANILHAS
# =========================
def carregar_planilhas_financeiro():
    sheet_60 = read_sheet_as_dataframe("60")
    sheet_51_stm = read_sheet_as_dataframe("51_STM")

    # Planilha 60
    s60 = sheet_60.iloc[:, [1, 3, 4, 7, 21]].copy()
    s60.columns = ["nome_vendedor", "codigo_cliente", "numero_ordem_servico", "tipo_vendedor", "status_planilha"]
    s60["origem"] = "60"

    # Planilha 51_STM
    stm = sheet_51_stm.iloc[276:, [2, 3, 5, 10, 23]].copy()
    stm.columns = ["codigo_cliente", "numero_ordem_servico", "nome_vendedor", "tipo_vendedor", "status_planilha"]
    stm["origem"] = "51_STM"

    # Padronização
    for df in (s60, stm):
        df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip().str.upper()
        df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip().str.upper()
        df["nome_vendedor"] = df["nome_vendedor"].astype(str).str.strip()
        df["tipo_vendedor"] = df["tipo_vendedor"].astype(str).str.strip().str.upper()
        df["status_planilha"] = df["status_planilha"].astype(str).str.strip().str.upper()

    return s60, stm

# =========================
# FUNÇÃO DE RELATÓRIO
# =========================
def aplicar_regras_relatorio(df_base: pd.DataFrame) -> pd.DataFrame:
    s60, stm = carregar_planilhas_financeiro()

    # Padroniza df_base
    df_base = df_base.copy()
    df_base["CÓDIGO CLIENTE"] = df_base["codigo_cliente"].astype(str).str.strip()
    df_base["CÓD O.S"] = df_base["numero_ordem_servico"].astype(str).str.strip()
    df_base["EMPRESA"] = df_base.get("conta", "").str.upper()

    # Planilha 60
    s60_renamed = s60.rename(columns={
        "codigo_cliente": "CÓDIGO CLIENTE",
        "numero_ordem_servico": "CÓD O.S",
        "nome_vendedor": "TÉCNICO",
        "tipo_vendedor": "TIPO_VENDEDOR",
        "status_planilha": "STATUS"
    })
    s60_renamed["FINANCEIRO"] = s60_renamed["STATUS"].apply(lambda x: "PAGO" if x in ["APROVADO", "N.C APROVADO"] else "-")
    s60_renamed["VALOR"] = s60_renamed["FINANCEIRO"].apply(lambda x: 50 if x == "PAGO" else 0)

    # Planilha 51_STM
    stm_renamed = stm.rename(columns={
        "codigo_cliente": "CÓDIGO CLIENTE",
        "numero_ordem_servico": "CÓD O.S",
        "nome_vendedor": "TÉCNICO",
        "tipo_vendedor": "TIPO_VENDEDOR",
        "status_planilha": "STATUS"
    })
    stm_renamed["FINANCEIRO"] = stm_renamed["STATUS"].apply(lambda x: "PAGO" if x in ["APROVADO", "N.C APROVADO"] else "-")
    stm_renamed["VALOR"] = stm_renamed["FINANCEIRO"].apply(lambda x: 50 if x == "PAGO" else 0)

    # Concatena planilhas
    planilhas = pd.concat([s60_renamed, stm_renamed], ignore_index=True)

    # Merge com df_base
    df_relatorio = df_base.merge(
        planilhas,
        on=["CÓDIGO CLIENTE", "CÓD O.S"],
        how="left",
        suffixes=("", "_planilha")
    )

    # Preenche não encontradas
    df_relatorio["STATUS"].fillna("-", inplace=True)
    df_relatorio["FINANCEIRO"].fillna("-", inplace=True)
    df_relatorio["VALOR"].fillna(0, inplace=True)
    df_relatorio["TIPO_VENDEDOR"].fillna("-", inplace=True)

    # Ordena e index
    df_relatorio = df_relatorio.sort_values(["EMPRESA", "CÓDIGO CLIENTE", "CÓD O.S"]).reset_index(drop=True)
    df_relatorio.index = df_relatorio.index + 1

    return df_relatorio

# =========================
# RESUMO POR VENDEDOR
# =========================
def resumo_por_vendedor(df_relatorio: pd.DataFrame):
    """
    Cria um resumo por vendedor:
        Index | Nome Vendedor | Quantidade de Vendas | Valor a Receber
    Considera apenas OS com STATUS diferente de REPROVADO.
    """
    if df_relatorio.empty:
        st.info("Nenhum dado disponível para resumo por vendedor.")
        return

    df_validos = df_relatorio[df_relatorio["STATUS"] != "REPROVADO"].copy()

    resumo = (
        df_validos.groupby("TÉCNICO", dropna=False).agg(
            Quantidade_Vendas=("CÓD O.S", "count"),
            Valor_a_Receber=("VALOR", "sum")
        )
        .reset_index()
        .rename(columns={"TÉCNICO": "Nome do Vendedor"})
    )

    resumo = resumo.sort_values("Valor_a_Receber", ascending=False).reset_index(drop=True)
    resumo.index = resumo.index + 1

    st.subheader("📊 Resumo por Vendedor")
    st.dataframe(resumo, use_container_width=True)

# =========================
# STREAMLIT APP
# =========================
def render_relatorio_financeiro_vendas():
    st.markdown("## 🧾 Relatório Financeiro – Vendas")

    if "df_fechamento_filtrado" not in st.session_state:
        st.warning("Carregue o fechamento primeiro.")
        return

    df_base = st.session_state["df_fechamento_filtrado"]
    if df_base.empty:
        st.warning("Nenhum dado disponível.")
        return

    # Aplica regras
    df_relatorio = aplicar_regras_relatorio(df_base)

    # Filtro por tipo de vendedor
    tipos_disponiveis = sorted(df_relatorio["TIPO_VENDEDOR"].dropna().unique())
    tipo_escolhido = st.selectbox("Filtrar por tipo de vendedor", tipos_disponiveis, key="tipo_vendedor")
    df_relatorio = df_relatorio[df_relatorio["TIPO_VENDEDOR"] == tipo_escolhido]

    # OS não encontradas
    st.markdown("### ⚠️ OS não encontradas na planilha (STATUS = '-')")
    for idx, row in df_relatorio[df_relatorio["STATUS"] == "-"].iterrows():
        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown(f"**{row['EMPRESA']} | {row['CÓDIGO CLIENTE']} | {row['CÓD O.S']} | {row['TÉCNICO']}**")
        with col2:
            status_novo = st.selectbox(
                "Alterar STATUS",
                ["-", "APROVADO", "N.C APROVADO", "REPROVADO"],
                key=f"status_{idx}",
            )
            if status_novo in ["APROVADO", "N.C APROVADO"]:
                df_relatorio.at[idx, "STATUS"] = status_novo
                df_relatorio.at[idx, "FINANCEIRO"] = "PAGO"
                df_relatorio.at[idx, "VALOR"] = 50
            elif status_novo == "REPROVADO":
                df_relatorio.at[idx, "STATUS"] = "REPROVADO"
                df_relatorio.at[idx, "FINANCEIRO"] = "-"
                df_relatorio.at[idx, "VALOR"] = 0

    # =========================
    # Relatório completo filtrado
    # =========================
    df_exibir = df_relatorio[df_relatorio["STATUS"] != "REPROVADO"].copy()
    st.subheader("📋 Relatório Completo")
    st.dataframe(df_exibir, use_container_width=True)

    # =========================
    # DF Consolidado sem STATUS e sem ORIGEM
    # =========================
    colunas_desejadas = ["EMPRESA", "CÓDIGO CLIENTE", "CÓD O.S", "TÉCNICO", "FINANCEIRO", "VALOR"]
    st.subheader("📂 DF Consolidado - Somente Colunas Principais")
    st.dataframe(df_exibir[colunas_desejadas], use_container_width=True)

    # =========================
    # Resumo por vendedor
    # =========================
    resumo_por_vendedor(df_exibir)
