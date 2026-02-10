import streamlit as st
import pandas as pd


def render_auditoria():
    st.subheader("🔍 Auditoria de Ordens de Serviço")

    # ======================================================
    # 1️⃣ Blindagem de contexto
    # ======================================================
    if "df_base_auditoria" not in st.session_state:
        st.info("Nenhuma planilha de auditoria carregada.")
        return

    df = st.session_state["df_base_auditoria"].copy()

    if df.empty:
        st.warning("A planilha de auditoria está vazia.")
        return

    # ======================================================
    # 2️⃣ Normalizações básicas
    # ======================================================
    if "status_auditoria" not in df.columns:
        df["status_auditoria"] = ""

    if "numero_ordem_servico" not in df.columns:
        st.error("Coluna 'numero_ordem_servico' não encontrada.")
        return

    if "codigo_cliente" not in df.columns:
        st.error("Coluna 'codigo_cliente' não encontrada.")
        return

    if "data_termino_executado" in df.columns:
        df["data_termino_executado"] = pd.to_datetime(
            df["data_termino_executado"],
            errors="coerce"
        )

    # ======================================================
    # 3️⃣ Identificação de OS duplicadas
    # ======================================================
    df = df.sort_values(
        by="data_termino_executado",
        ascending=False,
        na_position="last"
    )

    df["DUPLICADA"] = df.duplicated(
        subset=["codigo_cliente", "numero_ordem_servico"],
        keep=False
    )

    df_dup = df[df["DUPLICADA"]].copy()

    st.markdown("### 🔎 Diagnóstico de Duplicidade")

    if df_dup.empty:
        st.success("✅ Nenhuma OS duplicada encontrada neste conjunto.")
        st.dataframe(
            df.reset_index(drop=True),
            use_container_width=True
        )
        return

    st.warning(f"⚠️ {len(df_dup)} registros duplicados identificados")

    # ======================================================
    # 4️⃣ Painel de auditoria (Data Editor)
    # ======================================================
    st.markdown("### 📝 Definição do Status da Auditoria")

    colunas_painel = [
        "codigo_cliente",
        "numero_ordem_servico",
        "usuario_fechamento",
        "data_termino_executado",
        "status_auditoria",
    ]

    painel = df_dup[colunas_painel].copy()

    painel["data_termino_executado"] = painel[
        "data_termino_executado"
    ].dt.strftime("%d/%m/%Y")

    painel = painel.reset_index(drop=True)

    painel_editado = st.data_editor(
        painel,
        use_container_width=True,
        hide_index=True,
        column_config={
            "status_auditoria": st.column_config.SelectboxColumn(
                "Status da Auditoria",
                options=[
                    "",
                    "APROVADO",
                    "REPROVADO",
                    "AJUSTAR",
                    "PENDENTE",
                ],
            )
        },
        key="editor_auditoria_os",
    )

    # ======================================================
    # 5️⃣ Aplica auditoria no DataFrame principal
    # ======================================================
    for _, row in painel_editado.iterrows():
        mask = (
            (df["codigo_cliente"] == row["codigo_cliente"]) &
            (df["numero_ordem_servico"] == row["numero_ordem_servico"])
        )
        df.loc[mask, "status_auditoria"] = row["status_auditoria"]

    # ======================================================
    # 6️⃣ Feedback de pendências
    # ======================================================
    pendentes = (
        df["DUPLICADA"] &
        (
            df["status_auditoria"].isna() |
            (df["status_auditoria"].astype(str).str.strip() == "")
        )
    ).sum()

    if pendentes:
        st.warning(f"⚠️ {pendentes} OS duplicadas ainda sem auditoria")
    else:
        st.success("✅ Todas as OS duplicadas foram auditadas")

    # ======================================================
    # 7️⃣ Resultado final da auditoria
    # ======================================================
    st.markdown("### 📊 Resultado Consolidado")

    resultado = df[
        [
            "codigo_cliente",
            "numero_ordem_servico",
            "usuario_fechamento",
            "data_termino_executado",
            "status_auditoria",
            "DUPLICADA",
        ]
    ].copy()

    resultado["data_termino_executado"] = resultado[
        "data_termino_executado"
    ].dt.strftime("%d/%m/%Y")

    resultado = resultado.reset_index(drop=True)
    resultado.insert(0, "Nº", range(1, len(resultado) + 1))

    st.dataframe(resultado, use_container_width=True)

    # ======================================================
    # 8️⃣ Persistência (placeholder)
    # ======================================================
    st.divider()
    st.markdown("### 💾 Persistência da Auditoria")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Salvar Auditoria"):
            st.session_state["df_auditoria_final"] = df.copy()
            st.success("Auditoria salva em memória com sucesso.")

    with col2:
        if st.button("🗑️ Limpar Auditoria"):
            st.session_state.pop("df_base_auditoria", None)
            st.session_state.pop("df_auditoria_final", None)
            st.success("Auditoria removida.")
            st.rerun()
