def classificar_grupo(nome_grupo):
    nome = nome_grupo.upper()

    if "COMERCIAL" in nome and "INTERNO" in nome:
        return "COMERCIAL_INTERNO"
    if "COMERCIAL" in nome and "EXTERNO" in nome:
        return "COMERCIAL_EXTERNO"
    if "RECEP" in nome:
        return "RECEPCAO"
    if "INSTALA" in nome:
        return "PRODUCAO_INSTALACAO"
    if "SUPORTE" in nome:
        return "PRODUCAO_SUPORTE"

    return None
