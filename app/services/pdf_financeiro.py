from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf_financeiro(df, tecnico, data_inicio, data_fim, total):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate("financeiro.pdf")

    story = []

    story.append(Paragraph("RESUMO DE INSTALAÇÕES – FINANCEIRO", styles["Title"]))
    story.append(Paragraph(f"Técnico: {tecnico}", styles["Normal"]))
    story.append(Paragraph(f"Período: {data_inicio:%d/%m} a {data_fim:%d/%m}", styles["Normal"]))
    story.append(Paragraph(f"TOTAL A PAGAR: R$ {total:,.2f}", styles["Normal"]))

    data = [["ID", "Cliente", "OS", "Técnico", "Status", "Financeiro", "Valor"]]

    for _, r in df.iterrows():
        data.append([
            r["id"],
            r["codigo_cliente"],
            r["numero_ordem_servico"],
            r["usuario_fechamento"],
            r["status_auditoria"],
            r["status_financeiro"],
            f"R$ {r['valor_a_pagar']:.2f}"
        ])

    story.append(Table(data))
    doc.build(story)
