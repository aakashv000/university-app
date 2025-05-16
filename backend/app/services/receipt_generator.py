from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

def generate_receipt_pdf(payment, student, student_fee, receipt_number, output_path=None):
    """
    Generate a PDF receipt for a payment
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=1,  # Center alignment
        spaceAfter=0.3*inch
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=0.2*inch
    )
    
    normal_style = styles["Normal"]
    
    # Create content elements
    elements = []
    
    # Add title
    elements.append(Paragraph("UNIVERSITY FEE RECEIPT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add receipt information
    elements.append(Paragraph(f"Receipt Number: {receipt_number}", header_style))
    elements.append(Paragraph(f"Date: {payment.payment_date.strftime('%d-%m-%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add student information
    elements.append(Paragraph("Student Information", header_style))
    student_data = [
        ["Name:", student.full_name],
        ["Email:", student.email],
        ["Student ID:", str(student.id)]
    ]
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add payment information
    elements.append(Paragraph("Payment Information", header_style))
    payment_data = [
        ["Payment ID:", str(payment.id)],
        ["Payment Method:", payment.payment_method],
        ["Transaction ID:", payment.transaction_id or "N/A"],
        ["Semester:", student_fee.semester.name],
        ["Fee Description:", student_fee.description or "Tuition Fee"],
        ["Amount Paid:", f"${payment.amount:.2f}"],
    ]
    payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Add footer
    elements.append(Paragraph("Thank you for your payment.", normal_style))
    elements.append(Paragraph("This is a computer-generated receipt and does not require a signature.", normal_style))
    
    # If output_path is provided, save to disk
    if output_path:
        # Build the PDF to disk
        doc.build(elements)
        return output_path
    else:
        # Build the PDF to memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        doc.build(elements)
        buffer.seek(0)
        return buffer
