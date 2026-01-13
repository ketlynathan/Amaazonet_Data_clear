from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os


def gerar_pdf_financeiro(
    df,
    tecnico,
    empresa,
    periodo,
    data_pagamento,
    total_os,
    total_valor,
    logo_path
):
    nome_arquivo = f"Financeiro_{tecnico.replace(' ', '_')}.pdf"
    caminho = os.path.join("temp", nome_arquivo)
    os.makedirs("temp", exist_ok=True)

    styles = getSampleStyleSheet()
    elementos = []

    # ============================
    # LOGO
    # ============================
    if logo_path and os.path.exists(logo_path):
        img = Image(logo_path, width=3*cm, height=3*cm)
        elementos.append(img)

    elementos.append(Spacer(1, 0.3*cm))

    # ============================
    # CABEÇALHO
    # ============================
    elementos.append(Paragraph("<b>Resumo de Instalações</b>", styles["Title"]))
    elementos.append(Paragraph(f"Técnico: {tecnico}", styles["Normal"]))
    elementos.append(Paragraph(f"Empresa: {empresa}", styles["Normal"]))
    elementos.append(Paragraph(f"Período: {periodo}", styles["Normal"]))
    elementos.append(Paragraph(f"Data de pagamento: {data_pagamento}", styles["Normal"]))
    elementos.append(Spacer(1, 0.4*cm))

    # ============================
    # TOTAIS
    # ============================
    elementos.append(Paragraph(f"<b>Total de OS:</b> {total_os}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Total a receber:</b> R$ {total_valor}", styles["Normal"]))
    elementos.append(Spacer(1, 0.4*cm))

    # ============================
    # TABELA
    # ============================
    dados = [["Cliente", "OS", "Status", "Valor"]]

    for _, r in df.iterrows():
        dados.append([
            r["codigo_cliente"],
            r["numero_ordem_servico"],
            r["status_financeiro"],
            f"R$ {r['valor_a_pagar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        ])

    tabela = Table(dados, colWidths=[5*cm, 4*cm, 4*cm, 3*cm])

    tabela.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, "#CCCCCC"),
        ("BACKGROUND", (0,0), (-1,0), "#eeeeee"),
        ("ALIGN", (-1,1), (-1,-1), "RIGHT"),
    ]))

    elementos.append(tabela)

    doc = SimpleDocTemplate(caminho, pagesize=A4)
    doc.build(elementos)

    return caminho
