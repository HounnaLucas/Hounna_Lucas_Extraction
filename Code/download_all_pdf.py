
import requests 
from bs4 import BeautifulSoup  # Pour analyser et extraire des données HTML
from pathlib import Path  

site_base = "https://sgg.gouv.bj"  # L'URL du site du gouvernement du Bénin
base_url = "https://sgg.gouv.bj/recherche/?keywords=&begin=2024-01-01&end=2024-12-31&type=docs&offset="  # L'URL de recherche des décrets de 2024

offset = 1  # L'offset commence à 1 (numéro de la première page des résultats, 20 au total ici)
pdf_links = [] 
total_asides = 0  

print("🔍 Recherche des documents...")  

# Étape 1 : Récupérer tous les liens PDF

# Boucle pour récupérer toutes les pages de résultats
while True:
    print(f"Chargement de la page offset={offset}...")  
    url = base_url + str(offset)  # Construction de l'URL de la page en cours
    response = requests.get(url)  # Envoi de la requête HTTP pour récupérer la page
    soup = BeautifulSoup(response.text, 'html.parser')  # Parsing du contenu HTML de la page

    # Recherche de tous les blocs <aside> avec la classe "doc" qui contiennent les liens de téléchargement
    asides = soup.find_all("aside", class_="doc")
    
    # Si aucun bloc <aside> n'est trouvé, cela signifie qu'il n'y a plus de documents à récupérer
    if not asides:
        print("Fin des résultats.")  
        break  

    total_asides += len(asides)  # Incrémenter le compteur du nombre de résultats traités

    # Recherche des liens de téléchargement PDF dans chaque bloc <aside>
    for aside in asides:
        # Cherche un lien dont le texte est "Télécharger"
        download_link_tag = aside.find("a", string="Télécharger")
        if download_link_tag and download_link_tag.get("href"):
            full_pdf_url = site_base + download_link_tag["href"] 
            pdf_links.append(full_pdf_url) 

    offset += 1  

# Affichage du nombre total de documents trouvés et des liens PDF collectés
print(f"\nNombre total de documents trouvés : {total_asides}")
print(f"Nombre total de liens PDF collectés : {len(pdf_links)}")



# Étape 2 : Définir le nombre de fichiers à télécharger

# Nombre total de fichiers PDF collectés
nombre_de_telechargements = len(pdf_links)
print(f"\n📄 Nombre total de documents trouvés : {nombre_de_telechargements}")

# On peut définir ici un nombre maximum de fichiers à télécharger
max_to_download = 10  # Exemple : 10 fichiers à télécharger, ou  nombre_de_telechargement pour tout prendre



# Étape 3 : Téléchargement des fichiers PDF

# Création du dossier où les fichiers seront enregistrés
dest_folder = Path("mes_pdfs")
dest_folder.mkdir(parents=True, exist_ok=True)  # Si le dossier n'existe pas, il est créé

# Message indiquant le début du téléchargement
print(f"\n⬇️ Téléchargement des {min(max_to_download, nombre_de_telechargements)} fichiers PDF...")

# Boucle pour télécharger les fichiers PDF
for link in pdf_links[:max_to_download]: 
    filename = link.split("/")[-2] + ".pdf"  
    filepath = dest_folder / filename  
    print(f"  - {filename}")  
    r = requests.get(link)  
    with open(filepath, "wb") as f:  
        f.write(r.content)  

# Message de fin de téléchargement
print("\n✅ Terminé. Tous les fichiers ont été enregistrés dans 'mes_pdfs'.")
