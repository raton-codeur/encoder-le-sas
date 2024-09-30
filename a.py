#!/opt/local/bin/python3.10

import re
import shutil
import os

sas_path = "/Users/quentinhauuy/Documents/à rentrer/sas.txt"
image_source_dir = "/Users/quentinhauuy/Downloads"
image_dest_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/collection.media"
trash_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/sas.trash"
output_dir = "/Users/quentinhauuy/Downloads"

f = open(sas_path, "r")
sas = f.read()
f.close()
sas = sas.strip()

comments = []

if "\t" in sas :
    sas = sas.replace("\t", "    ")
    comments.append("tabulation remplacée par 4 espaces.")
if (comments) :
    print("commentaire :", comments)

# vérifie que le sas commence par un séparateur
# split le sas en liste de couples (séparateur, section)

def get_first_separator(sas) :
    for sep in ('---', '--', '-a', '-') :
        if sas.startswith(sep) :
            return sep
    exit("le sas ne commence pas par un séparateur")

def first_split() :
    global sas
    sep = get_first_separator(sas)
    sas = ["\n" + sep] + re.split(r'(\n---|\n--|\n-a|\n-)', sas[len(sep):]) # ["\n-", "a", "\n-", "b", ...]
    sas = [sas[i:(i + 2)] for i in range(0, len(sas), 2)] # [["\n-", "a"], ["\n-", "b"], ...]
first_split()

# diviser le sas en sections
def second_split() :
    global sas
    result = {"\n-": [], "\n--" : [], "\n---" : [], "\n-a" : []}
    for sep, section in sas :
        result[sep].append(section)
    sas = result
second_split()

def print_sas() :
    global sas
    for sep, sections in sas.items() :
        print(f"\n\n: {sep.strip()} :")
        print(sections)
print_sas()

formats = {
    "img": r"<img src=\"([\s\S]*?)\" />",
    "span": r"<span style=\"color:red;\">([\s\S]*?)</span>",
    "sup": r"<sup>([\s\S]*?)</sup>",
    "sub": r"<sub>([\s\S]*?)</sub>",
    "b": r"<b>([\s\S]*?)</b>",
    "trou" : r"\{\{c\d+::([\s\S]*?)(?:::([\s\S]*?))?\}\}"
}    

# vérifier le texte de l'attribut *src* d'une balise *img*,
# for sep, section in sas :
#     contents = re.findall(formats["img"], section)
#     for content in contents :
#         if re.search(r'[^\w\s\-\(\)\.]', content) :
#             exit(f"erreur dans la section :\n{section}\n\ncaractère interdit dans cet attribut de balise img :\n{content}")

# trimer les balises et les trous 
def trim() :
    global sas
    for i, (sep, section) in enumerate(sas) :
        for type_format, regex in formats.items() :
            contents = re.findall(regex, section)                
            for content in contents :
                if len(content) == 2 and content[1] :
                    sas[i][1] = sas[i][1].replace(content[1], content[1].strip())
                sas[i][1] = sas[i][1].replace(content[0], content[0].strip())


# trim()
# print(sas)


# sas = ["ab", "c", "d"]
# for i, valeur in enumerate(sas) :
#     if valeur == "c" :
#         sas[i] = "e"
# print(sas)

