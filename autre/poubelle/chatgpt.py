import re

def verifier_balise(section, balise, nom_balise):
    """Vérifie si le contenu d'une balise est vide dans une section donnée."""
    for contenu in re.findall(balise, section):
        if not contenu.strip():
            exit(f"erreur dans la section {repr(section)} : (balise) \"{nom_balise}\" vide.")

def verifier_trou(section):
    """Vérifie si un trou est vide dans une section donnée."""
    trous = re.findall(r"\{\{c\d+::([\s\S]*?)(::([\s\S]*?))?\}\}", section)
    for trou in trous:
        # Vérifie que soit le premier, soit le deuxième champ est non vide
        if not (trou[0].strip() or trou[2].strip()):
            exit(f"erreur dans la section {repr(section)} : trou vide.")

# Liste des balises à vérifier avec leur regex et nom
balises = [
    (r"<img src=\"([\s\S]*?)\" />", "img"),
    (r"<span style=\"color:red;\">([\s\S]*?)</span>", "span"),
    (r"<sup>([\s\S]*?)</sup>", "sup"),
    (r"<sub>([\s\S]*?)</sub>", "sub"),
    (r"<b>([\s\S]*?)</b>", "b")
]

# Liste des sections extraites du fichier sas (après avoir splitté avec les séparateurs)
sections = [i.strip() for i in re.split(r"-|--|---|-vf|-o|-r|-a", texte) if i.strip()]

for section in sections:
    # Vérification de chaque balise
    for balise, nom_balise in balises:
        verifier_balise(section, balise, nom_balise)
    
    # Vérification des trous
    verifier_trou(section)
