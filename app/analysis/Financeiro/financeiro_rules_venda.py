import pandas as pd
import streamlit as st
from app.analysis.google_sheets import read_sheet_as_dataframe
from app.analysis.Financeiro.calculo_comissao import comissao_tecnico_autonomo, buscar_valor_meta

# ======================================================
# Carrega planilhas Google
# ======================================================
@st.cache_data(ttl=600)
def carregar_planilhas():
    sheet_51 = read_sheet_as_dataframe("51")
    sheet_60 = read_sheet_as_dataframe("60")
    sheet_51_stm = read_sheet_as_dataframe("51_STM")
    return sheet_51, sheet_60, sheet_51_stm


# ======================================================
# Função principal
# ======================================================
def aplicar_regras_financeiras(df: pd.DataFrame) -> pd.DataFrame:
    sheet_51, sheet_60, sheet_51_stm = carregar_planilhas()

    df = df.copy()
    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip()
    df["usuario_fechamento"] = df["usuario_fechamento"].astype(str)

    # ======================================================
    # 🟢 PLANILHA 51 STM
    # C = cliente | D = OS | K = info extra | X = status
    # ======================================================
    stm = sheet_51_stm.iloc[:, [2, 3, 10, 23]].copy()
    stm.columns = [
        "codigo_cliente",
        "numero_ordem_servico",
        "info_51_stm",
        "status_51_stm",
    ]

    for c in stm.columns:
        stm[c] = stm[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 🔵 PLANILHA 51
    # H = cliente | I = OS | D = info extra | Y = status
    # ======================================================
    s51 = sheet_51.iloc[:, [7, 8, 3, 24]].copy()
    s51.columns = [
        "codigo_cliente",
        "numero_ordem_servico",
        "info_51",
        "status_51",
    ]

    for c in s51.columns:
        s51[c] = s51[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 🟠 PLANILHA 60
    # D = cliente | E = OS | H = info extra | V = status
    # ======================================================
    s60 = sheet_60.iloc[:, [3, 4, 7, 21]].copy()
    s60.columns = [
        "codigo_cliente",
        "numero_ordem_servico",
        "info_60",
        "status_60",
    ]

    for c in s60.columns:
        s60[c] = s60[c].astype(str).str.strip().str.upper()

    # ======================================================
    # 🔗 MERGES
    # ======================================================
    df = df.merge(stm, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df = df.merge(s51, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df = df.merge(s60, on=["codigo_cliente", "numero_ordem_servico"], how="left")

    # ======================================================
    # 🧾 REGRA STATUS AUDITORIA
    # ======================================================
    def status_auditoria(row):
        tecnico = str(row["usuario_fechamento"]).upper()

        if "NADINEI" in tecnico and row["status_51_stm"]:
            return row["status_51_stm"]

        if row["status_51"]:
            return row["status_51"]

        if row["status_60"]:
            return row["status_60"]

        return ""

    df["status_auditoria"] = df.apply(status_auditoria, axis=1)

    # ======================================================
    # 💰 STATUS FINANCEIRO
    # ======================================================
    def status_financeiro(status):
        status = str(status).upper()
        if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"]:
            return "PAGO"
        return "-"

    df["status_financeiro"] = df["status_auditoria"].apply(status_financeiro)

    # total de vendas pagas por colaborador
    vendas_por_pessoa = (
        df[df["status_financeiro"] == "PAGO"]
        .groupby("colaborador")
        .size()
        .to_dict()
    )

    def calcular_comissao(row):
        if row["status_financeiro"] != "PAGO":
            return 0

        # regra técnico autônomo
        valor_autonomo = comissao_tecnico_autonomo(row)
        if valor_autonomo > 0:
            return valor_autonomo

        chave_meta = row["chave_meta"]  # ex: COMERCIAL_INTERNO_AM_MANAUS
        qtd = vendas_por_pessoa.get(row["colaborador"], 0)

        valor_por_venda = buscar_valor_meta(chave_meta, qtd)

        return valor_por_venda

    df["valor_comissao_unitaria"] = df.apply(calcular_comissao, axis=1)
    df["valor_comissao_total"] = df["valor_comissao_unitaria"]


    df["valor_base"] = df["usuario_fechamento"].apply(vendas_por_pessoa)

    df["valor_a_pagar"] = df.apply(
            lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else 0,
            axis=1,
        )

    # ======================================================
    # 🆔 ID FINAL
    # ======================================================
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df
