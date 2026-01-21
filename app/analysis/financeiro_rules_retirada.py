import pandas as pd
import os
import streamlit as st
from app.analysis.google_sheets import read_sheet_as_dataframe

# ======================================================
# Cache – Planilha 39
# ======================================================
@st.cache_data(ttl=600)
def carregar_planilha_39():
    sheet_id = os.getenv("GOOGLE_SPREADSHEET_ID_39")

    if not sheet_id:
        raise ValueError("GOOGLE_SPREADSHEET_ID_39 não definida no .env")

    return read_sheet_as_dataframe(sheet_id)


# ======================================================
# Função principal
# ======================================================
def aplicar_regras_financeiras(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ======================================================
    # 0️⃣ Carrega planilha 39
    # ======================================================
    sheet_39 = carregar_planilha_39()

    # ======================================================
    # 1️⃣ Normalização HUBSOFT
    # ======================================================
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip().str.upper()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip().str.upper()
    df["estado"] = df["dados_endereco_instalacao.estado"].astype(str).str.upper()
    df["servico_status"] = df["dados_servico.servico_status"].astype(str).str.upper()

    # ======================================================
    # 2️⃣ Normalização Planilha 39
    # H (3) Cliente | I (4) OS
    # ======================================================
    sheet_39 = sheet_39.iloc[:, [3, 4]].copy()
    sheet_39.columns = ["codigo_cliente", "numero_ordem_servico"]

    for c in sheet_39.columns:
        sheet_39[c] = sheet_39[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 3️⃣ Chave composta
    # ======================================================
    df["chave"] = df["codigo_cliente"] + "|" + df["numero_ordem_servico"]
    sheet_39["chave"] = sheet_39["codigo_cliente"] + "|" + sheet_39["numero_ordem_servico"]

    chaves_relatorio = set(df["chave"])
    chaves_39 = set(sheet_39["chave"])

    # ======================================================
    # 4️⃣ Alertas de divergência
    # ======================================================
    sobra_relatorio = chaves_relatorio - chaves_39
    sobra_planilha = chaves_39 - chaves_relatorio

    if sobra_relatorio:
        st.warning(f"⚠️ {len(sobra_relatorio)} OS no relatório NÃO estão na Planilha 39")

    if sobra_planilha:
        st.warning(f"⚠️ {len(sobra_planilha)} OS na Planilha 39 NÃO estão no relatório")

    # ======================================================
    # 5️⃣ Status auditoria
    # ======================================================
    df["status_auditoria"] = df["chave"].apply(
        lambda x: "APROVADO" if x in chaves_39 else "-"
    )

    # ======================================================
    # 6️⃣ Alerta Serviço Habilitado
    # ======================================================
    df["alerta_servico"] = df["servico_status"].apply(
        lambda x: "⚠️ Serviço Habilitado" if x == "SERVIÇO HABILITADO" else ""
    )

    # ======================================================
    # 7️⃣ Valor por estado
    # ======================================================
    def valor_por_estado(row):
        if row["status_auditoria"] != "APROVADO":
            return 0
        if row["estado"] == "AM":
            return 35
        if row["estado"] == "PA":
            return 30
        return 0

    df["valor_a_pagar"] = df.apply(valor_por_estado, axis=1)

    # ======================================================
    # 8️⃣ ID
    # ======================================================
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df
