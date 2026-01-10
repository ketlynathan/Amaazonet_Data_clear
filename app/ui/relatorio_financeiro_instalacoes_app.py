import streamlit as st
import pandas as pd
from datetime import timedelta
from app.services.financeiro_rules import aplicar_regras_financeiras


def render_relatorio_financeiro_instalacoes():
    st.markdown("## 🧾 Resumo de Instalações – Financeiro")

    # ===============================
    # 1) Dados do técnico (session)
    # ===============================
    df_base = st.session_state.get("df_fechamento_filtrado")

    if df_base is None or df_base.empty:
        st.warning("Relatório técnico ainda não foi carregado.")
        return

    # ===============================
    # 2) Aplica regras financeiras
    # ===============================
    df = aplicar_regras_financeiras(df_base)

    # ===============================
    # 3) Filtro por técnico
    # ===============================
    tecnicos = sorted(df["usuario_fechamento"].dropna().unique())
    tecnico = st.selectbox("👷 Técnico", tecnicos)

    df = df[df["usuario_fechamento"] == tecnico]

    if df.empty:
        st.warning("Nenhum registro encontrado.")
        return

    # ===============================
    # 4) Datas
    # ===============================
    data_fim = pd.to_datetime(df["data_termino_executado"], dayfirst=True, errors="coerce").max()
    data_inicio = data_fim - timedelta(days=5)
    

    if pd.notnull(data_fim):
        data_pagamento = data_fim + timedelta(days=1)
    else:
        data_pagamento = None

    # ===============================
    # 5) Detecta duplicados
    # ===============================
    df["duplicado"] = df.duplicated(subset=["codigo_cliente"], keep=False)

    duplicados = df[df["duplicado"]]

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

    # ===============================
    # 6) Recalcula total
    # ===============================
    total = df["valor_a_pagar"].sum()
    total_os = len(df)

    # ===============================
    # 7) Cabeçalho
    # ===============================
    nome_exibicao = tecnico.split("_")[0]

    st.markdown("### 🧾 RESUMO DE INSTALAÇÕES")
    st.write(f"**Data referência:** {data_inicio:%d/%m} - {data_fim:%d/%m}")
    if data_pagamento:
        st.write(f"**Data pagamento:** {data_pagamento:%d/%m/%Y}")
    st.write(f"**Nome retirador:** {nome_exibicao}")
    st.write("**Empresa:** AMZ")

    st.markdown(f"### 📦 Total de OS: {total_os}")
    st.markdown(f"## 💰 TOTAL A RECEBER: R$ {total:,.2f}")

    # ===============================
    # 8) Tabela final
    # ===============================
    st.markdown("### 🧪 Auditoria Manual (corrigir antes do pagamento)")

    editable_df = df[[
        "id",
        "codigo_cliente",
        "numero_ordem_servico",
        "usuario_fechamento",
        "status_auditoria",
        "status_financeiro",
        "valor_a_pagar"
    ]].copy()

    edited = st.data_editor(
        editable_df,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "status_auditoria": st.column_config.SelectboxColumn(
                "STATUS",
                options=["APROVADO", "N.C APROVADO", "REPROVADO", "REPROVADO PARCIAL", "NAO AUDITADO"]
            )
        }
    )


    def highlight(row):
        if row["DUPLICADO"]:
            return ["background-color: #ffcccc"] * len(row)
        return [""] * len(row)

    st.dataframe(
        tabela.style.apply(highlight, axis=1),
        use_container_width=True,
        hide_index=True
    )