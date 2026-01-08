import streamlit as st
import pandas as pd
from datetime import date

from app.services.financeiro_rules import aplicar_regras_financeiras


# ======================================================
# UTIL
# ======================================================
def formatar_moeda(valor: float) -> str:
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ======================================================
# UI
# ======================================================
def render_relatorio_financeiro_instalacoes():
    st.title("🧾 Resumo de Instalações – Financeiro")

    # =========================
    # VALIDA DF ORIGEM
    # =========================
    if "df_fechamento_filtrado" not in st.session_state:
        st.warning(
            "⚠️ Gere primeiro o **Fechamento Técnicos (Metabase)**."
        )
        return

    df_origem = st.session_state["df_fechamento_filtrado"].copy()

    if df_origem.empty:
        st.warning("Nenhum dado disponível.")
        return

    # =========================
    # NORMALIZAÇÃO
    # =========================
    df = pd.DataFrame({
        "empresa": df_origem["conta"],
        "codigo_cliente": df_origem["codigo_cliente"],
        "codigo_os": df_origem["numero_ordem_servico"],
        "tecnico": df_origem["usuario_fechamento"],
        "status_os": df_origem.get("status_os", "APROVADO"),
    })

    # =========================
    # DUPLICIDADE DE CLIENTE
    # =========================
    df["cliente_duplicado"] = (
        df["codigo_cliente"]
        .duplicated(keep=False)
        .astype(int)
    )

    # =========================
    # REGRAS FINANCEIRAS
    # =========================
    df = aplicar_regras_financeiras(df)

    # =========================
    # CONTROLE MANUAL DE REMOÇÃO
    # =========================
    df["remover"] = False

    st.subheader("📋 Registros")

    df_editado = st.data_editor(
        df,
        column_config={
            "remover": st.column_config.CheckboxColumn(
                "Remover"
            ),
            "valor_a_pagar": st.column_config.NumberColumn(
                "Valor a pagar (R$)",
                format="R$ %.2f",
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

    df_final = df_editado[~df_editado["remover"]].copy()

    # =========================
    # RESUMO
    # =========================
    total_receber = df_final["valor_a_pagar"].sum()

    tecnico = (
        df_final["tecnico"].iloc[0]
        if not df_final.empty
        else "-"
    )

    empresa = (
        df_final["empresa"].iloc[0]
        if not df_final.empty
        else "-"
    )

    st.markdown("## 📊 Resumo Financeiro")

    col1, col2, col3 = st.columns(3)

    col1.metric("Empresa", empresa)
    col2.metric("Técnico", tecnico)
    col3.metric(
        "Total a Receber",
        formatar_moeda(total_receber),
    )

    # =========================
    # TABELA FINAL
    # =========================
    st.subheader("📄 Relatório Final")

    colunas_finais = [
        "empresa",
        "codigo_cliente",
        "codigo_os",
        "tecnico",
        "status_os",
        "status_financeiro",
        "valor_a_pagar",
        "cliente_duplicado",
    ]

    st.dataframe(
        df_final[colunas_finais],
        use_container_width=True,
        hide_index=True,
    )

    # =========================
    # EXPORTAÇÃO
    # =========================
    st.download_button(
        "⬇️ Exportar Relatório Financeiro",
        df_final[colunas_finais].to_csv(index=False),
        file_name="resumo_instalacoes_financeiro.csv",
        mime="text/csv",
    )
