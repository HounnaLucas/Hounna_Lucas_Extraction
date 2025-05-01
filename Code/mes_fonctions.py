from Code.mes_fonctions_suite import *
from Code.mots_cles import *
from Code.traitement_texte import *

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
# 🔧 Configuration manuelle de Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Charger le modèle français de spaCy
nlp = spacy.load("fr_core_news_md")

# Fonction principale d’extraction des données de l'entête dans l’en-tête d’un décret
def extraire_metadonnees_entete(texte: str) -> dict:
    doc = nlp(texte)  # Analyse linguistique du texte avec spaCy

    # 1. Extraction du numéro du décret et de sa date de publication
    numero_match = re.search(r"(D[ÉE]CRET\s+N[°º]\s+[0-9]{4}\s?[—-]\s?[0-9]+)\s+DU\s+([0-9]{1,2}\s+\w+\s+[0-9]{4})", texte, re.IGNORECASE)
    numero_decret = numero_match.group(1).strip() if numero_match else None
    date_publication = numero_match.group(2).strip() if numero_match else None

    # 2. Institution émettrice (souvent le Président de la République)
    institution_match = re.search(r"(LE PRÉSIDENT DE LA RÉPUBLIQUE[^\n]+(?:\n[^\n]+){0,2})", texte, re.IGNORECASE)
    institution = institution_match.group(1).replace('\n', ', ').strip() if institution_match else None

    # 3. Objet du décret (ce sur quoi porte le décret)
    objet_match = re.search(r"(portant\s+[^\.\!\?]+[\.\!\?])", texte, re.IGNORECASE)
    objet = objet_match.group(1).strip() if objet_match else None

    # Construction du dictionnaire de sortie
    resultats = {
        "metadonnees": {
            "numero_decret": numero_decret,
            "date_publication": date_publication,
            "institution": institution,
            "objet": objet
        }
    }

    return resultats


def clean_text(text):  # Simple nettoyage temporaire
    return re.sub(r"[ \t]+", " ", text.strip())


# Convertit un numéro (ex: "1", "2e", "3") en version ordinale lisible ("premier", "deuxième", etc.)
def numero_en_ordinal(n):
    n = str(n).lower().strip()
    exceptions = {
        "1": "premier", "1er": "premier", "premier": "premier",
        "2": "deuxième", "2e": "deuxième", "deuxième": "deuxième",
        "3": "troisième", "troisième": "troisième",
    }

    if n in exceptions:
        return exceptions[n]
    
    try:
        num = int(''.join(filter(str.isdigit, n)))  # Garde uniquement les chiffres
    except ValueError:
        return f"{n}ᵉ"  # Si aucun chiffre détecté, retourne un ordinal simple
    
    # Cas standards au-delà de 3
    if num == 1:
        return "premier"
    elif num == 2:
        return "deuxième"
    elif num == 3:
        return "troisième"
    else:
        return f"{num}ᵉ"


# Extraction des textes du préambule commençant par "Vu"

def extract_preambule(text):
    preambule = []
    last_numero = ""
    
    try:
        # Tentative d'extraction du préambule structuré avec "Vu"
        preambule_block = re.search(
            r"(LE PRÉSIDENT DE LA RÉPUBLIQUE,.*?CHEF DU GOUVERNEMENT,)(.*?)(?=Article premier|DÉCRÈTE)",
            text, re.DOTALL
        )
        if preambule_block:
            # Extraction et traitement des lignes si le bloc est trouvé
            preambule_block = preambule_block.group(2).strip()
           
            lignes = [l.strip() for l in preambule_block.splitlines() if l.strip()]
            
            # Diviser le texte en sections par "Vu" ou autre séparation
            sections, current_section = [], ""
            for line in lignes:
               # if not line.lower().startswith("vu"):
                #    line = "vu " + line[0].lower() + line[1:]  # mettre la 1ère lettre en minuscule après Vu
                # print(line)
                if line.lower().startswith("vu"):
                    if current_section:
                        sections.append(current_section.strip())
                       
                    current_section = line
                   
                else:
                    current_section += " " + line
            if current_section:
                sections.append(current_section.strip())

            # Traitement des sections extraites
            for section in sections:
                contenu = section.strip()
                type_texte, numero, date = "", "", ""
                
                # Extraction du numéro et de la date
                match_numero = re.search(r"(loi|décret|décision|arrêté)\s*n[°ºo]?\s*(\d{4}-\d+|\d+)", contenu, re.IGNORECASE)
                if match_numero:
                    type_texte, numero = match_numero.group(1).lower(), match_numero.group(2)
                
                match_date = re.search(r"(\d{1,2})\s+([a-zéûèê]+)\s+(\d{4})", contenu, re.IGNORECASE)
                if match_date:
                    day, month, year = match_date.groups()
                    date = f"{day} {month} {year}"
                
                # Nettoyage du contenu et ajout à la liste
                contenu = re.sub(r"[;:]+$", "", contenu).strip()
                preambule.append({
                    "type": type_texte,
                    "numero": numero,
                    "date": date,
                    "contenu": contenu
                })
        
        
            else:
                print("❌ Aucun préambule trouvé.")
               

    except Exception as e:
        print("Erreur dans l'extraction du préambule:", e)

    return preambule

def extract_preambule2(text):
    preambule = []
    last_numero = ""
    
    try:
        # Tentative d'extraction du préambule structuré sans "Vu"
        preambule_block = re.search(
            r"(LE PRÉSIDENT DE LA RÉPUBLIQUE,.*?CHEF DU GOUVERNEMENT,)(.*?)(?=Article premier|DÉCRÈTE)",
            text, re.DOTALL
        )
        if preambule_block:
            preambule_block= re.sub(r'\bvu\b\s*', '', text, flags=re.IGNORECASE)
            # Si la structure "Vu" n'est pas trouvée, recherche plus complexe
            preambule_block = re.search(
                r"(LE PRÉSIDENT.*?CHEF DU GOUVERNEMENT,)(.*?)(proposition.*?|Conseil.*?|(?=Article premier|DÉCRÈTE))",
                text, re.DOTALL | re.IGNORECASE
            )
            
            if preambule_block:
                bloc_texte = preambule_block.group(2).strip()
                lignes = re.split(r"\n+", bloc_texte)
                lignes_regroupees, bloc_courant = [], ""
            

                # Regrouper les lignes par type (loi, décret, etc.)
                for ligne in lignes:                    
                    if re.match(r"^\s*(la|le|les)\s+(loi|décret|décision|arrêté)?", ligne.strip(), re.IGNORECASE):
                       
                        if bloc_courant:
                            lignes_regroupees.append(bloc_courant.strip())
                        bloc_courant = ligne.strip()
                    else:
                        bloc_courant += " " + ligne.strip()
                if bloc_courant:
                    lignes_regroupees.append(bloc_courant.strip())

                # Extraction des informations de chaque bloc
                for bloc in lignes_regroupees:
                    contenu = bloc.strip()
                    type_texte, numero, date = "", "", ""

                    match_numero = re.search(r"(loi|décret|décision|arrêté)?\s*n[°ºo]?\s*(\d{4}-\d+|\d+)", bloc, re.IGNORECASE)
                    if match_numero:
                        type_texte, numero = (match_numero.group(1) or "").lower(), match_numero.group(2)
                        last_numero = numero
                    else:
                        numero = last_numero

                    match_date = re.search(r"(\d{1,2})\s+([a-zéûèê]+)\s+(\d{4})", bloc, re.IGNORECASE)
                    if match_date:
                        day, month, year = match_date.groups()
                        date = f"{day} {month} {year}"

                    preambule.append({
                        "type": type_texte,
                        "numero": numero,
                        "date": date,
                        "contenu": contenu
                    })
            else:
                print("❌ Aucun préambule trouvé.")
                

    except Exception as e:
        print("Erreur dans l'extraction du préambule:", e)

    return preambule



# Extraction des articles à partir du bloc "DÉCRÈTE"
def extract_articles(text):
    articles = []
    pages = re.split(r"--- Page (\d+) ---", text)  # Séparation par pages
    pages_dict = {}

    # Création d’un dictionnaire associant numéro de page et contenu
    for i in range(1, len(pages), 2):
        page_num = int(pages[i])
        page_content = pages[i+1]
        pages_dict[page_num] = page_content

    full_text = " ".join(pages_dict.values())
    decret_block = re.split(r"DÉCRÈTE", full_text, flags=re.IGNORECASE)[-1]

    # Recherche des articles (numérotés ou "premier")
    matches = re.finditer(
        r"Article\s+(premier|\d{1,2}|[a-zéèêûî\-]+)\s*(.*?)(?=Article\s+(premier|\d{1,2}|[a-zéèêûî\-]+)\s|Fait à|$)",
        decret_block, flags=re.DOTALL | re.IGNORECASE
    )

    for match in matches:
        numero_brut = match.group(1)
        contenu = clean_text(match.group(2))
        article_type = detect_article_type(contenu)
        page = detect_page_for_article(pages_dict, match.group(0))

        articles.append({
            "article": numero_en_ordinal(numero_brut),
            "contenu": contenu,
            "type": article_type,
            "page": page
        })

    return articles

# Détection du type d'article en fonction des mots-clés
def detect_article_type(content):
    content_lower = content.lower()
    if "nomm" in content_lower:
        return "nomination"
    elif "interdit" in content_lower:
        return "interdiction"
    elif "rappel" in content_lower:
        return "rappel"
    elif "modifi" in content_lower:
        return "modification"
    else:
        return "autre"


# Détecte la page d'un article grâce à un extrait du texte
def detect_page_for_article(pages_dict, article_text):
    for page_num, content in pages_dict.items():
        if article_text[:40] in content:
            return page_num
    return None


# Extraction de mots-clés juridiques à partir du texte
def extract_legal_terms(text):
    doc = nlp(text)
    terms = set()

    keywords = {"décret", "article", "nomination", "loi", "attribution", "organisation", "fonctionnement",
                "ministre", "présidence", "interdiction", "révocation"}

    for token in doc:
        if token.text.lower() in keywords:
            terms.add(token.text.lower())

    return sorted(list(terms))
