import pandas as pd
import unicodedata
from app.analysis.Financeiro.financeiro_sources import carregar_planilhas_financeiro
from app.analysis.Financeiro.financeiro_utils import padronizar_campos_chave


import unicodedata

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    return texto

    base_autonomos["tipo_vendedor"] = base_autonomos["tipo_vendedor"].apply(normalizar_texto)
    tipo_escolhido = normalizar_texto(tipo_escolhido)



def garantir_colunas(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
    return df


def aplicar_regras(df_base):
    df_base = padronizar_campos_chave(df_base)

    s60, stm = carregar_planilhas_financeiro()
    base_vendedores = pd.concat([s60, stm], ignore_index=True)

    df = df_base.merge(
        base_vendedores,
        on=["codigo_cliente", "numero_ordem_servico"],
        how="left"
    )

    # Status financeiro
    df["status_auditoria"] = df["status_planilha"].fillna("").astype(str).str.strip().str.upper()

    def status_financeiro(status):
        status = str(status).upper().strip()
        return "PAGO" if status in ["APROVADO", "N.C APROVADO", "NC APROVADO"] else "-"

    df["status_financeiro"] = df["status_planilha"].apply(status_financeiro)

    # Valor por vendedor
    def valor_base(nome, tipo):
        nome = normalizar_texto(nome)
        tipo = normalizar_texto(tipo)
        if "AUTONOMO" in tipo:
            if "JOSIVAN" in nome:
                return 60
            return 50
        return 0

    df["valor_base"] = df.apply(lambda r: valor_base(r["nome_vendedor"], r["tipo_vendedor"]), axis=1)
    df["valor_a_pagar"] = df.apply(lambda r: r["valor_base"] if r["status_financeiro"] == "PAGO" else 0, axis=1)

    total_por_vendedor = (
        df.groupby("nome_vendedor", dropna=False)["valor_a_pagar"]
        .sum()
        .reset_index()
        .sort_values("valor_a_pagar", ascending=False)
    )

    # ✅ FILTRA VENDEDORES AUTÔNOMOS
    autonomos = df[df["tipo_vendedor"].str.upper().str.contains("AUTONOMO")].copy()

    return {
        "base_completa": df,
        "total_por_vendedor": total_por_vendedor,
        "autonomos": autonomos  # <-- aqui está a chave que faltava
    }
