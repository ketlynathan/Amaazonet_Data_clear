from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import cm
from pathlib import Path
from io import BytesIO
from num2words import num2words


# ======================================================
# DADOS DA EMPRESA
# ======================================================
def get_dados_empresa(empresa: str):
    empresa = empresa.upper()

    if empresa == "MANIA":
        return {
            "nome": "MANIA TELECOM TELECOMUNICACOES LTDA",
            "email": "contato@maniatelecom.com.br",
            "logo": "app/img/mania.png",
        }

    elif empresa == "AMAZONET":
        return {
            "nome": "Amazonet Telecomunicações Ltda.",
            "email": "contato@amazonett.com.br",
            "logo": "app/img/amazonet.png",
        }

    else:
        raise ValueError("Empresa não reconhecida")


# ======================================================
# GERADOR PRINCIPAL
# ======================================================
def gerar_recibo_pagamento(
    tecnico: str,
    empresa: str,
    valor_total: float,
    qtd_instalacoes: int,
    data_pagamento: str,
    tipo_servico="Serviços"
):
    dados_empresa = get_dados_empresa(empresa)

    empresa_nome = dados_empresa["nome"]
    empresa_email = dados_empresa["email"]
    logo_path = dados_empresa["logo"]

    valor_extenso = num2words(valor_total, lang="pt_BR").replace(" , ", "e ").capitalize()
    if not valor_extenso.lower().endswith("reais"):
        valor_extenso += " reais"

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )


    styles = getSampleStyleSheet()

    estilo_normal = ParagraphStyle("normal", parent=styles["Normal"], fontSize=9)
    estilo_bold = ParagraphStyle("bold", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold")
    estilo_valor = ParagraphStyle(
        "valor",
        parent=styles["Normal"],
        fontSize=12,
        fooutntName="Helvetica-Bold",
        alignment=TA_RIGHT
    )

    story = []


    for _ in range(2):  # duas vias
        story += bloco_cabecalho(
            empresa_nome=empresa_nome,
            empresa_email=empresa_email,
            logo_path=logo_path,
            valor_total=valor_total,
            styles=styles,
        )

        story += bloco_corpo(
            empresa_nome=empresa_nome,
            tecnico=tecnico,
            valor_extenso=valor_extenso,
            qtd_instalacoes=qtd_instalacoes,
            data_pagamento=data_pagamento,
            estilo_normal=estilo_normal,
            estilo_bold=estilo_bold,
            tipo_servico=tipo_servico,
        )

        

        story.append(Spacer(1, 120))

    doc.build(story)
    buffer.seek(0)
    return buffer




# ======================================================
# CABEÇALHO COM LOGO, EMPRESA E RECIBO
# ======================================================
def bloco_cabecalho(
    empresa_nome,
    empresa_email,
    logo_path,
    valor_total,
    styles,
):
    # Logo
    logo = Image(logo_path, width=4 * cm, height=4 * cm)

    # Estilo Empresa
    estilo_empresa_nome = ParagraphStyle(
        "empresa_nome",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    )

    estilo_empresa_endereco = ParagraphStyle(
        "empresa_endereco",
        parent=styles["Normal"],
        fontSize=8,
        leading=9,
        alignment=TA_CENTER,
    )

    texto_endereco = f"""
    Rua: Figueiredo Pimentel, nº 140, Jorge Teixeira CEP: 69088-563<br/>
    Fone: (92) 3090-6868<br/>
    E-mail: {empresa_email}<br/>
    Manaus-AM
    """

    # Estilo Recibo
    estilo_valor = ParagraphStyle(
        "estilo_valor",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#000000"),
    )

    valor_formatado = f"{valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Monta a coluna RECIBO
    coluna_valor = [
        Paragraph("<b>RECIBO</b>", estilo_valor),
        Spacer(1, 6),
        Paragraph(f"R$ {valor_formatado}", estilo_valor),
    ]

    # Monta a tabela com 3 colunas
    tabela = Table(
        [
            [
                logo,
                [
                    Paragraph(empresa_nome, estilo_empresa_nome),
                    Paragraph(texto_endereco, estilo_empresa_endereco),
                ],
                coluna_valor,
            ]
        ],
        colWidths=[3.5 * cm, 12 * cm, 3 * cm],  # Ajuste largura conforme necessidade
    )

    tabela.setStyle(
    TableStyle(
        [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("ALIGN", (2, 0), (2, 0), "CENTER"),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
            ("TOPPADDING", (0,0), (-1,0), 5),    # aumenta espaço acima do texto
            ("BOTTOMPADDING", (0,0), (-1,0), 1), # aumenta espaço abaixo do texto
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
    

    return [tabela, Spacer(1, 12)]


# ======================================================
# CORPO
# ======================================================
def bloco_corpo(
    empresa_nome,
    tecnico,
    valor_extenso,
    qtd_instalacoes,
    data_pagamento,
    tipo_servico,
    estilo_normal,
    estilo_bold,
):
    dados = [
        ["CÓDIGO PAGAMENTO:", "1", "DATA:", data_pagamento, "1 VIA EMPRESA"],
        ["RECEBI DA EMPRESA:", empresa_nome, "", "", ""],
        ["A QUANTIA DE:", valor_extenso, "", "", ""],
        ["REFERENTE A:", f"{qtd_instalacoes} {tipo_servico.upper()}", "", "", ""],
        ["RECEBEDOR:", tecnico, "", "", ""],
        ["ASSINATURA DO RECEBEDOR:", "", "", "", ""],
    ]

    tabela = Table(
        dados,
        colWidths=[170, 80, 80, 80, 120],
        rowHeights=[None, None, None, None, None, 1.5 * cm]
    )

    tabela.setStyle(TableStyle([
        ("SPAN", (1, 1), (-1, 1)),
        ("SPAN", (1, 2), (-1, 2)),
        ("SPAN", (1, 3), (-1, 3)),
        ("SPAN", (1, 4), (-1, 4)),
        ("SPAN", (1, 5), (-1, 5)),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0,0), (-1,0), 2),    # aumenta espaço acima do texto
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEBELOW", (1, 5), (-1, 5), 1, colors.black),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),   # primeira coluna (cabeçalhos) à esquerda
        ("ALIGN", (1, 0), (-1, -1), "CENTER") # valores centralizados
]))
   

    return [tabela]
