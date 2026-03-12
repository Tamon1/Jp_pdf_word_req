import io
import fitz
import pytesseract
from PIL import Image
import os

if not os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    raise RuntimeError("Tesseract not found")

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
print(pytesseract.pytesseract.tesseract_cmd)

def ocr_pdf(pdf_bytes, dpi=250):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text += pytesseract.image_to_string(img, lang="jpn")

    return text
