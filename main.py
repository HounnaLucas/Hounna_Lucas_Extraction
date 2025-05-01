from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
import json

# Importe tes fonctions existantes
from Code.mes_fonctions import *
from Code.mes_fonctions_suite import *
from Code.mots_cles import *
from Code.traitement_texte import *
from model_yolo import *
app = FastAPI()

@app.post("/extract/")
async def extract_pdf(file: UploadFile = File(...)):
    try:
        # Sauvegarder temporairement le fichier
        temp_pdf_path = f"temp_{file.filename}"
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Lancer ton pipeline
        full_text = extract_text_from_scanned_pdf(temp_pdf_path)
        nettoyer_text = nettoyer_texte (full_text)
        entete= extraire_metadonnees_entete(full_text)
        # Extraction du préambule
        preambule = extract_preambule(nettoyer_text)        
        preambule2 = extract_preambule2(full_text)
        article = extract_articles(nettoyer_text)
        ampliations = extraire_ampliations(nettoyer_text)
        signataires = extract_relevant_text(nettoyer_text)
        termes_legaux = extract_legal_terms(nettoyer_text)
        annexe = extraire_annexe (nettoyer_text)
        resume = associer_ministeres_et_noms(signataires, ministeres_mots_cles)
        resultat = {
            "entete": entete["metadonnees"],
            "preambule": preambule,
            "preambules": preambule2,
            "articles": article,
            "ampliations": ampliations,
            "Signataires" : resume,
            "annexe" : annexe,
            "termes_legaux": termes_legaux
        }

        output_folder = "output"  # 
        os.makedirs(output_folder, exist_ok=True)
        json_output_path = os.path.join(output_folder, "resultat.json")

        # Sauvegarde du résultat dans le fichier JSON
        with open (json_output_path, 'w') as json_file: json.dump(resultat, json_file, indent=4)

        # Exemple d'appel à la fonction
        model_path = "Code/best.pt"     # Remplacez par le chemin de votre modèle YOLO
        model_yolo(temp_pdf_path, model_path)

        # Supprimer le fichier temporaire
        os.remove(temp_pdf_path)

        return JSONResponse(content=resultat)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
