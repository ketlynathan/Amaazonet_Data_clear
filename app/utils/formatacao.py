import pandas as pd
from pathlib import Path
import re

def limpar_nome_tecnico(nome):
    if not nome:
        return ""

    nome = str(nome)
    nome = nome.replace("\n", " ").replace("\r", " ")

    if "LOBATOS" in nome.upper():
        return "Leidinaldo Lobato da Fonseca"

    nome = re.split(r"_", nome)[0]
    nome = re.split(r"\b(TEC|TECNICO|MAO|MÃO|TERC|TÉC)\b", nome, flags=re.IGNORECASE)[0]
    nome = re.sub(r"\s+", " ", nome).strip()

    return nome.title()


def limpar_cpf(cpf):
    return re.sub(r"\D", "", str(cpf))


def carregar_autonomos(caminho_csv=None):
    if caminho_csv is None:
        caminho_csv = Path(__file__).resolve().parent / "autonomos.csv"

    df_auto = pd.read_csv(caminho_csv, dtype=str)

    df_auto.columns = df_auto.columns.str.strip().str.upper()
    df_auto["CPF"] = df_auto["CPF"].apply(lambda x: re.sub(r"\D", "", str(x)).zfill(11))

    return set(df_auto["CPF"].unique())
