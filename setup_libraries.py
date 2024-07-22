import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

libraries = [
    "PyMuPDF",  # fitz
    "pytesseract",
    "Pillow",  # PIL
    "PyQt6",
    "threading",  # standard library, no need to install
    "os",  # standard library, no need to install
    "json",  # standard library, no need to install
    "datetime",  # standard library, no need to install
    "glob",  # standard library, no need to install
    "prompt_analysis",  # Assume this is a local module
    "retrieve_text_from_pdf",  # Assume this is a local module
    "retrieve_text_from_bildirim",  # Assume this is a local module
    "pdf_reader",  # Assume this is a local module
    "dateutil",
    "pandas",
    "nltk",
    "sklearn",
    "numpy",
    "thefuzz",
    "requests",
    "beautifulsoup4",  # bs4
    "traceback",  # standard library, no need to install
]

for lib in libraries:
    try:
        print(f"Installing {lib}...")
        install(lib)
        print(f"{lib} installed successfully.")
    except Exception as e:
        print(f"Failed to install {lib}: {e}")

print("All libraries installed.")
