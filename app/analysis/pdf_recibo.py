from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from num2words import num2words
from reportlab.lib.units import cm


def valor_extenso(v):
    return num2words(float(v), lang="pt_BR").replace(" vírgula zero zero", "") + " reais"


def gerar_recibo_pagamento(
        empresa,
        endereco,
        email,
        telefone,
        tecnico,
        qtd_instalacoes,
        valor,
        data_pagamento,
        codigo="001"
):
    nome_arquivo = f"Recibo_{tecnico.replace(' ','_')}.pdf"

    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    bold = ParagraphStyle("b", parent=styles["Normal"], fontName="Helvetica-Bold")
    centro = ParagraphStyle("c", parent=styles["Normal"], alignment=1)

    elementos = []

    def bloco_recibo():
        return [
            Paragraph(f"<b>{empresa}</b> &nbsp;&nbsp;&nbsp; <b>RECIBO</b>", bold),
            Paragraph(endereco),
            Paragraph(f"Fone: {telefone}"),
            Paragraph(f"E-mail: {email}"),
            Spacer(1, 0.6*cm),

            Paragraph(f"<b>R$ {valor:,.2f}</b>".replace(",", "X").replace(".", ",").replace("X", "."), 
                      ParagraphStyle("v", parent=styles["Normal"], fontSize=16, alignment=2)),
            Spacer(1, 0.4*cm),

            Paragraph(f"<b>CÓDIGO PAGAMENTO:</b> {codigo} &nbsp;&nbsp;&nbsp; <b>DATA:</b> {data_pagamento}", styles["Normal"]),
            Spacer(1, 0.4*cm),

            Paragraph(f"<b>RECEBI DA EMPRESA:</b> {empresa}", styles["Normal"]),
            Paragraph(f"<b>A QUANTIA DE:</b> {valor_extenso(valor)}", styles["Normal"]),
            Paragraph(f"<b>REFERENTE A:</b> {qtd_instalacoes} INSTALAÇÕES", styles["Normal"]),
            Paragraph(f"<b>RECEBEDOR:</b> {tecnico}", styles["Normal"]),
            Spacer(1, 1*cm),

            Paragraph("ASSINATURA DO RECEBEDOR: _________________________________________________", styles["Normal"]),
        ]

    # 1ª via
    elementos.extend(bloco_recibo())
    elementos.append(Spacer(1, 1.5*cm))

    # Linha de corte
    elementos.append(Paragraph("-"*120, centro))
    elementos.append(Spacer(1, 1.5*cm))

    # 2ª via
    elementos.extend(bloco_recibo())

    doc.build(elementos)

    return nome_arquivo
    

