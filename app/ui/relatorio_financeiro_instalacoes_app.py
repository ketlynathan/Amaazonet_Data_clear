import streamlit as st
import pandas as pd
from datetime import timedelta
from app.services.financeiro_rules import aplicar_regras_financeiras



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
    # 2️⃣ Aplica regras financeiras
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

    tecnico_selecionado = st.selectbox("Selecione", tecnicos)

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
         df["data_termino_executado"], dayfirst=True, errors="coerce" ) 
    
    data_fim = df["data_termino_executado"].max() 
    data_inicio = data_fim - timedelta(days=5) 

    #if pd.notnull(data_fim) 
       # else None 
    data_pagamento = data_fim + timedelta(days=1) 
    #if pd.notnull(data_fim) else None


    # ======================================================
    # 5️⃣ Controle de duplicidade por cliente
    # ======================================================

    df = df.copy()

    # ==============================
    # 1️⃣ Remove duplicados técnicos
    # (mesmo cliente + mesma OS)
    # ==============================
    df = (
        df
        .sort_values("data_termino_executado", ascending=False)
        .drop_duplicates(
            subset=["codigo_cliente", "numero_ordem_servico"],
            keep="first"
        )
        .reset_index(drop=True)
    )

    # ==============================
    # 2️⃣ Marca clientes com múltiplas OS
    # ==============================
    df["CLIENTE_REPETIDO"] = (
        df.groupby("codigo_cliente")["numero_ordem_servico"]
        .transform("nunique") > 1
    )

    # ==============================
    # 3️⃣ Mostra apenas duplicados reais
    # ==============================
    dup = df[df["CLIENTE_REPETIDO"]]

    if not dup.empty:
        st.warning("⚠️ Clientes com mais de uma OS detectados")

        opcoes = (
            dup
            .apply(lambda r: f"{r['codigo_cliente']} | OS {r['numero_ordem_servico']}", axis=1)
            .unique()
            .tolist()
        )

        remover = st.multiselect(
            "Selecione quais OS devem ser removidas",
            opcoes
        )

        if remover:
            remover_os = [x.split("OS")[1].strip() for x in remover]

            # Remove somente as OS selecionadas
            df = df[~df["numero_ordem_servico"].astype(str).isin(remover_os)]

            # Recalcula duplicidade após remoção
            df["CLIENTE_REPETIDO"] = (
                df.groupby("codigo_cliente")["numero_ordem_servico"]
                .transform("nunique") > 1
            )

    # ======================================================
    # 6️⃣ Total financeiro
    # ======================================================
    df["valor_a_pagar"] = pd.to_numeric(df["valor_a_pagar"], errors="coerce").fillna(0)

    total_final = df["valor_a_pagar"].sum()

    total_final = df["valor_a_pagar"].sum()
    total_os = len(df)

    # ======================================================
    # 7️⃣ CABEÇALHO VISUAL (ESTILO RELATÓRIO PROFISSIONAL)
    # ======================================================

    from pathlib import Path

    # ===============================
    # Define logo por conta
    # ===============================
    contas = df["conta"].dropna().unique()

    if len(contas) == 1:
        conta = contas[0]
    else:
        conta = "MISTO"

    if conta.upper() == "AMAZONET":
        logo_path = "app/img/amazonet.png"
    elif conta.upper() == "MANIA":
        logo_path = "app/img/mania.png"
    else:
        logo_path = None


    # ===============================
    # Datas formatadas
    # ===============================
    data_pagamento = data_fim + timedelta(days=1)

    periodo_txt = f"{data_inicio:%d/%m} - {data_fim:%d/%m}"
    pagamento_txt = f"{data_pagamento:%d/%m/%Y}"

    # ===============================
    # Nome do técnico
    # ===============================
    nome_exibicao = (
        "Leidinaldo Lobato da Fonseca"
        if "LOBATOS" in tecnico_selecionado.upper()
        else tecnico_selecionado
    )

    # ===============================
    # Cabeçalho visual
    # ===============================
    col1, col2 = st.columns([3, 2])

    with col1:
        cols = st.columns([1, 5])
        if logo_path and Path(logo_path).exists():
            cols[0].image(logo_path, width=150)

        cols[1].markdown(
            """
            <div style="
                text-align:center;
                font-size:28px;
                font-weight:700;
                margin-top:10px;
            ">
                Resumo Instalações
            </div>
            """,
            unsafe_allow_html=True
        )
        def formatar_brl(valor):
            try:
                valor = float(valor)
            except:
                return "0,00"

            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(
            f"""
            <div style="
                background-color:#f2f2f2;
                color:#222;
                padding:10px;
                border-radius:6px;
                text-align:center;
                font-weight:bold;
                font-size:16px;
                margin-top:5px;
            ">
                Técnico: {nome_exibicao}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div style="
                background-color:#f2f2f2;
                color:#222;
                padding:10px;
                border-radius:6px;
                text-align:center;
                font-weight:bold;
                font-size:16px;
                margin-top:5px;
            ">
                Total a Receber:  R$ {formatar_brl(total_final)}
            </div>
            """,
            unsafe_allow_html=True
        )

            

    with col2: 
        st.markdown(
            f"""
            <div style="
                border:1px solid #ddd;
                padding:10px;
                border-radius:6px;
                text-align:center;
                font-weight:bold;
                font-size:16px;
                margin-bottom:8px;
                background-color:transparent;
            ">
                Período: {periodo_txt}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="
                background-color:#ffe066;
                padding:10px;
                border-radius:6px;
                text-align:center;
                font-weight:bold;
                font-size:16px;
            ">
                Data de Pagamento : {pagamento_txt}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="
                background-color:#1f4fd8;
                color:white;
                padding:10px;
                border-radius:6px;
                text-align:center;
                font-weight:bold;
                font-size:16px;
                margin-top:10px;
            ">
                Empresa<br>{conta}
            </div>
            """,
            unsafe_allow_html=True
        )
        

    st.divider()

    # ===============================
    # Rodapé Financeiro
    # ===============================
    aprovadas = (df["status_financeiro"] == "PAGO").sum()
    reprovadas = (df["status_financeiro"] != "PAGO").sum()

    st.markdown( 
        f""" 
        <div style="font-size:12px; 
        color:gray; text-align:right; 
        margin-top:10px;"> 
        ✔ Aprovadas: {aprovadas} &nbsp;&nbsp; 
        ❌ Reprovadas: {reprovadas} </div> 
        """, unsafe_allow_html=True 
        ), 
    st.markdown( 
          f"""
    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        font-size:12px;
        color:#666;
        margin-top:8px;
    ">
        <div>
            Total de OS: {total_os}
        </div>
    </div>
    """,
            unsafe_allow_html=True
        ),



    # ======================================================
    # 8️⃣ Auditoria
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

    auditoria_df = auditoria_df.reset_index(drop=True)
    auditoria_df.index += 1

    st.dataframe(auditoria_df, width="stretch")
    
    from reportlab.lib.pagesizes import A4, landscape
    from app.services.pdf_financeiro import gerar_pdf_financeiro

    # ======================================================
    # PREPARA DADOS DA TABELA (formatação BRL)
    # ======================================================

   
    df_pdf = df.copy()

    df_pdf["valor_a_pagar"] = pd.to_numeric(df_pdf["valor_a_pagar"], errors="coerce").fillna(0)

    # ======================================================
    # BOTÃO DE GERAR PDF
    # ======================================================

    st.markdown("---")

    if st.button("📄 Gerar PDF do Técnico"):

        caminho = gerar_pdf_financeiro(
            df=df_pdf,  # envia o dataframe inteiro (já tratado)
            tecnico=nome_exibicao,
            empresa=conta,
            periodo=f"{data_inicio:%d/%m/%Y} - {data_fim:%d/%m/%Y}",
            data_pagamento=f"{data_pagamento:%d/%m/%Y}",
            total_os=total_os,
            total_valor=formatar_brl(total_final),
            logo_path=logo_path,
        )

        with open(caminho, "rb") as f:
            st.download_button(
                "⬇️ Baixar PDF",
                f,
                file_name=caminho.split("/")[-1],
                mime="application/pdf",
            )


