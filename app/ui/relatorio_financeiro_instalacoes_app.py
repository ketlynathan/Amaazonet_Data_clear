import streamlit as st
import pandas as pd
from datetime import timedelta
from pathlib import Path
from app.analysis.financeiro_rules import aplicar_regras_financeiras
from app.analysis.pdf_relatorio import montar_tabela
from app.analysis.pdf_recibo import gerar_recibo_pagamento


def render_relatorio_financeiro_instalacoes():
    st.markdown("## 🧾 Resumo Financeiro – Instalações")

    # ======================================================
    # 1️⃣ Blindagem
    # ======================================================
    if "df_fechamento_filtrado" not in st.session_state:
        st.warning("Carregue o fechamento técnico primeiro.")
        return

    df_base = st.session_state["df_fechamento_filtrado"]

    if df_base.empty:
        st.warning("Nenhum dado disponível.")
        return

    # ======================================================
    # 2️⃣ Aplica regras financeiras (51 / 60 / 51_STM / Nadinei)
    # ======================================================
    df = aplicar_regras_financeiras(df_base)

    if df.empty:
        st.warning("Nenhum dado após regras financeiras.")
        return

    # ======================================================
    # 3️⃣ Filtro de Técnico (com busca)
    # ======================================================
    st.markdown("### 👷 Técnico")

    tecnicos = sorted(df["usuario_fechamento"].dropna().unique())

    busca = st.text_input("Pesquisar técnico")

    if busca:
        tecnicos = [t for t in tecnicos if busca.lower() in t.lower()]

    if not tecnicos:
        st.warning("Nenhum técnico encontrado.")
        return

    tecnico_selecionado = st.selectbox("Selecione", tecnicos)

    # Lobatos pode ter variações
    if "LOBATOS" in tecnico_selecionado.upper():
        df = df[df["usuario_fechamento"].str.contains("LOBATOS", case=False, na=False)]
    else:
        df = df[df["usuario_fechamento"] == tecnico_selecionado]

    if df.empty:
        st.warning("Nenhum registro para este técnico.")
        return

    # ======================================================
    # 4️⃣ Datas de referência
    # ======================================================
    df["data_termino_executado"] = pd.to_datetime(
        df["data_termino_executado"], dayfirst=True, errors="coerce"
    )

    data_fim = df["data_termino_executado"].max()

    if pd.isna(data_fim):
        st.warning("Sem data válida de término.")
        return

    data_inicio = data_fim - timedelta(days=5)
    data_pagamento = data_fim + timedelta(days=1)

    # ======================================================
    # 5️⃣ Deduplicação por cliente + OS
    # ======================================================
    df = (
        df.sort_values("data_termino_executado", ascending=False)
        .drop_duplicates(subset=["codigo_cliente", "numero_ordem_servico"], keep="first")
        .reset_index(drop=True)
    )

    df["CLIENTE_REPETIDO"] = (
        df.groupby("codigo_cliente")["numero_ordem_servico"]
        .transform("nunique") > 1
    )

    dup = df[df["CLIENTE_REPETIDO"]]

    if not dup.empty:
        st.warning("⚠️ Clientes com mais de uma OS detectados")

        opcoes = dup.apply(
            lambda r: f"{r['codigo_cliente']} | OS {r['numero_ordem_servico']}",
            axis=1
        ).unique().tolist()

        remover = st.multiselect("Selecione quais OS devem ser removidas", opcoes)

        if remover:
            remover_os = [x.split("OS")[1].strip() for x in remover]
            df = df[~df["numero_ordem_servico"].astype(str).isin(remover_os)]

    
    # ======================================================
    # 7 Painel de auditoria (edição manual)
    # ======================================================

    painel = None
    df = df.copy()

    linhas_em_branco = df["status_auditoria"].isna() | (df["status_auditoria"].str.strip() == "")

    if linhas_em_branco.any():
        st.warning("⚠️ Existem OS sem status de auditoria. Você pode definir manualmente abaixo.")

        painel = df.loc[linhas_em_branco, [
            "codigo_cliente",
            "numero_ordem_servico",
            "status_auditoria"
        ]].copy()

        painel = st.data_editor(
            painel,
            use_container_width=True,
            column_config={
                "status_auditoria": st.column_config.SelectboxColumn(
                    "Status Auditoria",
                    options=["", "APROVADO", "NC APROVADO", "N.C APROVADO", "REPROVADO"],
                    required=False,
                )
            },
            key="editor_status"
        )

    # ======================================================
    # Aplica alterações no dataframe principal
    # ======================================================

    if painel is not None and not painel.empty:
        for _, row in painel.iterrows():
            df.loc[
                (df["codigo_cliente"] == row["codigo_cliente"]) &
                (df["numero_ordem_servico"] == row["numero_ordem_servico"]),
                "status_auditoria"
            ] = row["status_auditoria"]

    # ======================================================
    # Recalcula financeiro após edição
    # ======================================================

    def status_financeiro(status):
        status = str(status).upper().strip()
        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"
        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)

    df["valor_base"] = df["usuario_fechamento"].apply(
        lambda nome:
            90 if "LOBATOS" in str(nome).upper()
            else 50 if "EDINELSON" in str(nome).upper()
            else 60 if "NADINEI" in str(nome).upper()
            else 0
    )

    df["valor_a_pagar"] = df.apply(
        lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else 0,
        axis=1,
    )

    # ======================================================
    #  Totais
    # ======================================================
    df["valor_a_pagar"] = pd.to_numeric(df["valor_a_pagar"], errors="coerce").fillna(0)

    total_final = df["valor_a_pagar"].sum()
    total_os = len(df)


    # ======================================================
    # 8 Cabeçalho visual
    # ======================================================
    contas = df["conta"].dropna().unique()
    conta = contas[0] if len(contas) == 1 else "MISTO"

    if conta.upper() == "AMAZONET":
        logo_path = "app/img/amazonet.png"
    elif conta.upper() == "MANIA":
        logo_path = "app/img/mania.png"
    else:
        logo_path = None

    periodo_txt = f"{data_inicio:%d/%m} - {data_fim:%d/%m}"
    pagamento_txt = f"{data_pagamento:%d/%m/%Y}"

    if "LOBATOS" in tecnico_selecionado.upper():
        nome_exibicao = "Leidinaldo Lobato da Fonseca"
    else:
        # Remove sufixos como _TEC_TERC_MAO ou similares
        nome_exibicao = tecnico_selecionado.split("_")[0]

    def formatar_brl(valor):
        try:
            return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return "0,00"

    col1, col2 = st.columns([3, 2])

    with col1:
        cols = st.columns([1, 5])
        if logo_path and Path(logo_path).exists():
            cols[0].image(logo_path, width=150)

        cols[1].markdown(
            "<div style='text-align:center;font-size:28px;font-weight:700;'>Resumo Instalações</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div style='background:#f2f2f2;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>"
            f"Técnico: {nome_exibicao}</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div style='background:#f2f2f2;padding:10px;border-radius:6px;text-align:center;font-weight:bold;'>"
            f"Total a Receber: R$ {formatar_brl(total_final)}</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(f"<div style='border:1px solid #ddd;padding:10px;text-align:center;'>Período: {periodo_txt}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#ffe066;padding:10px;text-align:center;'>Data de Pagamento: {pagamento_txt}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#1f4fd8;color:white;padding:10px;text-align:center;'>Empresa<br>{conta}</div>", unsafe_allow_html=True)

    # =============================== # Rodapé Financeiro # =============================== 
    aprovadas = (df["status_financeiro"] == "PAGO").sum() 
    reprovadas = (df["status_financeiro"] != "PAGO").sum() 
    st.markdown( f""" <div style="font-size:12px; color:gray; text-align:right; margin-top:10px;"> 
                ✔ Aprovadas: {aprovadas} &nbsp;&nbsp; ❌ Reprovadas: {reprovadas} </div> """,
                  unsafe_allow_html=True ), 
    st.markdown( f""" <div style=" display:flex; justify-content:space-between;
                 align-items:center; font-size:12px;
                 color:#666; margin-top:8px; "> <div> Total de OS: {total_os} </div> </div> """,
                   unsafe_allow_html=True ),

 
    # ======================================================
    # 9 Auditoria
    # ======================================================

    auditoria_df = df[
        [
            "codigo_cliente",
            "numero_ordem_servico",
            "usuario_fechamento",
            "status_auditoria",
            "status_financeiro",
            "valor_a_pagar",
        ]   
    ].copy()

    auditoria_df = auditoria_df.reset_index(drop=True).reset_index()
    auditoria_df.rename(columns={"index": "Nº"}, inplace=True)
    auditoria_df["Nº"] = auditoria_df["Nº"] + 1

    st.dataframe(auditoria_df, width="stretch")

    
    def status_financeiro(status):
        status = str(status).upper().strip()
        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"
        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)

    df["valor_a_pagar"] = df.apply(
        lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else 0,
        axis=1,
    )


    if st.button("📄 Gerar Relatório do Técnico"):
        caminho = montar_tabela(
            df=auditoria_df,                  # tabela final auditada
            tecnico=nome_exibicao,      # nome do técnico
            empresa=conta,              # empresa
            data_inicio=data_inicio,    # data inicial do período
            data_fim=data_fim,          # data final do período
            data_pagamento=data_pagamento, # data de pagamento
            total_valor=total_final, # total a receber
            logo_path=logo_path,        # logo
        )

        with open(caminho, "rb") as f:
            st.download_button(
                "⬇️ Baixar PDF",
                f,
                file_name=caminho.split("/")[-1],
                mime="application/pdf",
            )
    # Somente técnicos que NÃO são Nadinei podem gerar recibo
    if "NADINEI" not in nome_exibicao.upper():

        if st.button("🧾 Gerar Recibo"):
            caminho_recibo = gerar_recibo_pagamento(
                tecnico=nome_exibicao,
                empresa=conta,
                valor=total_final,              # ✅ agora bate com a função
                data_pagamento=data_pagamento,
                qtd_instalacoes=len(auditoria_df),
            )

            with open(caminho_recibo, "rb") as f:
                st.download_button(
                    "⬇️ Baixar Recibo",
                    f,
                    file_name=caminho_recibo.split("/")[-1],
                    mime="application/pdf",
                )


    

