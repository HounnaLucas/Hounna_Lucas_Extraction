from ultralytics import YOLO
import cv2
import os

# Chemin vers le modèle entraîné
model_path = "runs/detect/train/weights/best.pt"
print(f"📦 Chargement du modèle depuis : {model_path}")
model = YOLO(model_path)

# Image à tester
image_path = "azez.JPG"
print(f"🖼️ Chargement de l'image : {image_path}")
image = cv2.imread(image_path)

# Exécution de la prédiction
print("🔍 Lancement de la détection...")
results =  model(image, conf=0.05)

# Créer un dossier pour sauvegarder les signatures extraites
output_dir = "signatures_extraites"
os.makedirs(output_dir, exist_ok=True)

# Récupérer les détections
boxes = results[0].boxes
print(f"✅ {len(boxes)} signature(s) détectée(s).")

# Parcourir les boîtes et extraire chaque signature
for i, box in enumerate(boxes):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cropped = image[y1:y2, x1:x2]
    
    output_path = os.path.join(output_dir, f"signature_{i+1}.jpg")
    cv2.imwrite(output_path, cropped)
    print(f"💾 Signature {i+1} enregistrée dans : {output_path}")

# Sauvegarder l’image avec les détections (boîtes dessinées)
results[0].save(filename="image_avec_detections.jpg")
print("🖼️ Image avec les signatures détectées sauvegardée sous : image_avec_detections.jpg")
