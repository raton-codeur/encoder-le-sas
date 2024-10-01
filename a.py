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

# vérifier que le sas commence par un séparateur
def starts_with_separator(sas) :
    for sep in ('---', '--', '-)', '-') :
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
    sections = re.split(r'\n---|\n--|\n-)|\n-', sas) # la liste des sections du sas
    for section in sections :
        contents = re.findall(formats["img"], section)
        for content in contents :
            if re.search(r'[^\w\s\-\(\)\.]', content) :
                exit(f"erreur dans la section :\n{section}\n\ncaractère interdit dans l'attribut src")
check_img_src(sas)

if "\t" in sas :
    sas = sas.replace("\t", "    ")

# modification du contenu des balises et des trous.
def trim_format() :
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
        sas = sas.replace("{{" + f"c{a}::{b}" + "}}", "{{" + f"c{a}::{b.strip()}" + "}}")
        sas = sas.replace("{{" + f"c{a}::{b}::{d}" + "}}", "{{" + f"c{a}::{b.strip()}::{d.strip()}" + "}}")
trim_format()

# debut du remplissage des sections

def get_first_separator(sas) :
    for sep in ('---', '--', '-)', '-') :
        if sas.startswith(sep) :
            return sep
    return None

def first_split() :
    global sas
    sep = get_first_separator(sas)
    sas = ["\n" + sep] + re.split(r'(\n---|\n--|\n-)|\n-)', sas[len(sep):]) # ["\n-", "a", "\n-", "b", ...]
    sas = [sas[i:(i + 2)] for i in range(0, len(sas), 2)] # [["\n-", "a"], ["\n-", "b"], ...]
first_split()

# diviser le sas en sections
def second_split() :
    global sas
    result = {"\n-": [], "\n--" : [], "\n---" : [], "\n-)" : []}
    for sep, section in sas :
        result[sep].append(section)
    sas = result
second_split()

# commencer a remplir les sections
def rename_sections() :
    global sas
    result = {"1" : [], "2" : [], "3" : [], "a" : []}
    for sep, sections in sas.items() :
        if sep == "\n-":
            result["1"] = sections
        elif sep == "\n--":
            result["2"] = sections
        elif sep == "\n---":
            result["3"] = sections
        elif sep == "\n-)":
            result["a"] = sections
    sas = result
rename_sections()

# trouver les sections t
def distribute() :
    global sas
    result = {"c1" : [], "c2" : [], "c3" : [], "t1" : [], "t2" : [], "t3" : [], "a" : []}
    for section in sas["1"] :
        if re.search(formats["trou"], section) :
            result["t1"].append(section)
        else :
            result["c1"].append(section)
    for section in sas["2"] :
        if re.search(formats["trou"], section) :
            result["t2"].append(section)
        else :
            result["c2"].append(section)
    for section in sas["3"] :
        if re.search(formats["trou"], section) :
            result["t3"].append(section)
        else :
            result["c3"].append(section)
    for section in sas["a"] :
        result["a"].append(section)
    sas = result
distribute()

def print_sas() :
    global sas
    for type, sections in sas.items() :
        print(f": {type} :")
        print(sections)
print_sas()
print()

# debut de la verification des champs

def split_field() :
    global sas
    # for type, sections in sas.items() :
    #     for i in range(len(sections)) :
    #         sections[i] = sections[i].split("@")
    for sections in sas["c1"], sas["c3"], sas["t1"], sas["t2"], sas["t3"] :
        for i in range(len(sections)) :
            if (len(re.split(r"(?<!\\)@", sections[i])) > 2) :
                exit("trop de champs dans la section :\n" + sections[i])
            sections[i] = re.split(r"(?<!\\)@", sections[i])
    for sections in sas["c2"] :
        for i in range(len(sections)) :
            if (len(re.split(r"(?<!\\)@", sections[i])) > 3) :
                exit("trop de champs dans la section :\n" + sections[i])
            print(sections[i])
            # sections[i] = re.split(r"(?<!\\)@", sections[i])
split_field()

print_sas()

