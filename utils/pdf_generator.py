from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from datetime import datetime

def create_sales_report_pdf(chart_image_data, start_date, end_date, products):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    title = Paragraph("Relatório de Vendas", title_style)
    elements.append(title)
    
    date_info = Paragraph(f"Período: {start_date} até {end_date}", styles["Normal"])
    elements.append(date_info)
    
    products_info = Paragraph(f"Produtos: {', '.join(products)}", styles["Normal"])
    elements.append(products_info)
    elements.append(Spacer(1, 20))
    
    with open("temp_chart.png", "wb") as f:
        f.write(chart_image_data)
    chart_image = Image("temp_chart.png", width=9*inch, height=6*inch)
    elements.append(chart_image)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf