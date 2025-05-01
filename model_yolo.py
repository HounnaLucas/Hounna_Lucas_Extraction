import os
import json
import numpy as np
from pdf2image import convert_from_path
from ultralytics import YOLO
import cv2

# Fonction principale qui utilise YOLO pour détecter les signatures dans un PDF
def model_yolo(pdf_path, model_path="best.pt", output_folder="output"):
    # Créer le dossier de sortie si nécessaire
    os.makedirs(output_folder, exist_ok=True)

    # Charger le modèle YOLO
    print(f"📦 Chargement du modèle depuis : {model_path}")
    model = YOLO(model_path)

    # Convertir le PDF en images
    print(f"📄 Conversion du PDF : {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)

    # Liste pour stocker les liens vers les images
    image_links = []

    # Parcourir toutes les images extraites du PDF
    for page_num, image in enumerate(images):
        # Convertir l'image en format OpenCV (BGR)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Exécuter la détection YOLO sur l'image
        print(f"🔍 Lancement de la détection pour la page {page_num + 1}...")
        results = model(image_cv, conf=0.05)

        # Dossier pour les images avec détections
        detection_output_folder = os.path.join(output_folder, "images_avec_detections")
        os.makedirs(detection_output_folder, exist_ok=True)

        # Dossier pour les signatures extraites
        signatures_folder = os.path.join(output_folder, "signatures_extraites")
        os.makedirs(signatures_folder, exist_ok=True)

        # Récupérer les détections
        boxes = results[0].boxes
        print(f"✅ {len(boxes)} signature(s) détectée(s) sur la page {page_num + 1}.")

        # Sauvegarder les signatures extraites et générer les liens
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped = image_cv[y1:y2, x1:x2]

            # Sauvegarder la signature extraite
            signature_filename = f"page_{page_num + 1}_signature_{i + 1}.jpg"
            signature_path = os.path.join(signatures_folder, signature_filename)
            cv2.imwrite(signature_path, cropped)

            # Ajouter le lien de la signature dans le JSON
            image_links.append({"image": signature_path})

        # Sauvegarder l'image avec les détections (boîtes dessinées)
        detection_filename = f"page_{page_num + 1}_with_detections.jpg"
        detection_path = os.path.join(detection_output_folder, detection_filename)
        results[0].save(filename=detection_path)

        # Ajouter le lien de l'image avec détections dans le JSON
        image_links.append({"image_with_detections": detection_path})

    # Sauvegarder le fichier JSON avec les liens vers les images
    json_output_path = os.path.join(output_folder, "image_links.json")
    with open(json_output_path, 'w') as json_file:
        json.dump(image_links, json_file, indent=4)

    print(f"💾 Fichier JSON sauvegardé : {json_output_path}")
    print(f"✅ Traitement terminé ! Tous les fichiers sont enregistrés dans le dossier : {output_folder}")


