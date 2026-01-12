import streamlit as st
import pandas as pd
from datetime import timedelta
from app.services.financeiro_rules import aplicar_regras_financeiras


def render_relatorio_financeiro_instalacoes():
    st.markdown("## 🧾 Resumo de Instalações – Financeiro")

    # ======================================================
    # 1️⃣ Dados técnicos vindos da tela de fechamento
    # ======================================================
    df_base = st.session_state.get("df_fechamento_filtrado")

    if df_base is None or df_base.empty:
        st.warning("Relatório técnico ainda não foi carregado.")
        return

    # ======================================================
    # 2️⃣ Aplica regras financeiras
    # ======================================================
    df = aplicar_regras_financeiras(df_base)

    # ======================================================
    # 3️⃣ Filtro por técnico / grupo
    # ======================================================
    tecnicos = sorted(df["usuario_fechamento"].dropna().unique())

    tecnico_selecionado = st.selectbox("👷 Técnico", tecnicos)

    # REGRA DE FILTRO FINANCEIRO
    if "LOBATOS" in tecnico_selecionado.upper():
        df = df[df["usuario_fechamento"].str.contains("LOBATOS", case=False, na=False)]
    else:
        df = df[df["usuario_fechamento"] == tecnico_selecionado]

    if df.empty:
        st.warning("Nenhum registro encontrado.")
        return


    # ======================================================
    # 4️⃣ Datas de referência (vindas do filtro)
    # ======================================================
    data_inicio = st.session_state.get("data_inicio_filtro")
    data_fim = st.session_state.get("data_fim_filtro")

    data_pagamento = (
        data_fim + timedelta(days=1)
        if data_fim is not None
        else None
    )



    # ======================================================
    # 5️⃣ Identifica clientes duplicados
    # ======================================================
    df["DUPLICADO"] = df.duplicated(subset=["codigo_cliente"], keep=False)

    duplicados = df[df["DUPLICADO"]]

    if not duplicados.empty:
        st.warning("⚠️ Existem clientes duplicados. Selecione quais deseja remover.")

        opcoes = duplicados.apply(
            lambda r: f"{r['codigo_cliente']} | OS {r['numero_ordem_servico']}",
            axis=1
        ).tolist()

        remover = st.multiselect("🗑️ Remover registros:", opcoes)

        if remover:
            remover_os = [x.split("OS")[1].strip() for x in remover]
            df = df[~df["numero_ordem_servico"].astype(str).isin(remover_os)]

    # ======================================================
    # 6️⃣ Totais
    # ======================================================
    df["valor_a_pagar"] = (
    df["valor_a_pagar"]
    .astype(str)
    .str.replace("R$", "", regex=False)
    .str.replace(",", ".", regex=False)
    )

    df["valor_a_pagar"] = pd.to_numeric(
        df["valor_a_pagar"],
        errors="coerce"
    ).fillna(0)
    total = df["valor_a_pagar"].sum()
    total_os = len(df)

    # ======================================================
    # 7️⃣ Cabeçalho
    # ======================================================
    st.markdown("### 🧾 RESUMO DE INSTALAÇÕES")

    if data_inicio is not None and data_fim is not None:
        st.write(
        f"**Data referência:** {data_inicio:%d/%m/%Y} - {data_fim:%d/%m/%Y}"
    )
    else:
        st.warning("Período de referência não definido pelo filtro.")

    if data_pagamento is not None:
        st.write(
        f"**Data pagamento:** {data_pagamento:%d/%m/%Y}"
    )

    # Normaliza o nome do técnico selecionado
    nome_base = (
        tecnico_selecionado
        .split("_")[0]
        .strip()
    )

    # Regra especial para Lobatos
    if "LOBATOS" in nome_base.upper():
        nome_exibicao = "Leidinaldo Lobato da Fonseca"
    else:
        nome_exibicao = nome_base

    st.write(f"**Nome do Técnico:** {nome_exibicao}")

    # Empresa pela coluna conta
    contas = df["conta"].dropna().unique()

    if len(contas) == 1:
        conta = contas[0]
    else:
        conta = "MISTO"

    if str(conta).upper().startswith("MANIA"):
        empresa = "Mania"
    elif str(conta).upper().startswith("AMAZ") or str(conta).upper().startswith("AMZ"):
        empresa = "AMZ"
    else:
        empresa = conta

    st.write(f"**Empresa:** {empresa}")

    st.markdown(f"### 📦 Total de OS: {total_os}")
    st.markdown(f"## 💰 TOTAL A RECEBER: R$ {total:,.2f}")

    # ======================================================
    # 8️⃣ Remove duplicatas reais (cliente + OS)
    # ======================================================
    df["DUPLICADO"] = df.duplicated(
        subset=["codigo_cliente", "numero_ordem_servico"],
        keep="first"
    )
    df["DUPLICADO"] = df.duplicated(
        subset=["codigo_cliente"],
        keep=False
    )
    # ======================================================
    # 9️⃣ Tabela de auditoria (visual com destaque)
    # ======================================================
    st.markdown("Relatório Fechamento Técnicos")

    auditoria_df = df[
        [
            "codigo_cliente",
            "numero_ordem_servico",
            "usuario_fechamento",
            "status_auditoria",
            "status_financeiro",
            "valor_a_pagar",
            "DUPLICADO",
        ]
    ].copy()

    auditoria_df["status_auditoria"] = auditoria_df["status_auditoria"].fillna("")
    auditoria_df["status_financeiro"] = auditoria_df["status_financeiro"].fillna("")
    auditoria_df["valor_a_pagar"] = pd.to_numeric(
        auditoria_df["valor_a_pagar"], errors="coerce"
    ).fillna(0)

    auditoria_df = auditoria_df.reset_index(drop=True)
    auditoria_df.index = auditoria_df.index + 1


    def destacar_duplicados(row):
        if row["DUPLICADO"]:
            return ["background-color: #ffcccc"] * len(row)
        return [""] * len(row)


    st.dataframe(
        auditoria_df
        .style
        .apply(destacar_duplicados, axis=1),
        use_container_width=True
    )

    # ======================================================
    # 🔟 Editor (sem estilo, mas editável)
    # ======================================================
    edited = st.data_editor(
        auditoria_df.drop(columns=["DUPLICADO"]),
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "status_auditoria": st.column_config.SelectboxColumn(
                "Status Auditoria",
                options=[
                    "",
                    "APROVADO",
                    "N.C APROVADO",
                    "REPROVADO",
                    "REPROVADO PARCIAL",
                    "NAO AUDITADO",
                ],
            ),
            "status_financeiro": st.column_config.SelectboxColumn(
                "Status Financeiro",
                options=["", "PAGO", "-"],
            ),
            "valor_a_pagar": st.column_config.NumberColumn(
                "Valor a pagar",
                min_value=0,
                step=10,
            ),
        },
    )


    # ======================================================
    # 11️⃣ Regras automáticas de pagamento
    # ======================================================
    def recalcular(row):
        if row["status_auditoria"] in ["REPROVADO", "REPROVADO PARCIAL"]:
            return 0
        return row["valor_a_pagar"]

    edited["valor_a_pagar"] = edited.apply(recalcular, axis=1)

    # ======================================================
    # 12️⃣ Total final
    # ======================================================
    total_final = edited["valor_a_pagar"].sum()

    st.markdown("### 📊 Resultado Final")
    st.dataframe(edited, use_container_width=True)

