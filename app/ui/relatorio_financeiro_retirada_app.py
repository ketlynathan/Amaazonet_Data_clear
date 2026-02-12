import streamlit as st
import pandas as pd
from datetime import timedelta
from pathlib import Path

from app.analysis.Financeiro.financeiro_rules_retirada import carregar_planilha_39
from app.analysis.pdf.pdf_relatorio import montar_tabela
from app.analysis.pdf.pdf_recibo import gerar_recibo_pagamento
from app.utils.formatacao import limpar_nome_tecnico
from app.utils.formatacao import carregar_logo_seguro



# ========================= UTILITÁRIOS =========================
def valor_por_estado(estado: str) -> int:
    if estado == "AM":
        return 35
    if estado == "PA":
        return 30
    return 0


def criar_chave(df: pd.DataFrame, col_cliente="codigo_cliente", col_os="numero_ordem_servico") -> pd.Series:
    return (
        df[col_cliente].astype(str).str.strip().str.upper() +
        "|" +
        df[col_os].astype(str).str.strip().str.upper()
    )


def st_card(texto, tamanho=16, padding=10, largura="100%", bg=None, color=None):
    tema = st.get_option("theme.base")
    bg_card = bg or ("#333333" if tema == "dark" else "#f2f2f2")
    color_text = color or ("#FFFFFF" if tema == "dark" else "#222222")
    st.markdown(
        f"<div style='background:{bg_card};color:{color_text};padding:{padding}px;"
        f"border-radius:6px;text-align:center;font-weight:bold;font-size:{tamanho}px;"
        f"width:{largura}; margin-bottom:5px;'>{texto}</div>",
        unsafe_allow_html=True
    )


# ========================= CARREGAMENTO E PREPARO =========================
def preparar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 📅 Converter datas
    if "data_termino_executado" in df.columns:
        df["data_termino_executado"] = pd.to_datetime(
            df["data_termino_executado"],
            dayfirst=True,
            errors="coerce"
        )
    else:
        df["data_termino_executado"] = pd.NaT

    # 🌎 ESTADO VINDO DA CIDADE (já que API não manda estado)
    MAPA_CIDADE_ESTADO = {
        "MANAUS": "AM",
        "ITACOATIARA": "AM",
        "PARINTINS": "AM",
        "MANACAPURU": "AM",
        "BELÉM": "PA",
        "ANANINDEUA": "PA",
        "SANTARÉM": "PA",
    }

    if "cidade" in df.columns:
        df["estado"] = (
            df["cidade"]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()
            .map(MAPA_CIDADE_ESTADO)
            .fillna("")
        )
    else:
        df["estado"] = ""

    # 🔑 Criar chave única
    df["chave"] = criar_chave(df)

    return df



def carregar_sheet_39(data_pagamento, tecnico_exibicao=None) -> pd.DataFrame:
    sheet_39 = carregar_planilha_39().copy()
    sheet_39["data_planilha"] = pd.to_datetime(sheet_39.iloc[:, 1], dayfirst=True, errors="coerce")
    
    if tecnico_exibicao:
        sheet_39["tecnico"] = sheet_39.iloc[:, 5].astype(str).str.strip().apply(limpar_nome_tecnico)
        sheet_39 = sheet_39[
            (sheet_39["data_planilha"] == data_pagamento) &
            (sheet_39["tecnico"] == tecnico_exibicao)
        ]
    
    sheet_39 = sheet_39.iloc[:, [3, 4]].copy()
    sheet_39.columns = ["codigo_cliente", "numero_ordem_servico"]
    sheet_39["chave"] = criar_chave(sheet_39)
    return sheet_39


# ========================= AUDITORIA =========================
def auditoria_manual(df: pd.DataFrame):
    pendentes = df[df["status_auditoria"] == "PENDENTE"].copy()
    if pendentes.empty:
        return df

    st.markdown("### 🧩 Auditoria Manual das Pendentes")
    painel = pendentes[["codigo_cliente", "numero_ordem_servico", "estado", "status_auditoria"]].copy()
    painel["status_auditoria"] = ""

    painel_editado = st.data_editor(
        painel,
        use_container_width=True,
        column_config={
            "status_auditoria": st.column_config.SelectboxColumn(
                "Definir Status",
                options=["", "APROVADO", "REPROVADO"]
            )
        },
        key="auditoria_manual_pendentes"
    )

    for _, row in painel_editado.iterrows():
        mask = (
            (df["codigo_cliente"] == row["codigo_cliente"]) &
            (df["numero_ordem_servico"] == row["numero_ordem_servico"])
        )
        if row["status_auditoria"] == "APROVADO":
            df.loc[mask, "status_auditoria"] = "APROVADO"
            df.loc[mask, "status_financeiro"] = "PAGO"
            df.loc[mask, "valor_a_pagar"] = df.loc[mask, "estado"].apply(valor_por_estado)
        elif row["status_auditoria"] == "REPROVADO":
            df = df[~mask]
    return df


# ========================= RENDERIZAÇÃO =========================
def render_relatorio_financeiro_retirada():

    if "df_fechamento_filtrado" not in st.session_state:
        st.warning("Carregue o fechamento técnico primeiro.")
        return

    df = preparar_dataframe(st.session_state["df_fechamento_filtrado"])
    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

    # Datas
    data_inicio = st.session_state.get("periodo_inicio")
    data_fim = st.session_state.get("periodo_fim")

    if not data_inicio or not data_fim:
        st.warning("Período não definido.")
        st.stop()

    # garante pegar o dia inteiro
    data_fim = data_fim + timedelta(days=1) - timedelta(seconds=1)

    df_periodo = df[
        (df["data_termino_executado"] >= data_inicio) &
        (df["data_termino_executado"] <= data_fim)
    ]

    data_pagamento = (data_fim + timedelta(days=1)).normalize()

    # Planilha 39 para pagamento
    sheet_39_pagamento = carregar_sheet_39(data_pagamento)
    chaves_planilha = set(sheet_39_pagamento["chave"])

    # Status automático
    df["status_auditoria"] = df["chave"].apply(lambda x: "APROVADO" if x in chaves_planilha else "PENDENTE")
    df["status_financeiro"] = df["status_auditoria"].apply(lambda x: "PAGO" if x == "APROVADO" else "-")
    df["valor_a_pagar"] = df.apply(lambda r: valor_por_estado(r["estado"]) if r["status_auditoria"] == "APROVADO" else 0, axis=1)

    # Auditoria manual
    tecnico_base = df["usuario_fechamento"].dropna().iloc[0] if "usuario_fechamento" in df.columns else ""
    nome_exibicao = limpar_nome_tecnico(tecnico_base)
    df = auditoria_manual(df)

    # Comparação Planilha x Relatório
    sheet_39_filtrada = carregar_sheet_39(data_pagamento, tecnico_exibicao=nome_exibicao)
    df_periodo = df[(df["data_termino_executado"] >= data_inicio) & (df["data_termino_executado"] <= data_fim)]
    
    chaves_planilha = set(sheet_39_filtrada["chave"])
    chaves_relatorio = set(df_periodo["chave"])

    so_planilha = chaves_planilha - chaves_relatorio
    so_relatorio = chaves_relatorio - chaves_planilha

    st.markdown("### 🔍 Conferência Planilha 39 x Relatório")
    col1, col2 = st.columns(2)
    col1.info(f"📄 OS na Planilha: **{len(chaves_planilha)}**")
    col2.info(f"🖥️ OS no Relatório: **{len(chaves_relatorio)}**")

    # Totais
    df["valor_a_pagar"] = pd.to_numeric(df["valor_a_pagar"], errors="coerce").fillna(0)
    total_final = df["valor_a_pagar"].sum()
    conta = df["conta"].dropna().unique()
    conta = conta[0] if len(conta) == 1 else "MISTO"
    
    periodo_txt = f"{data_inicio:%d/%m} - {data_fim:%d/%m}"
    pagamento_txt = f"{data_pagamento:%d/%m/%Y}"

    # ========================= CARDS ALINHADOS =========================
    st.markdown("<h2 style='text-align:center'>Resumo Financeiro – Retirada</h2>", unsafe_allow_html=True)

    col_esq1, col_dir1 = st.columns(2)
    with col_esq1:
        st_card(f"Técnico: {nome_exibicao}", tamanho=16)
        st_card(f"Total a Receber: R$ {total_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with col_dir1:
        st_card(f"Período: {periodo_txt}")
        st_card(f"Data de Pagamento: {pagamento_txt}", bg="#ffe066", color="#222")
        st_card(f"Empresa: {conta}", bg="#1f4fd8", color="#FFFFFF")

    # Tabela final
    auditoria_df = df[["codigo_cliente", "numero_ordem_servico", "usuario_fechamento",
                       "status_auditoria", "status_financeiro", "valor_a_pagar"]].copy()
    auditoria_df = auditoria_df.reset_index(drop=True)
    auditoria_df.insert(0, "Nº", auditoria_df.index + 1)
    st.dataframe(auditoria_df, use_container_width=True)
    st.success(f"💰 Total a pagar: R$ {total_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    tipo_relatorio = "retirada"
    # PDFs
    if st.button("📄 Gerar Relatório"):
        pdf_buffer = montar_tabela(
            auditoria_df,
            nome_exibicao,
            conta,
            data_inicio,
            data_fim,
            data_pagamento,
            total_final,
            tipo_servico=tipo_relatorio,
            logo_path=carregar_logo_seguro(conta)
        )

        st.download_button(
            "⬇️ Baixar PDF",
            data=pdf_buffer,
            file_name=f"Relatorio_{nome_exibicao}.pdf",
            mime="application/pdf"
        )


    

    if st.button("🧾 Gerar Recibo"):
        pdf_buffer = gerar_recibo_pagamento(
            tecnico=nome_exibicao,
            empresa=conta,
            valor_total=total_final,
            qtd_instalacoes=len(df[df["status_financeiro"] == "PAGO"]),
            data_pagamento=data_pagamento.strftime("%d/%m/%Y"),
            tipo_servico=tipo_relatorio
        )

        st.download_button(
            "⬇️ Baixar Recibo",
            data=pdf_buffer,
            file_name=f"Recibo_{nome_exibicao}.pdf",
            mime="application/pdf"
        )

