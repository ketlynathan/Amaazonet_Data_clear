from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import black
from reportlab.platypus import Image, Spacer
from io import BytesIO
import os
import re
from app.utils.formatacao import carregar_logo_seguro, limpar_nome_tecnico




def formatar_brl(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"
    


def montar_tabela(
    df,
    tecnico,
    empresa,
    data_inicio,
    data_fim,
    data_pagamento,
    total_valor,
    tipo_servico,   # 👈 NOVO
    logo_path=None
):

    tecnico = limpar_nome_tecnico(tecnico)
    nome_limpo = limpar_nome_tecnico(tecnico)
    
    buffer = BytesIO()  # 🔥 cria PDF na memória

    doc = SimpleDocTemplate(
        buffer,  # 🔥 usa o buffer em vez de caminho de arquivo
        pagesize=A4,
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
    empresa_upper = (empresa or "").upper()

    if "AMAZON" in empresa_upper:
        logo_path = "app/img/amazonet.png"
        cor_empresa = colors.HexColor("#413371")

    elif "MANIA" in empresa_upper:
        logo_path = "app/img/mania.png"
        cor_empresa = colors.HexColor("#2A7E9D")

    else:
        logo_path = None
        cor_empresa = colors.HexColor("#1f4fd8")


    # =========================
    # TOPO (LOGO SEGURO)
    # =========================
    tipo = str(tipo_servico).strip().lower()

    mapa_titulos = {
        "instalações": "RESUMO INSTALAÇÕES",
        "instalacoes": "RESUMO INSTALAÇÕES",
        "retirada": "RESUMO RETIRADAS",
        "retiradas": "RESUMO RETIRADAS",
        "venda": "RESUMO VENDAS",
        "vendas": "RESUMO VENDAS",
        "suporte": "RESUMO SUPORTE",
    }
    logo = carregar_logo_seguro(logo_path, largura=4.2*cm, altura=3.5*cm)

    titulo_texto = mapa_titulos.get(
        str(tipo_servico).lower(),
        f"RESUMO {str(tipo_servico).upper()}"
    )

    titulo = Paragraph(
        titulo_texto,
        ParagraphStyle(
            "Titulo",
            parent=styles["Normal"],
            fontSize=20,
            fontName="Helvetica-Bold",
            textColor=cor_empresa,
            alignment=TA_CENTER
        )
    )
    
    
    tabela_topo = Table(
    [[logo, titulo, ""]],
    colWidths=[4.5*cm, 9*cm, 4.5*cm]  # esquerda | centro | direita (espelho)
)
    #tabela_topo = Table([[logo, titulo]], colWidths=[5*cm, 10*cm])

    tabela_topo.setStyle(TableStyle([
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

    ("ALIGN", (0,0), (0,0), "LEFT"),
    ("ALIGN", (1,0), (1,0), "CENTER"),
    ("ALIGN", (2,0), (2,0), "RIGHT"),

    # 👇 DESCE SOMENTE A LOGO
    ("TOPPADDING", (0,0), (0,0), 15),

    # Mantém o resto normal
    ("TOPPADDING", (1,0), (2,0), 0),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),

    ("BOX", (0,0), (-1,-1), 0, colors.white),
    ("GRID", (0,0), (-1,-1), 0, colors.white),
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
    estilo_label = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=11,
        textColor=black,
        spaceAfter=2,
    )

    estilo_valor = ParagraphStyle(
        "Valor",
        parent=styles["Normal"],
        fontSize=11,
    )

    estilo_total = ParagraphStyle(
        "Total",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        spaceBefore=6,
    )

    bloco_info = Table(
    [
        [
            Paragraph(f"Técnico: <b>{tecnico}</b>", estilo_valor),
            Paragraph(
                f"Período: <b>{data_inicio:%d/%m} – {data_fim:%d/%m}</b>",
                estilo_valor
            ),
        ],
        [
            Paragraph(
                f"Total a receber: <b>R$ {formatar_brl(total_valor)}</b>",
                estilo_valor
            ),
            Paragraph(
                f"Pagamento: <b>{data_pg}</b>",
                estilo_valor
            ),
        ],
    ],
    colWidths=[10*cm, 8.5*cm],
)


    bloco_info.setStyle(TableStyle([

    # GRID invisível
    ("GRID", (0,0), (-1,-1), 0, colors.white),

    # Fundos padronizados
    ("BACKGROUND", (0,0), (0,0), colors.HexColor("#f2f2f2")),  # Técnico
    ("BACKGROUND", (1,0), (1,0), colors.HexColor("#f2f2f2")),  # Período
    ("BACKGROUND", (0,1), (0,1), colors.HexColor("#f2f2f2")),  # Total
    ("BACKGROUND", (1,1), (1,1), colors.HexColor("#f2f2f2")),  # Pagamento

    # Espaçamento interno
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),

    # Alinhamentos
    ("ALIGN", (1,0), (1,0), "RIGHT"),   # Período
    ("ALIGN", (1,1), (1,1), "RIGHT"),   # Pagamento
]))

    elementos.append(bloco_info)
    elementos.append(Spacer(1, 0.5*cm))



    # =========================
    # TABELA
    # =========================
    data = [[
        "Nº","EMPRESA","CLIENTE","CÓD O.S",
        "TÉCNICO","STATUS","FINANCEIRO","VALOR"
    ]]

    for i, r in enumerate(df.itertuples(), 1):
        data.append([
            Paragraph(str(i), estilo_tabela),
            Paragraph(empresa, estilo_tabela),
            Paragraph(str(r.codigo_cliente), estilo_tabela),
            Paragraph(str(r.numero_ordem_servico), estilo_tabela),
            Paragraph(limpar_nome_tecnico(r.usuario_fechamento), estilo_tabela),
            Paragraph(str(r.status_auditoria), estilo_tabela),
            Paragraph(str(r.status_financeiro), estilo_tabela),
            Paragraph(formatar_brl(r.valor_a_pagar), estilo_tabela),
        ])

    tabela = Table(data, repeatRows=1, colWidths=[
        0.8*cm, 2.2*cm, 1.8*cm, 3.5*cm, 4*cm, 2.5*cm, 2.2*cm, 1.5*cm
    ])
 
    tabela.setStyle(TableStyle([
        # Cabeçalho
        ("BACKGROUND", (0, 0), (-1, 0), cor_empresa),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),

        # 👉 CORPO DA TABELA (AQUI)
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),

        # Valor alinhado à direita (boa prática financeira)
        ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),

        # Grid
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    elementos.append(tabela)
    doc.build(elementos)

    buffer.seek(0)   # volta para o início do arquivo em memória
    return buffer    # retorna o PDF pronto para download
