import json
import os
from pdf_reader.extract import get_elements_from_pdf, ExtractedTable, PdfParagraph, ExtractedPdfElement
import random
import tempfile



def table_to_text(table):
    text_parts = []
    table_df_format = table.df_format()

    for row in table_df_format:
        text_parts.append(str(list(row.values())))
    return text_parts



def get_page_as_text(page):
    page_content = {"paragraphs": [], "tables": []}
    for element in page.paragraphs:
        if isinstance(element, ExtractedTable):
            page_content["tables"].append(table_to_text(element))
        elif isinstance(element, PdfParagraph):
            page_content["paragraphs"].append(str(element))
    return page_content



def get_pdf_as_text(filepath):
    pages = get_elements_from_pdf(filepath)
    document_content = {"pages": []}
    for page in pages:
        document_content["pages"].append(get_page_as_text(page))
    return document_content


def convert_pdf_to_json(pdf_path):
    # Generate a random seed (not necessarily needed unless used for something specific)
    random_seed = random.randint(1, 100000)

    try:
        # Create a temporary file with a .json extension
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        temp_file_name = temp_file.name

        # Close the file explicitly
        temp_file.close()

        # Convert PDF to structured content (assuming you have a function to extract text)
        document_content = get_pdf_as_text(pdf_path)


        # Save structured content to JSON file
        with open(temp_file_name, "w", encoding="utf-8") as f:
            json.dump(document_content, f, ensure_ascii=False, indent=4)

        return temp_file_name

    except OSError as e:
        print(f"Error: {e}")
        return None




