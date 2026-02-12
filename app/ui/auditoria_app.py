import streamlit as st
import pandas as pd
from datetime import datetime
import os


def render_auditoria():

    st.subheader("🔍 Auditoria de Ordens de Serviço")

    # ======================================================
    # 1️⃣ Verificação inicial
    # ======================================================
    df_base = st.session_state.get("df_auditoria")

    if df_base is None:
        st.info("Nenhuma planilha de auditoria carregada.")
        return

    if not isinstance(df_base, pd.DataFrame) or df_base.empty:
        st.warning("Planilha vazia ou inválida.")
        return

    df_base = df_base.copy()

    # ======================================================
    # 2️⃣ Garantir dataframe de trabalho
    # ======================================================
    df = st.session_state.get("df_auditoria_trabalho")

    if df is None or not isinstance(df, pd.DataFrame):
        df = df_base.copy()

    # ======================================================
    # 3️⃣ Garantir colunas obrigatórias
    # ======================================================
    colunas_obrigatorias = {
        "status_venda": "",
        "motivo_reprovacao_venda": "",
        "status_instalacao": "",
        "motivo_reprovacao_instalacao": "",
        "auditor": "",
        "data_auditoria": None,
    }

    for col, valor_padrao in colunas_obrigatorias.items():
        if col not in df.columns:
            df[col] = valor_padrao

    st.session_state["df_auditoria_trabalho"] = df

    # ======================================================
    # 4️⃣ Painel Editável
    # ======================================================

    st.markdown("### 📝 Definição Manual de Auditoria")

    # Garantir que dataframe já existe
    if "df_auditoria_trabalho" not in st.session_state:
        df_base_copy = df_base.copy()

        colunas_obrigatorias = {
            "status_venda": "",
            "motivo_reprovacao_venda": "",
            "status_instalacao": "",
            "motivo_reprovacao_instalacao": "",
            "auditor": "",
            "data_auditoria": None,
        }

        for col, valor in colunas_obrigatorias.items():
            if col not in df_base_copy.columns:
                df_base_copy[col] = valor

        st.session_state["df_auditoria_trabalho"] = df_base_copy

    # AQUI NÃO RECRIAMOS MAIS
    df = st.session_state["df_auditoria_trabalho"]

    colunas_edicao = [
        "codigo_cliente",
        "numero_ordem_servico",
        "usuario_abertura",
        "status_venda",
        "motivo_reprovacao_venda",
        "usuario_fechamento",
        "status_instalacao",
        "motivo_reprovacao_instalacao",
    ]

    painel = df[colunas_edicao]

    painel_editado = st.data_editor(
        painel,
        use_container_width=True,
        hide_index=True,
        column_config={
            "status_venda": st.column_config.SelectboxColumn(
                "Status Venda",
                options=["", "APROVADO", "REPROVADO", "REPROVADO PARCIALMENTE", "N.C APROVADO"],
            ),
            "status_instalacao": st.column_config.SelectboxColumn(
                "Status Instalação",
                options=["", "APROVADO", "REPROVADO", "REPROVADO PARCIALMENTE", "N.C APROVADO"],
            ),
        },
        key="editor_auditoria_manual",
    )

    # Atualização DIRETA E SEGURA
    st.session_state["df_auditoria_trabalho"][colunas_edicao] = painel_editado


    # ======================================================
    # 5️⃣ Validação
    # ======================================================
    erros_venda = df[
        df["status_venda"].isin(["REPROVADO", "REPROVADO PARCIALMENTE"])
        & (df["motivo_reprovacao_venda"].astype(str).str.strip() == "")
    ]

    erros_instalacao = df[
        df["status_instalacao"].isin(["REPROVADO", "REPROVADO PARCIALMENTE"])
        & (df["motivo_reprovacao_instalacao"].astype(str).str.strip() == "")
    ]

    if not erros_venda.empty or not erros_instalacao.empty:
        st.error("⚠️ Existem reprovações sem motivo.")
    else:
        st.success("Validação OK.")

    # ======================================================
    # 6️⃣ Resumo Comercial
    # ======================================================
    st.markdown("### 📊 Resumo da Auditoria")

    df_resumo = df.copy()

    for col in ["status_venda", "status_instalacao"]:
        df_resumo[col] = (
            df_resumo[col].fillna("").astype(str).str.strip().str.upper()
        )

    # ----------- COMERCIAL -----------
    st.markdown("## 🏢 Comercial")

    aprovadas_venda = df_resumo[df_resumo["status_venda"] == "APROVADO"]
    reprovadas_venda = df_resumo[df_resumo["status_venda"].isin(["REPROVADO", "REPROVADO PARCIALMENTE"])]
    nc_venda = df_resumo[df_resumo["status_venda"] == "N.C APROVADO"]
    pendentes_venda = df_resumo[df_resumo["status_venda"] == ""]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aprovadas", len(aprovadas_venda))
    c2.metric("Reprovadas", len(reprovadas_venda))
    c3.metric("N.C Aprovadas", len(nc_venda))
    c4.metric("Pendentes", len(pendentes_venda))

    # ----------- INSTALAÇÃO -----------
    st.divider()
    st.markdown("## 🛠️ Instalação")

    aprovadas_inst = df_resumo[df_resumo["status_instalacao"] == "APROVADO"]
    reprovadas_inst = df_resumo[df_resumo["status_instalacao"].isin(["REPROVADO", "REPROVADO PARCIALMENTE"])]
    nc_inst = df_resumo[df_resumo["status_instalacao"] == "N.C APROVADO"]
    pendentes_inst = df_resumo[df_resumo["status_instalacao"] == ""]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aprovadas", len(aprovadas_inst))
    c2.metric("Reprovadas", len(reprovadas_inst))
    c3.metric("N.C Aprovadas", len(nc_inst))
    c4.metric("Pendentes", len(pendentes_inst))

    # ==============================
    # CLASSIFICAÇÃO
    # ==============================

    aprovadas_df = df[
        (df["status_venda"] == "APROVADO") &
        (df["status_instalacao"] == "APROVADO")
    ]

    reprovadas_df = df[
        (df["status_venda"].isin(["REPROVADO", "REPROVADO PARCIALMENTE"])) |
        (df["status_instalacao"].isin(["REPROVADO", "REPROVADO PARCIALMENTE"]))
    ]


    # Função para montar descrição do status
    def formatar_status(status, motivo):
        if status in ["REPROVADO", "REPROVADO PARCIALMENTE"] and motivo:
            return f"{status} - {motivo}"
        return status


    # Aplicar formatação
    if not reprovadas_df.empty:
        reprovadas_df = reprovadas_df.copy()

        reprovadas_df["Venda"] = reprovadas_df.apply(
            lambda row: formatar_status(row["status_venda"], row.get("motivo_venda", "")),
            axis=1
        )

        reprovadas_df["Instalação"] = reprovadas_df.apply(
            lambda row: formatar_status(row["status_instalacao"], row.get("motivo_instalacao", "")),
            axis=1
        )


    # ==============================
    # LAYOUT
    # ==============================

    col_aprovadas, col_reprovadas, col_nc_aprovadas = st.columns(3)


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
                        "Venda",
                        "Instalação",
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        with col_nc_aprovadas:
            st.markdown("#### 🟡 Ordens N.C Aprovadas")

            if nc_inst.empty:
                st.info("Nenhuma ordem N.C aprovada.")
            else:
                st.dataframe(
                    nc_inst[
                        [
                            "codigo_cliente",
                            "numero_ordem_servico",
                            "Venda",
                            "Instalação",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )


    # ======================================================
    # 7️⃣ Salvar Auditoria + Excel
    # ======================================================
    st.divider()

    auditor_nome = st.text_input(
        "Nome do Auditor",
        value=st.session_state.get("auditor_nome", "")
    )

    if st.button("💾 Finalizar Auditoria"):

        if auditor_nome.strip() == "":
            st.warning("Informe o nome do auditor.")
            st.stop()

        if not erros_venda.empty or not erros_instalacao.empty:
            st.error("Corrija as reprovações sem motivo antes de salvar.")
            st.stop()

        df["auditor"] = auditor_nome
        df["data_auditoria"] = datetime.now()

        st.session_state["auditor_nome"] = auditor_nome
        st.session_state["df_auditoria_final"] = df.copy()

        # Criar pasta
        pasta = "auditorias_exportadas"
        os.makedirs(pasta, exist_ok=True)

        # Nome com timestamp único
        agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nome_arquivo = f"auditoria_{agora}.xlsx"
        caminho = os.path.join(pasta, nome_arquivo)

        df.to_excel(caminho, index=False)

        st.success(f"Auditoria finalizada e salva: {nome_arquivo}")
