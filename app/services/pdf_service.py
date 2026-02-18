import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from flask import current_app

def generate_invoice_pdf(invoice, user):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(name='BusinessName', fontSize=18, leading=22, fontName='Helvetica-Bold', textColor=colors.HexColor("#0a2540")))
    styles.add(ParagraphStyle(name='InvoiceTitle', fontSize=32, leading=38, fontName='Helvetica-Bold', alignment=2, textColor=colors.HexColor("#0a2540")))
    styles.add(ParagraphStyle(name='ClientHeader', fontSize=10, leading=12, fontName='Helvetica-Bold', textColor=colors.grey))
    
    elements = []

    logo = None
    logo_filename = invoice.logo_path or user.organization.logo_path
    if logo_filename:
        # Check static uploads
        # If stored as relative path 'uploads/...'
        logo_full_path = os.path.join(current_app.root_path, 'static', logo_filename)
        if not os.path.exists(logo_full_path):
             # Try just filename in static/uploads
             if os.path.basename(logo_filename) == logo_filename:
                  logo_full_path = os.path.join(current_app.root_path, 'static', 'uploads', logo_filename)

        if os.path.exists(logo_full_path):
            logo = Image(logo_full_path, 1*inch, 1*inch)
            logo.hAlign = 'LEFT'

    business_info = [
        [Paragraph(user.organization.name or user.username, styles['BusinessName'])],
        [Paragraph(user.organization.address or "", styles['Normal'])]
    ]
    
    header_data = [
        [logo if logo else "", business_info, Paragraph("INVOICE", styles['InvoiceTitle'])]
    ]
    header_table = Table(header_data, colWidths=[1.2*inch, 3*inch, 2.8*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 40))

    info_data = [
        [Paragraph("BILL TO:", styles['ClientHeader']), Paragraph("INVOICE DETAILS:", styles['ClientHeader'])],
        [Paragraph(f"<b>{invoice.client.name}</b><br/>{invoice.client.email}", styles['Normal']), 
         Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}<br/><b>Issue Date:</b> {invoice.issue_date.strftime('%d %b %Y')}<br/><b>Due Date:</b> {invoice.due_date.strftime('%d %b %Y')}", styles['Normal'])]
    ]
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    data = [['Description', 'Quantity', 'Rate', 'Amount']]
    for item in invoice.items:
        data.append([item.description, f"{item.quantity:g}", f"{item.rate:,.2f}", f"{item.amount:,.2f}"])
    
    subtotal = sum(item.amount for item in invoice.items)
    
    table = Table(data, colWidths=[4*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#475569")),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor("#cbd5e1")),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    totals_data = [
        ['', 'Subtotal:', f"{subtotal:,.2f} {invoice.currency}"],
        ['', f'Tax:', f"{sum(i.tax_amount for i in invoice.items):,.2f} {invoice.currency}"],
        ['', 'TOTAL:', f"{invoice.amount:,.2f} {invoice.currency}"]
    ]
    totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (1, 2), (2, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 2), (2, 2), 14),
        ('TEXTCOLOR', (1, 2), (2, 2), colors.HexColor("#0055ff")),
        ('TOPPADDING', (1, 2), (2, 2), 10),
    ]))
    elements.append(totals_table)

    if invoice.notes or invoice.terms:
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("NOTES & TERMS:", styles['ClientHeader']))
        elements.append(Paragraph(f"{invoice.notes}<br/><br/>{invoice.terms}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
