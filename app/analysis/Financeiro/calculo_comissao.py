from .tabelas_metas import METAS

def buscar_valor_meta(chave_meta, quantidade):
    regras = METAS.get(chave_meta, [])

    for minimo, maximo, valor in regras:
        if minimo <= quantidade <= maximo:
            return valor

    return 0

def comissao_tecnico_autonomo(row):
    if row["tipo_tecnico"] == "AUTONOMO" and row["status_financeiro"] == "PAGO":
        return 50.0
    return 0.0
