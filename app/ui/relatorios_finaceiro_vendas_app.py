import streamlit as st
import pandas as pd
from app.analysis.Financeiro.financeiro_rules_venda import aplicar_regras


def render_relatorio_financeiro_vendas():
    st.markdown("## 🧾 Resumo Financeiro – Vendas")

    # =====================================================
    # VALIDA BASE
    # =====================================================
    if "df_fechamento_filtrado" not in st.session_state:
        st.warning("Carregue o fechamento primeiro.")
        return

    df_base = st.session_state["df_fechamento_filtrado"].copy()

    if df_base.empty:
        st.warning("Nenhum dado disponível.")
        return

    # =====================================================
    # APLICA REGRAS FINANCEIRAS
    # =====================================================
    try:
        resultados = aplicar_regras(df_base)
    except Exception as e:
        st.error(f"Erro ao aplicar regras financeiras: {e}")
        return

    if "autonomos" not in resultados:
        st.error("Resultado das regras não contém a chave 'autonomos'.")
        return

    base_autonomos = resultados["autonomos"]

    if base_autonomos is None or base_autonomos.empty:
        st.info("Nenhum vendedor autônomo encontrado para o período.")
        return

    # =====================================================
    # GARANTE COLUNAS ESPERADAS
    # =====================================================
    def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        return df

    base_autonomos = normalizar_colunas(base_autonomos)

    if "tipo_vendedor" not in base_autonomos.columns:
        st.error(
            f"Coluna 'tipo_vendedor' não encontrada. Colunas disponíveis: {list(base_autonomos.columns)}"
        )
        return

    # =====================================================
    # FILTROS
    # =====================================================
    st.markdown("## 👤 Vendedores Autônomos (51 STM + 60)")

    tipos = sorted(base_autonomos["tipo_vendedor"].dropna().unique())

    if not tipos:
        st.info("Nenhum tipo de vendedor encontrado.")
        return

    tipo_escolhido = st.selectbox("Filtrar tipo de vendedor", tipos)

    filtrado = base_autonomos[
        base_autonomos["tipo_vendedor"] == tipo_escolhido
    ]

    # =====================================================
    # RESUMO FINANCEIRO
    # =====================================================
    if "valor_comissao" in filtrado.columns:
        filtrado["valor_comissao"] = pd.to_numeric(
            filtrado["valor_comissao"], errors="coerce"
        ).fillna(0)

        total = filtrado["valor_comissao"].sum()

        st.success(
            f"💰 Total de comissão ({tipo_escolhido}): "
            f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    # =====================================================
    # TABELA FINAL
    # =====================================================
    df_final = resultados["base_completa"]
    totais = resultados["total_por_vendedor"]

    st.subheader("📋 Base Completa (Metabase + Planilhas)")
    st.dataframe(df_final, use_container_width=True)

    st.subheader("💰 Total por Vendedor")
    st.dataframe(totais, use_container_width=True)


