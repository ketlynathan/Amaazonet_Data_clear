from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import os


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
    logo = Image(logo_path, width=3.2 * cm, height=1.5 * cm) if logo_path and os.path.exists(logo_path) else Paragraph("")

    titulo = Paragraph("RESUMO FINANCEIRO", ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        textColor=cor_empresa
    ))

    data_pg = data_pagamento.strftime("%d/%m/%Y") if hasattr(data_pagamento, "strftime") else str(data_pagamento)

    bloco_datas = Paragraph(
        f"<b>PERÍODO:</b> {data_inicio:%d/%m} - {data_fim:%d/%m}<br/>"
        f"<font backColor='#fff176'><b>DATA PAGAMENTO:</b> {data_pg}</font>",
        ParagraphStyle("Datas", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER)
    )

    tabela_topo = Table([[logo, titulo, bloco_datas]], colWidths=[3.5*cm, 10*cm, 6*cm])
    tabela_topo.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
    elementos += [tabela_topo, Spacer(1, 0.4 * cm)]

    # =========================
    # TÉCNICO / EMPRESA
    # =========================
    elementos.append(Table([[
        Paragraph("<b>TÉCNICO:</b>", estilo_normal), Paragraph(tecnico, estilo_normal),
        Paragraph("<b>EMPRESA:</b>", estilo_normal), Paragraph(empresa, estilo_normal)
    ]], colWidths=[3*cm, 10*cm, 3*cm, 10*cm],
    style=[("BACKGROUND", (2,0), (3,0), colors.HexColor("#dbeafe"))]))

    elementos.append(Spacer(1, 0.25 * cm))

    # =========================
    # TOTAL A RECEBER
    # =========================
    tabela_total = Table([[
        Paragraph("<b>TOTAL A RECEBER:</b>", estilo_bold),
        Paragraph(f"<font backColor='#fff176'><b>R$ {formatar_brl(total_valor)}</b></font>",
                ParagraphStyle("Total", parent=styles["Normal"], fontSize=12))
    ]], colWidths=[6*cm, 8*cm])

    tabela_total.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "LEFT")
    ]))

    tabela_total.hAlign = "LEFT"

    elementos.append(tabela_total)

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
        1*cm, 2.4*cm, 2.2*cm, 3.1*cm, 4*cm, 2.5*cm, 2.2*cm, 2*cm
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
