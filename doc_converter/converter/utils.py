import os
from pdf2docx import Converter
from docx import Document
from reportlab.pdfgen import canvas
from openpyxl import load_workbook
import csv
from PIL import Image

def convert_file(file_path, target_format):
    base, ext = os.path.splitext(file_path)
    ext = ext.lower().strip(".")  # Normalize extensions
    converted_path = f"{base}.{target_format}"

    try:
        if ext == "pdf" and target_format == "docx":
            cv = Converter(file_path)
            cv.convert(converted_path)
            cv.close()

        elif ext == "docx" and target_format == "pdf":
            doc = Document(file_path)
            pdf = canvas.Canvas(converted_path)
            y = 800
            for para in doc.paragraphs:
                pdf.drawString(100, y, para.text)
                y -= 20
            pdf.save()

        elif ext == "txt" and target_format == "pdf":
            with open(file_path, "r", encoding="utf-8") as txt_file:
                pdf = canvas.Canvas(converted_path)
                y = 800
                for line in txt_file:
                    pdf.drawString(100, y, line.strip())
                    y -= 20
                pdf.save()

        elif ext == "png" and target_format == "pdf":
            image = Image.open(file_path)
            image.convert("RGB").save(converted_path)

        elif ext == "xlsx" and target_format == "pdf":
            workbook = load_workbook(file_path)
            sheet = workbook.active
            pdf = canvas.Canvas(converted_path)
            y = 800
            for row in sheet.iter_rows(values_only=True):
                pdf.drawString(100, y, " | ".join(map(str, row)))
                y -= 20
            pdf.save()

        elif ext == "xlsx" and target_format == "docx":
            workbook = load_workbook(file_path)
            sheet = workbook.active
            doc = Document()
            for row in sheet.iter_rows(values_only=True):
                doc.add_paragraph(" | ".join(map(str, row)))
            doc.save(converted_path)

        elif ext == "csv" and target_format == "pdf":
            with open(file_path, newline='', encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                pdf = canvas.Canvas(converted_path)
                y = 800
                for row in reader:
                    pdf.drawString(100, y, ", ".join(row))
                    y -= 20
                pdf.save()

        elif ext == "csv" and target_format == "docx":
            doc = Document()
            with open(file_path, newline='', encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    doc.add_paragraph(", ".join(row))
            doc.save(converted_path)

        else:
            raise ValueError(f"Conversion from {ext} to {target_format} is not supported.")

        return converted_path  # Return the path of the converted file
    
    except Exception as e:
        raise RuntimeError(f"Error converting {file_path}: {str(e)}")
