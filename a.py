#!/opt/local/bin/python3.10

import re
import shutil
import os

sas_path = "sas.txt"
# sas_path = "/Users/quentinhauuy/Documents/à rentrer/sas.txt"
image_source_dir = "/Users/quentinhauuy/Downloads"
image_dest_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/collection.media"
trash_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/sas.trash"
output_dir = "/Users/quentinhauuy/Downloads"

f = open(sas_path, "r")
sas = f.read()
f.close()
sas = sas.strip()

# debut des verifications

# vérifier que le sas commence par un séparateur
def starts_with_separator(sas) :
    for sep in ('---', '--', '-a', '-') :
        if sas.startswith(sep) :
            return True
    return False
if not starts_with_separator(sas) :
    exit("le sas ne commence pas par un séparateur")

# nom dun format -> regex
formats = {
    "img": r"<img src=\"([\s\S]*?)\" />",
    "span": r"<span style=\"color:red;\">([\s\S]*?)</span>",
    "sup": r"<sup>([\s\S]*?)</sup>",
    "sub": r"<sub>([\s\S]*?)</sub>",
    "b": r"<b>([\s\S]*?)</b>",
    "trou" : r"\{\{c\d+::([\s\S]*?)(?:::([\s\S]*?))?\}\}",
    "trou complet" : r"\{\{c(\d+)::([\s\S]*?)(::([\s\S]*?))?\}\}"
}

# verifier les caracteres dans lattribut src de balise img
def check_img_src(sas) :
    sections = re.split(r'\n---|\n--|\n-a|\n-', sas) # la liste des sections du sas
    for section in sections :
        contents = re.findall(formats["img"], section)
        for content in contents :
            if re.search(r'[^\w\s\-\(\)\.]', content) :
                exit(f"erreur dans la section :\n{section}\n\ncaractère interdit dans l'attribut src")
check_img_src(sas)

# fin des verifications

if "\t" in sas :
    sas = sas.replace("\t", "    ")

# modification du contenu des balises et des trous.
def trim() :
    global sas
    for i in re.findall(formats["img"], sas) :
        sas = sas.replace(f"<img src=\"{i}\" />", f"<img src=\"{i.strip()}\" />")
    for i in re.findall(formats["span"], sas) :
        sas = sas.replace(f"<span style=\"color:red;\">{i}</span>", f"<span style=\"color:red;\">{i.strip()}</span>")
    for i in re.findall(formats["sup"], sas) :
        sas = sas.replace(f"<sup>{i}</sup>", f"<sup>{i.strip()}</sup>")
    for i in re.findall(formats["sub"], sas) :
        sas = sas.replace(f"<sub>{i}</sub>", f"<sub>{i.strip()}</sub>")
    for i in re.findall(formats["b"], sas) :
        sas = sas.replace(f"<b>{i}</b>", f"<b>{i.strip()}</b>")
    for a, b, c, d in re.findall(formats["trou complet"], sas) :
        # texte = texte.replace("{{" + f"c{i[0]}::{i[1]}" + "}}", "{{" + f"c{i[0]}::{i[1].strip()}" + "}}")
        # texte = texte.replace("{{" + f"c{i[0]}::{i[1]}::{i[3]}" + "}}", "{{" + f"c{i[0]}::{i[1].strip()}::{i[3].strip()}" + "}}")
        sas = sas.replace("{{" + f"c{a}::{b}" + "}}", "{{" + f"c{a}::{b.strip()}" + "}}")
        sas = sas.replace("{{" + f"c{a}::{b}::{d}" + "}}", "{{" + f"c{a}::{b.strip()}::{d.strip()}" + "}}")


trim()
print(sas)
