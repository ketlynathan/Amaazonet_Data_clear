import streamlit as st
import pandas as pd
from datetime import datetime


def render_auditoria():
    st.subheader("🔍 Auditoria de Ordens de Serviço")

    # ======================================================
    # 1️⃣ Blindagem corrigida
    # ======================================================
    df_base = st.session_state.get("df_auditoria")

    if df_base is None:
        st.info("Nenhuma planilha de auditoria carregada.")
        return

    if df_base.empty:
        st.warning("Planilha vazia.")
        return

    df_base = df_base.copy()


    # ======================================================
    # 2️⃣ Criar tabela auditável independente
    # ======================================================
    if (
        "df_auditoria_trabalho" not in st.session_state
        or st.session_state["df_auditoria_trabalho"] is None
    ):

        df_trabalho = df_base.copy()

        df_trabalho["status_auditoria"] = ""
        df_trabalho["motivo_reprovacao"] = ""
        df_trabalho["auditor"] = ""
        df_trabalho["data_auditoria"] = None

        st.session_state["df_auditoria_trabalho"] = df_trabalho

    df = st.session_state["df_auditoria_trabalho"]


    # ======================================================
    # 3️⃣ Painel de Auditoria Editável
    # ======================================================
    st.markdown("### 📝 Definição Manual de Auditoria")

    colunas_edicao = [
        "codigo_cliente",
        "numero_ordem_servico",
        "usuario_fechamento",
        "status_auditoria",
        "motivo_reprovacao",
    ]

    painel = df[colunas_edicao].copy()  # ❗ sem reset_index

    painel_editado = st.data_editor(
        painel,
        use_container_width=True,
        hide_index=True,
        column_config={
            "status_auditoria": st.column_config.SelectboxColumn(
                "Status",
                options=["", "APROVADO", "REPROVADO PARCIALMENTE", "N.C APROVADO", "PENDENTE"],
            ),
            "motivo_reprovacao": st.column_config.TextColumn(
                "Motivo (se reprovado)"
            ),
        },
        key="editor_auditoria_manual",
    )

    df.update(painel_editado)

    st.session_state["df_auditoria_trabalho"] = df



    # ======================================================
    # 5️⃣ Validação obrigatória
    # ======================================================
    erros = df[
        (df["status_auditoria"] == "REPROVADO PARCIALMENTE") &
        (df["motivo_reprovacao"].astype(str).str.strip() == "")
    ]

    if not erros.empty:
        st.error("⚠️ Existem OS reprovadas sem motivo.")
    else:
        st.success("Validação OK.")


    # ======================================================
    # 7️⃣ Resumo visual organizado
    # ======================================================
    st.markdown("### 📊 Resumo da Auditoria")

    # usamos o dataframe ativo (já filtrado e editado)
    df_resumo = df.copy()

    # normaliza status para evitar erro
    df_resumo["status_auditoria"] = (
        df_resumo["status_auditoria"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    aprovadas_df = df_resumo[df_resumo["status_auditoria"] == "APROVADO"]
    reprovadas_df = df_resumo[df_resumo["status_auditoria"] == "REPROVADO PARCIALMENTE"]
    nc_aprovadas = df_resumo[df_resumo["status_auditoria"] == "N.C APROVADO"]
    pendentes_df = df_resumo[df_resumo["status_auditoria"] == ""]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aprovadas", aprovadas_df.shape[0])
    c2.metric("Reprovadas", reprovadas_df.shape[0])
    c3.metric("N.C Aprovadas", nc_aprovadas.shape[0])
    c4.metric("Pendentes", pendentes_df.shape[0])

    st.divider()

    col_aprovadas, col_reprovadas = st.columns(2)

    # ==============================
    # APROVADAS
    # ==============================
    with col_aprovadas:
        st.markdown("#### ✅ Ordens Aprovadas")

        if aprovadas_df.empty:
            st.info("Nenhuma ordem aprovada.")
        else:
            st.dataframe(
                aprovadas_df[
                    [
                        "codigo_cliente",
                        "numero_ordem_servico",
                        "usuario_fechamento",
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    # ==============================
    # REPROVADAS
    # ==============================
    with col_reprovadas:
        st.markdown("#### ❌ Ordens Reprovadas")

        if reprovadas_df.empty:
            st.info("Nenhuma ordem reprovada.")
        else:
            st.dataframe(
                reprovadas_df[
                    [
                        "codigo_cliente",
                        "numero_ordem_servico",
                        "motivo_reprovacao",
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


    # ======================================================
    # 8️⃣ Salvar Auditoria Final
    # ======================================================
    st.divider()

    auditor_nome = st.text_input("Nome do Auditor")

    if st.button("💾 Finalizar Auditoria"):

        if auditor_nome.strip() == "":
            st.warning("Informe o nome do auditor.")
            return

        if not erros.empty:
            st.error("Corrija as reprovações sem motivo antes de salvar.")
            return

        auditor_nome = st.text_input(
            "Nome do Auditor",
            value=st.session_state.get("auditor_nome", "")
        )

        st.session_state["auditor_nome"] = auditor_nome

        df["auditor"] = auditor_nome

        df["data_auditoria"] = datetime.now()

        st.session_state["df_auditoria_final"] = df.copy()

        st.success("Auditoria finalizada com sucesso.")


    
