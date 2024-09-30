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

# vérifie que le sas commence par un séparateur
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
    "trou" : r"\{\{c\d+::([\s\S]*?)(?:::([\s\S]*?))?\}\}"
}

# on veut la liste des sections du sas
sections = re.split(r'\n---|\n--|\n-a|\n-', sas)

# verifier les caracteres dans lattribut src de balise img
for section in sections :
    contents = re.findall(formats["img"], section)
    for content in contents :
        if re.search(r'[^\w\s\-\(\)\.]', content) :
            exit(f"erreur dans la section :\n{section}\n\ncaractère interdit dans cet attribut de balise img :\n{content}")
# fin des verifications

# remplacement des (caractères) "<" et ">".
sas = re.sub(r"<(?!img src=\"|/?(span|b>|sup>|sub>))", "&lt;", sas)
sas = re.sub(r"(?<!<span style=\"color:red;\"|\" /)>", "&gt;", sas)

print(sas)
if "\t" in sas :
    sas = sas.replace("\t", "    ")
