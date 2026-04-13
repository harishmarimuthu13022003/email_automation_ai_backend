from fpdf import FPDF
import os
from datetime import datetime

class PDFService:
    @staticmethod
    def generate_invoice_pdf(data: dict):
        pdf = FPDF()
        pdf.add_page()
        
        # Set fonts
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(0, 20, "INVOICE", ln=True, align='C')
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Invoice ID: {data.get('invoice_id', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Client Details:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Name: {data.get('client_name')}", ln=True)
        pdf.cell(0, 10, f"Email: {data.get('client_email')}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Description: {data.get('description')}", ln=True)
        pdf.cell(0, 10, f"Due Date: {data.get('due_date')}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Total Amount: ${data.get('amount')}", ln=True, align='R')
        
        pdf.ln(20)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "Thank you for your business!", ln=True, align='C')
        
        # Ensure static folder exists
        os.makedirs("static/invoices", exist_ok=True)
        file_path = f"static/invoices/invoice_{data.get('invoice_id')}.pdf"
        pdf.output(file_path)
        return file_path
