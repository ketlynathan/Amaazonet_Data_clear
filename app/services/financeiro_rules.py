import streamlit as st
import pandas as pd
from datetime import date

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="💰 Financeiro – Instalações",
    layout="wide",
)

# ======================================================
# REGRAS DE NEGÓCIO
# ======================================================
STATUS_VALIDOS = {"APROVADO", "N.C APROVADO"}

VALOR_POR_TECNICO = {
    "NADINEI": 60.0,
    "EDINELSON": 50.0,
    "LOBATOS": 90.0,
}

# ======================================================
# ENGINE FINANCEIRO
# ======================================================
def aplicar_regras_financeiras(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalizações
    df["tecnico"] = (
        df["usuario_fechamento"]
        .astype(str)
        .str.strip()
    )

    df["tecnico_normalizado"] = df["tecnico"].str.upper()

    # Status financeiro
    df["status_financeiro"] = df["status_os"].apply(
        lambda x: "PAGO" if x in STATUS_VALIDOS else "BLOQUEADO"
    )

    # Valor a pagar
    def calcular_valor(row):
        if row["status_os"] not in STATUS_VALIDOS:
            return 0.0
        return VALOR_POR_TECNICO.get(row["tecnico_normalizado"], 0.0)

    df["valor_a_pagar"] = df.apply(calcular_valor, axis=1)

    return df

# ======================================================
# APP
# ======================================================
def render_financeiro_instalacoes():
    st.title("💰 Relatório Financeiro – Instalações")

    # ==================================================
    # RECUPERA BASE DO METABASE
    # ==================================================
    df_origem = st.session_state.get(
        "df_fechamento_filtrado",
        pd.DataFrame()
    )

    if df_origem.empty:
        st.warning(
            "⚠️ Nenhum dado recebido.\n\n"
            "👉 Gere o relatório na tela **Fechamento Técnico – Metabase** primeiro."
        )
        return

    st.success(f"📥 {len(df_origem)} registros recebidos do Metabase")

    # ==================================================
    # APLICA REGRAS FINANCEIRAS
    # ==================================================
    df = aplicar_regras_financeiras(df_origem)

    # ==================================================
    # RESUMO
    # ==================================================
    st.subheader("📌 Resumo Financeiro")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total de Ordens",
            len(df),
        )

    with col2:
        st.metric(
            "Ordens Pagas",
            int((df["status_financeiro"] == "PAGO").sum()),
        )

    with col3:
        total_geral = df["valor_a_pagar"].sum()
        st.metric(
            "Total a Pagar",
            f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )

    # ==================================================
    # AGRUPAMENTO POR TÉCNICO
    # ==================================================
    st.subheader("👷 Pagamento por Técnico")

    df_tecnico = (
        df.groupby("tecnico", as_index=False)
        .agg(
            ordens=("numero_ordem_servico", "count"),
            total=("valor_a_pagar", "sum"),
        )
        .sort_values("total", ascending=False)
    )

    df_tecnico["total"] = df_tecnico["total"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.dataframe(
        df_tecnico,
        use_container_width=True,
        hide_index=True,
    )

    # ==================================================
    # TABELA DETALHADA
    # ==================================================
    st.subheader("📄 Detalhamento das Ordens")

    colunas_exibir = [
        "conta",
        "codigo_cliente",
        "numero_ordem_servico",
        "tecnico",
        "status_os",
        "status_financeiro",
        "valor_a_pagar",
    ]

    colunas_exibir = [c for c in colunas_exibir if c in df.columns]

    df_exibir = df[colunas_exibir].copy()

    df_exibir["valor_a_pagar"] = df_exibir["valor_a_pagar"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True,
    )

    # ==================================================
    # EXPORTAÇÃO
    # ==================================================
    st.download_button(
        "⬇️ Exportar Financeiro (CSV)",
        df.to_csv(index=False),
        file_name=f"financeiro_instalacoes_{date.today()}.csv",
        mime="text/csv",
    )
