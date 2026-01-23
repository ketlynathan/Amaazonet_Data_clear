import re

def limpar_nome_tecnico(nome):
    if not nome:
        return ""

    nome = str(nome)
    nome = nome.replace("\n", " ").replace("\r", " ")

    # 🔥 REGRA ESPECIAL LOBATOS
    if "LOBATOS" in nome.upper():
        return "Leidinaldo Lobato da Fonseca"

    nome = re.split(r"_", nome)[0]
    nome = re.split(r"\b(TEC|TECNICO|MAO|MÃO|TERC|TÉC)\b", nome, flags=re.IGNORECASE)[0]
    nome = re.sub(r"\s+", " ", nome).strip()

    return nome.title()
