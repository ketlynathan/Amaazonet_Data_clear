import pandas as pd
import streamlit as st
from datetime import timedelta
from app.analysis.google_sheets import read_sheet_as_dataframe


# ======================================================
# 📄 Cache – Planilha 60
# ======================================================
@st.cache_data(ttl=600)
def carregar_planilha_60_venda():
    # Agora usamos a chave "39" do seu sheet_map
    return read_sheet_as_dataframe("60_venda")


# ======================================================
# 💰 Função principal de regras financeiras
# ======================================================
def aplicar_regras_financeiras(
    df: pd.DataFrame,
    data_inicio=None,
    data_fim=None,
) -> pd.DataFrame:

    df = df.copy()

    df["codigo_cliente"] = df["codigo_cliente"].astype(str).str.strip().str.upper()
    df["numero_ordem_servico"] = df["numero_ordem_servico"].astype(str).str.strip().str.upper()
    df["estado"] = df["dados_endereco_instalacao.estado"].astype(str).str.upper()
    df["servico_status"] = df["dados_servico.servico_status"].astype(str).str.upper()

    # Se não existir ainda, cria como pendente
    if "status_auditoria" not in df.columns:
        df["status_auditoria"] = "PENDENTE"

    # Status financeiro
    df["status_financeiro"] = df["status_auditoria"].apply(
        lambda x: "PAGO" if x == "APROVADO" else "-"
    )

    def valor_por_estado(estado):
        if estado == "AM": return 35
        if estado == "PA": return 30
        return 0

    df["valor_a_pagar"] = df.apply(
        lambda row: valor_por_estado(row["estado"]) if row["status_auditoria"] == "APROVADO" else 0,
        axis=1
    )

    df["alerta_servico"] = df["servico_status"].apply(
        lambda x: "⚠️ Serviço Habilitado" if x == "SERVIÇO HABILITADO" else ""
    )

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    return df



