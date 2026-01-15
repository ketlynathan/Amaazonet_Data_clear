from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import os
import re


def formatar_brl(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"


def montar_tabela(df, tecnico, empresa, data_inicio, data_fim, data_pagamento, total_valor, logo_path=None):

    caminho_pdf = f"Resumo_{tecnico.replace(' ', '_')}.pdf"

    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize= A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm
    )

    elementos = []
    styles = getSampleStyleSheet()

    # =========================
    # ESTILOS
    # =========================
    estilo_normal = ParagraphStyle("normal", parent=styles["Normal"], fontSize=10)
    estilo_bold = ParagraphStyle("bold", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold")
    estilo_tabela = ParagraphStyle("tabela", parent=styles["Normal"], fontSize=9, leading=11)

    # =========================
    # IDENTIDADE DA EMPRESA
    # =========================
    empresa_upper = empresa.upper()

    if "AMAZON" in empresa_upper:
        logo_path = "app/img/amazonet.png"
        cor_empresa = colors.HexColor("#413371")
    elif "MANIA" in empresa_upper:
        logo_path = "app/img/mania.png"
        cor_empresa = colors.HexColor("#2A7E9D")
    else:
        cor_empresa = colors.HexColor("#1f4fd8")

    # =========================
    # TOPO
    # =========================
    logo = Image(logo_path, width=3.5*cm, height=1.6*cm) if logo_path and os.path.exists(logo_path) else ""

    titulo = Paragraph(
        "RESUMO INSTALAÇÕES",
        ParagraphStyle(
            "Titulo",
            parent=styles["Normal"],
            fontSize=14,
            fontName="Helvetica-Bold",
            textColor=cor_empresa,
            alignment=TA_CENTER
        )
    )
    

    tabela_topo = Table([[logo, titulo]], colWidths=[5*cm, 7*cm])

    tabela_topo.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (2,0), (2,0), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))

    elementos.append(tabela_topo)
    elementos.append(Spacer(1, 0.3*cm))


    # =========================
    # TÉCNICO / EMPRESA
    # =========================

    data_pg = data_pagamento.strftime("%d/%m/%Y") if hasattr(data_pagamento, "strftime") else str(data_pagamento)
    # ===============================
    # BLOCO TÉCNICO | PERÍODO | TOTAL | DATA PAGAMENTO
    # ===============================

    bloco_info = Table(
        [
            [
                Paragraph(f"<b>Técnico:</b> {tecnico}", estilo_normal),
                Paragraph(f"<b>Período:</b> {data_inicio:%d/%m} - {data_fim:%d/%m}", estilo_normal)
            ],
            [
                Paragraph(f"<b>TOTAL A RECEBER:</b> R$ {formatar_brl(total_valor)}",
                        ParagraphStyle(
                            "TotalDestaque",
                            parent=styles["Normal"],
                            fontSize=12,
                            fontName="Helvetica-Bold"
                        )),
                Paragraph(f"<b>Data de Pagamento:</b> {data_pg}", estilo_normal)
            ]
        ],
        colWidths=[11*cm, 7*cm]
    )

    bloco_info.setStyle(TableStyle([

        # GRID invisível
        ("GRID", (0,0), (-1,-1), 0, colors.white),

        # Técnico
        ("BACKGROUND", (0,0), (0,0), colors.HexColor("#f2f2f2")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),

        # Total a Receber (amarelo)
        ("BACKGROUND", (0,1), (0,1), colors.HexColor("#ffe066")),
        ("BOX", (0,1), (0,1), 1, cor_empresa),

        # Data de pagamento (amarelo suave)
        ("BACKGROUND", (1,1), (1,1), colors.HexColor("#fff3a0")),

        # Alinhamento
        ("ALIGN", (1,0), (1,0), "RIGHT"),   # período
        ("ALIGN", (1,1), (1,1), "RIGHT"),   # data pagamento
    ]))

    elementos.append(bloco_info)
    elementos.append(Spacer(1, 0.5*cm))



    # =========================
    # TABELA
    # =========================
    data = [[
        "Nº","EMPRESA","CÓD CLIENTE","CÓD O.S",
        "TÉCNICO","STATUS","FINANCEIRO","VALOR"
    ]]

    for i, r in enumerate(df.itertuples(), 1):
        data.append([
            Paragraph(str(i), estilo_tabela),
            Paragraph(empresa, estilo_tabela),
            Paragraph(str(r.codigo_cliente), estilo_tabela),
            Paragraph(str(r.numero_ordem_servico), estilo_tabela),
            Paragraph(str(r.usuario_fechamento).replace("_TEC_TERC_MAO", ""), estilo_tabela),
            Paragraph(str(r.status_auditoria), estilo_tabela),
            Paragraph(str(r.status_financeiro), estilo_tabela),
            Paragraph(formatar_brl(r.valor_a_pagar), estilo_tabela),
        ])

    tabela = Table(data, repeatRows=1, colWidths=[
        1*cm, 2.1*cm, 2.3*cm, 3.5*cm, 3.8*cm, 2.2*cm, 2.2*cm, 1.5*cm
    ])
 
    tabela.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), cor_empresa),
        ("TEXTCOLOR",(0,0),(-1,0), colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.black),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,0),(-1,0),"CENTER"),
        ("ALIGN",(0,1),(0,-1),"CENTER"),
        ("ALIGN",(-1,1),(-1,-1),"RIGHT"),
        ("LEFTPADDING",(0,0),(-1,-1),4),
        ("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))

    elementos.append(tabela)
    doc.build(elementos)

    return caminho_pdf
