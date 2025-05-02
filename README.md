
# 🧠 Extraction Automatique d'Informations de Documents PDF - Hackathon 2025

Ce projet permet d'extraire automatiquement des informations pertinentes (titre, date, ministère, objet) depuis des PDF non structurés (ex: décrets gouvernementaux), et de produire un fichier JSON structuré.

## 🔧 Fonctionnalités


- 📰 **Téléchargement de Décrets** : Téléchargement automatique des décrets gouvernementaux depuis [sgg.gouv.bj](https://sgg.gouv.bj/documentheque/decrets/)
- 🔍 **OCR avec Tesseract** : Conversion d'images en texte pour les documents PDF scannés.
- 🧠 **Traitement NLP** : Extraction des informations pertinentes via des expressions régulières et du traitement linguistique.
- 🔮 Idées futures
 **Modèle YOLO** : Détecter automatiquement les signatures dans des documents PDF. 
- 📦 **Structuration des Données** : Génération de fichiers JSON structurés pour chaque décret traité.
- 🌐 **API REST avec FastAPI** : Fourniture d'une API pour une utilisation facile via des requêtes HTTP.


## 📂 Arborescence du projet

```
.
Projet Lucas/
│
│
├── Code/                         # Code source du projet
│   ├── __init__.py
│   ├── mes_fonctions.py          # Fonctions d'extraction du contenu
│   ├── mes_fonctions_suite.py    # Suite des fonctions d'extraction
│   ├── mots_clés.py              # Dictionnaires des Ministères au Bénin
│   ├── traitement_texte.py       # Fichier d'extraction et de nettoyage du texte
│   ├── doxnload_all_pdf.py       # Telecharger pdf sur le site du gouvernement
│   ├── best.pt                   # Modèle ML utilisé
│
├── mes_pdfs/                     # Dossier pour les PDF d'entrée
│
├── Model Entrainement/           # Entrainement modèle Yolo
│   ├── Lucas/                    # Jeu d'images annotées
│   ├── entrainemant.py          
│   ├── validation.py    
│   ├── signature.yaml              
│  
├── main.py                       # Script principal d'exécution
│
├── model_yolo.py                 # Modèle Machine learning d'extraction sighature
│
├── requirements.txt              # Dépendances du projet
│
└── README.md                     # Description du projet

```

En sortie s'ajoutent ;

```
.
Projet Lucas
│
├── Output/                          # Dossier pour les résultats extraits           
│   ├── image _avec _detections
│   ├── signatures_extraites       
│   ├── image_links.json      
│   ├── resultat.json    
       

```

## ▶️ Utilisation

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Démarrer l'API FastAPI

```bash
uvicorn main:app --reload
```

### 3. Utiliser l'API
   http://127.0.0.1:8000/docs
- `POST /extract/` : Envoie un fichier PDF, reçoit un JSON structuré.

## 📊 Exemple de sortie JSON

```json
{
  "titre": "Décret n°2024-123",
  "date": "18 Janvier 2024",
  "ministère": "Ministère de l'Économie et des Finances",
  "objet": "portant nomination au sein du Conseil d’administration"
}
```

### Structuration de la partie "explication du code" :

1. **Introduction générale :** 
   Le code est conçu pour extraire des informations structurées de documents PDF non structurés, avec une architecture modulaire qui comprend l'OCR, le traitement NLP, et l'API REST."

2. **Détails de l'API (FastAPI) :**
   Le fichier `main.py` contient la définition de l'API REST qui permet de recevoir des fichiers PDF et de retourner les informations extraites sous forme de JSON."

3. **Détails du modéle Yolo (FastAPI) :**
   Le fichier `model_yolo.py` permet :
   - TélChargement d’un modèle YOLO (format `.pt`) (Ici on a exporté best.pt qui a été entrainé à partir d'un jeu de données disponible dans Model Entrainement
   - Conversion de PDF en images haute résolution
   - Détection des signatures sur chaque page
   - Extraction et sauvegarde des signatures

5. **Les différentes fonctions :**
   DE nombreuses fonctions sont utilisées dans le déroulé. Les principales fonctions sont appelées dans le main prinicpal
   
     - `extract_text_from_scanned_pdf()` : "Cette fonction applique l'OCR avec Tesseract pour extraire du texte brut à partir de PDF scannés."

     - `nettoyer_texte()` : "Elle nettoie le texte extrait en supprimant les caractères inutiles et en normalisant le texte."
         Les pdfs utilisés ici ont tous une sctructure quasi identique. Pour cela nous avons divisé le pdf en différentes parties, auquelles sont associées des fonctions
     
     - `extraire_metadonnees_entete` : Fonction principale d’extraction des données de l'entête d’un décret. C'est la partie supérieure droite qui comporte le numéro 
         du décret, sa date de publication et l'objet. Grâce à la fonction  re.search() paramétrée, on identifie les différents éléments de sortie. 
         Elle retourne : 
      # resultats =  "metadonnees": { "numero_decret": numero_decret, "date_publication": date_publication, "institution": institution, "objet": objet }
     
     - `extract_preambule` : Avant l'annonce des Articles, un rappel d'anciennes lois ou de décrets, sur lesquels se basent les nouveaux articles est effectué.
         Cette portion, nommée ici préambule, est constitué de phrases commençant par "Vu". Durant l'extraction, la structure du texte est parfgois biaisé (On a
         donc codé une option avec extraction propre et une autre où les mots-clés VU, sont désorganisés.)
         Elle retourne
      # preambule.append({ "type": type_texte, "numero": numero, "date": date, "contenu": contenu })

     - `extract_articles` : Fonction principale d’extraction des articles d’un décret. C'est la partie du texte commençant après le mots-Clé DECRETE. Chaque article 
         posséde un numéro (1,2,2,...), un type (nomination, interdition, Rappel, Information, Modification, ...) et est inscrit sur une page donnée.
         Elle retourne : 
      # articles.append({ "article": numero_en_ordinal(numero_brut), "contenu": contenu, "type": article_type, "page": page })

      - `extraire_ampliations` : "Cette fonction permet la structuration des ampliations du communniqué."

      - `associer_ministeres_et_noms` : Appliqué à la portion de texte située entre Fait à.. et Ampliation..., elle permet d'extraire la liste des signataires du décret. 
         On extrait les postes ministériels et les noms des ministres signataires.
         Elle retourne
      # resultat_json = { "Entités Signataires ": ministeres_detectes, "Ont signé ": noms_formates }

      - `extract_legal_terms` : Retourne les termes juridiques les plus utilisées dans le décret

      - `extraire_annexe` : Retourne tout élément annexé au communiqué principal

      - `model_yolo` : détecter automatiquement les signatures dans des documents PDF. Il convertit chaque page du PDF en image, applique la détection d’objets, extrait les signatures détectées, et génère un fichier JSON contenant les chemins des résultats. Elle retourne :
        les images avec détection (dossier) les signatures () et les lien des signatures


  

6. **Le pipeline de traitement :**
   Le texte brut extrait est ensuite nettoyé, puis les informations pertinentes (titre, date, ministère, etc.) sont extraites grâce à des expressions régulières et stockées dans un format JSON. 

7. **Conclusion :**
   En résumé, ce projet vise à automatiser l'extraction d'informations depuis des décrets gouvernementaux en PDF, avec une API permettant aux utilisateurs d'envoyer des documents et d'obtenir des informations structurées."


