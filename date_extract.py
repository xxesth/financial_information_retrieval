import fitz  # PyMuPDF
import re
from datetime import datetime
import pytesseract
from PIL import Image

def extract_dates_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    found_date = None
    
    for page_num in range(len(doc)):
        page_text = doc[page_num].get_text()
        dates = find_dates_in_text(page_text)
        
        if dates:
            found_date = dates[0]  # Assuming the first date found is the one we want
            break
    
    if found_date:
        extracted_dates = [found_date.strftime('%Y-%m-%d')]
    else:
        # Perform OCR for scanned PDFs
        extracted_dates = extract_dates_from_scanned_pdf(pdf_path)
    
    return extracted_dates

def find_dates_in_text(text):
    # Regex patterns for different date formats
    date_patterns = [
        r'\b(\d{1,2})[/\.](\d{1,2})[/\.](\d{4})\b',  # dd/mm/yyyy or dd.mm.yyyy
        r'\b(\d{1,2})\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+(\d{4})\b'  # dd month yyyy
    ]

    extracted_dates = []

    for pattern in date_patterns:
        regex = re.compile(pattern, re.IGNORECASE)
        matches = regex.findall(text)

        for match in matches:
            if len(match) == 3:
                if match[1].isdigit():
                    month = int(match[1])
                else:
                    month = {
                        'Ocak': 1, 'Şubat': 2, 'Mart': 3, 'Nisan': 4,
                        'Mayıs': 5, 'Haziran': 6, 'Temmuz': 7, 'Ağustos': 8,
                        'Eylül': 9, 'Ekim': 10, 'Kasım': 11, 'Aralık': 12
                    }[match[1].capitalize()]

                day = int(match[0])
                year = int(match[2])
                try:
                    extracted_dates.append(datetime(year, month, day))
                except ValueError:
                    pass  # Skip invalid dates

    return extracted_dates

def extract_dates_from_scanned_pdf(pdf_path):
    text = extract_text_from_scanned_pdf(pdf_path)
    dates = find_dates_in_text(text)
    
    return [date.strftime('%Y-%m-%d') for date in dates]

def extract_text_from_scanned_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(doc)):
        # Convert page to image
        page = doc[page_num]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        
        # Perform OCR on the image
        page_text = pytesseract.image_to_string(img, lang='tur')
        text += page_text + "\n"
    
    return text

