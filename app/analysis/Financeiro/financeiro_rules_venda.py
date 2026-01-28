import pandas as pd
import unicodedata
from app.analysis.Financeiro.financeiro_sources import carregar_planilhas_financeiro
from app.analysis.Financeiro.financeiro_utils import padronizar_campos_chave


def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    return texto


def aplicar_regras(df_base):
    df_base = padronizar_campos_chave(df_base)

    s60, stm = carregar_planilhas_financeiro()

    # =============================
    # 🧹 PADRONIZA TIPOS DE VENDEDOR
    # =============================

    s60["tipo_vendedor"] = s60["tipo_vendedor"].apply(normalizar_texto)

    # STM não tem tipo → forçamos como autônomo
    stm["tipo_vendedor"] = "VENDEDOR AUTONOMO"

    TIPOS_AUTONOMOS = [
        "VENDEDOR AUTONOMO",
        "VENDEDOR AUTONOMOS REGIONAIS",
        "VENDEDOR AUTONOMO REGIONAIS",
    ]

    s60_aut = s60[s60["tipo_vendedor"].isin(TIPOS_AUTONOMOS)].copy()
    stm_aut = stm.copy()

    # =============================
    # 🔗 BASE UNIFICADA DE AUTÔNOMOS
    # =============================

    colunas_padrao = [
        "codigo_cliente",
        "numero_ordem_servico",
        "nome_autonomo",
        "tipo_vendedor",
        "status"
    ]

    base_autonomos = pd.concat(
        [
            s60_aut[colunas_padrao],
            stm_aut[colunas_padrao],
            
        ],
        ignore_index=True
    )

    # =============================
    # 🔎 CRUZAMENTOS ORIGINAIS
    # =============================

    df_stm = df_base.merge(stm, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    df_60 = df_base.merge(s60, on=["codigo_cliente", "numero_ordem_servico"], how="left")
    


    resumo = pd.DataFrame({
        "codigo_cliente": df_base["codigo_cliente"],
        "numero_ordem_servico": df_base["numero_ordem_servico"],
        "encontrado_51_stm": df_stm["status_51_stm"].notna(),
        "encontrado_60": df_60["status_60"].notna(),
    })

    resumo["origem_encontrada"] = (
        resumo["encontrado_51_stm"].map({True: "51_STM", False: ""}) +
        resumo["encontrado_60"].map({True: " 60", False: ""})
    ).str.strip()

    return {
        "base": df_base,
        "51_STM": df_stm,
        "60": df_60,
        "autonomos": base_autonomos,   # 👈 NOVA BASE
        "resumo": resumo
    }
