from Code.mes_fonctions import *
from Code.mes_fonctions_suite import *
from Code.mots_cles import *

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
import spacy
import re
import os
import json
import unicodedata

# Configuration manuelle de Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Charger le modèle français de spaCy
nlp = spacy.load("fr_core_news_md")

def extract_text_from_scanned_pdf(pdf_path):
    """
    Extrait le texte d’un fichier PDF scanné
    
    pdf_path: Chemin vers le fichier PDF scanné.
    return: Texte extrait, page par page, séparé avec des entêtes.
    """
    doc = fitz.open(pdf_path)  # Ouvre le fichier PDF avec fitz
    results = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)  # Charge la page actuelle
        pix = page.get_pixmap(dpi=300)     # Rend l’image de la page à haute résolution (300 DPI)
        img = Image.open(io.BytesIO(pix.tobytes("png")))  # Convertit l’image en objet PIL.Image pour OCR

        #  OCR avec reconnaissance française
        try:
            text = pytesseract.image_to_string(img, lang="fra")  
        except pytesseract.TesseractError as e:
            print(f"Erreur Tesseract sur la page {page_number + 1} : {e}")
            text = "[Erreur OCR]"

        # Symbole pour signifir la présence de signature sur le fichier
        if "signature" in text.lower() or "signé" in text.lower():
            text += "\n\n[sign]" 
        results.append(f"--- Page {page_number + 1} ---\n{text.strip()}")

    return "\n\n".join(results)  # Retourne le tout sous forme de chaîne, avec séparation entre les pages


def nettoyer_texte(texte: str) -> str:
    """
    Nettoie le texte OCR pour le rendre plus lisible.
    
    texte: Texte brut issu de l’OCR.
    :return: Texte nettoyé.
    """
    texte = texte.replace('\xa0', ' ')  
    texte = re.sub(r'[ \t]+', ' ', texte)  
    texte = re.sub(r'\n{2,}', '\n', texte)  
    texte = texte.strip() 
    return texte
