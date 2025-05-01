from Code.mes_fonctions import *
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

def extraire_ampliations(texte: str) -> dict:
    # Cherche la ligne contenant "AMPLIATIONS : ..."
    ampliations_section = re.search(r"AMPLIATIONS\s*:\s*(.+)", texte, re.IGNORECASE)

    if not ampliations_section: 
        # Si la section n’est pas trouvée, retourne un dictionnaire vide
        return {}

    contenu = ampliations_section.group(1)  # Récupère le contenu après "AMPLIATIONS :"

    # Sépare les éléments de la liste d'ampliations par le séparateur ";"
    items = re.split(r'\s*;\s*', contenu)

    ampliations = {}
    for item in items:
        # Pour chaque élément, cherche un destinataire suivi d’un nombre
        match = re.match(r"(.+?)\s+(\d+)", item.strip())
        if match:
            destinataire = match.group(1).strip()         # Nom du destinataire
            exemplaires = int(match.group(2))             # Nombre d'exemplaires
            ampliations[destinataire] = exemplaires       # Ajoute au dictionnaire

    return ampliations


def extract_relevant_text(text):
    """
    Extrait le bloc de texte situé entre 'Fait à' et 'AMPLIATIONS'
    """
    pattern = r"Fait à[^\n]*\n(.*?)\nAMPLIATIONS[^\n]*"
    match = re.search(pattern, text, re.DOTALL)  # DOTALL pour inclure les retours à la ligne dans .
    return match.group(1) if match else None     # Retourne le bloc si trouvé, sinon None


def extraire_annexe(texte):
    """
    Extrait le contenu situé après le mot-clé [sign], supposé représenter la fin du document.
    """
    match = re.search(r'\[sign\](.*)', texte)

    if match:
        contenu_annexe = match.group(1).strip()  # Récupère ce qu'il y a après [sign]
        return {"annexe": contenu_annexe}
    else:
        return {"annexe": ""}  # Si rien trouvé, retourne un champ vide


def normaliser_texte(texte):
    """
    Nettoie le texte en supprimant les accents et les caractères spéciaux,
    sans affecter la casse des majuscules.
    """
    texte = texte.lower()  # Convertit en minuscules
    texte = unicodedata.normalize('NFKD', texte).encode('ASCII', 'ignore').decode('utf-8')  # Supprime les accents
    texte = texte.replace("’", "'").replace("‘", "'").replace("`", "'")  # Remplace certaines apostrophes
    texte = re.sub(r"\s+", " ", texte)  # Supprime les sauts de ligne et espaces multiples
    return texte


def nettoyer_nom(nom):
    """
    Supprime les accents dans un nom sans changer la casse.
    """
    nom = unicodedata.normalize('NFKD', nom).encode('ASCII', 'ignore').decode('utf-8')
    return nom


def est_majuscule(nom):
    """
    Vérifie si un nom est entièrement en majuscules.
    """
    return nom.isupper()


def formater_nom(nom):
    """
    Met en forme un nom : garde les majuscules si déjà en majuscules,
    sinon met en majuscule la première lettre de chaque mot.
    """
    if est_majuscule(nom):
        return nom
    else:
        return nom.strip().title()


def associer_ministeres_et_noms(texte_extrait, ministeres_mots_cles):
    """
    Associe les ministères détectés à partir des mots-clés et
    extrait les noms (ex : prénom NOM) des signataires.
    """
    if not texte_extrait:
        return {}

    # Étape 1 : normaliser le texte pour faciliter la recherche des mots-clés
    texte_normalise = normaliser_texte(texte_extrait)

    # Initialisation avec la Présidence toujours incluse
    ministeres_detectes = ["Présidence de la République"]
    for ministere, cles in ministeres_mots_cles.items():
        for mot in cles:
            mot_norm = normaliser_texte(mot)
            # Si un mot-clé est trouvé dans le texte, on ajoute le ministère
            if re.search(rf"\b{mot_norm}\b", texte_normalise) and ministere not in ministeres_detectes:
                ministeres_detectes.append(ministere)
                break

    # Étape 2 : Extraire les noms de type "Prénom NOM" (NOM en majuscules)
    pattern_nom = r"\b([A-Z][a-zéèêàîôïûùç'’\-]+(?:\s[A-Z][a-z]+)*\.?)\s+([A-Z]{2,}(?:\s[A-Z]{2,})*)"
    noms_detectes = re.findall(pattern_nom, texte_extrait)

    # Nettoyer et formater chaque nom détecté
    noms_formates = []
    for prenom, nom in noms_detectes:
        nom_nettoye = nettoyer_nom(nom)
        noms_formates.append(f"{prenom} {formater_nom(nom_nettoye)}")

    # Générer le dictionnaire de résultat
    resultat_json = {
        "Entités Signataires ": ministeres_detectes,
        "Ont signé ": noms_formates
    }

    return resultat_json




# --- 4. Sauvegarde du résultat dans un fichier TXT
def save_results_txt(preambule, articles, output_file="resultats.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        # Sauvegarde des préambules
        f.write("Préambule:\n")
        for p in preambule:
            f.write(f"Numéro: {p['numero']}\nDate: {p['date']}\nContenu: {p['contenu']}\n\n")

        # Sauvegarde des articles
        f.write("Articles:\n")
        for article in articles:
            f.write(f"Article: {article['article']}\nType: {article['type']}\nPage: {article['page']}\nContenu: {article['contenu']}\n\n")

    print(f"Résultats sauvegardés dans le fichier {output_file}")
