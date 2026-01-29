import pandas as pd
from pathlib import Path
import re

from reportlab.platypus import Image, Spacer
from reportlab.lib.units import cm


def carregar_logo_seguro(logo_path, largura=4.2*cm, altura=3.5*cm):
    """
    Carrega logo de forma segura. Se não encontrar, retorna um Spacer para não quebrar o PDF.
    """
    if not logo_path:
        return Spacer(1, altura)

    caminho = Path.cwd() / logo_path
    if caminho.exists():
        return Image(str(caminho), width=largura, height=altura)

    print(f"⚠️ Logo não encontrada em: {caminho}")
    return Spacer(1, altura)

def get_dados_empresa(empresa: str):
    empresa = (empresa or "").upper()

    if "MANIA" in empresa:
        return {
            "nome": "MANIA TELECOM TELECOMUNICACOES LTDA",
            "email": "contato@maniatelecom.com.br",
            "logo": "app/img/mania.png",
            "cor": "#2A7E9D",
        }

    elif "AMAZON" in empresa:
        return {
            "nome": "Amazonet Telecomunicações Ltda.",
            "email": "contato@amazonett.com.br",
            "logo": "app/img/amazonet.png",
            "cor": "#413371",
        }

    else:
        return {
            "nome": empresa,
            "email": "",
            "logo": None,
            "cor": "#1f4fd8",
        }


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
