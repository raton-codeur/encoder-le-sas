#!/opt/local/bin/python3.10

import re
import os
import shutil

sas_path = "/Users/quentinhauuy/Documents/à rentrer/sas.txt"
image_source_dir = "/Users/quentinhauuy/Downloads"
image_dest_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/collection.media"
trash_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/sas.trash"
output_dir = "/Users/quentinhauuy/Downloads"

with open(sas_path, "r") as f :
    sas = f.read().strip()

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
    sections = re.split(r'\n---|\n--|\n-\)|\n-', sas) # la liste des sections du sas
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
    sas = ["\n" + sep] + re.split(r'(\n---|\n--|\n-\)|\n-)', sas[len(sep):]) # ["\n-", "a", "\n-", "b", ...]
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
        if sections :
            print(f": {type} :")
            print(sections)

# debut de la verification des champs

def split_1_section_type(sections, nb_fields, a = False) :
    for i in range(len(sections)) :
        if (len(re.split(r"(?<!\\)@", sections[i])) > nb_fields) :
            exit("trop de champs dans la section :\n" + sections[i])
        sections[i] = re.split(r"(?<!\\)@", sections[i])
        if a and len(sections[i]) == 2 :
            sections[i].extend(['', ''])
            sections[i][1], sections[i][2] = sections[i][2], sections[i][1]
        if (len(sections[i]) < nb_fields) :
            sections[i].extend([''] * (nb_fields - len(sections[i])))
    return sections

# split les sections en champs
def split_field() :
    global sas
    nb_fields = 2
    for sections in sas["c1"], sas["c3"], sas["t1"], sas["t2"], sas["t3"] :
        sections = split_1_section_type(sections, nb_fields)
    nb_fields = 3
    sas["c2"] = split_1_section_type(sas["c2"], nb_fields)
    nb_fields = 4
    sas["a"] = split_1_section_type(sas["a"], nb_fields, 1)
split_field()

def remove_empty() :
    """ parcourt les sections. si tous les champs d'une section sont vides, la section est supprimée """
    global sas
    for type, section in sas.items() :
        sas[type] = [section for section in sas[type] if not all([field.strip() == '' for field in section])]
remove_empty()

def get_empty_a() :
    global sas
    for section in sas["a"] :
        for i in range(len(section)) :
            if section[i].strip() == '' :
                section[i] = "<p></p>"
get_empty_a()

def check_trou() :
    global sas
    for type in "t1", "t2", "t3" :
        for section in sas[type] :
            if re.search(formats["trou"], section[1]) :
                exit(f"erreur dans la section :\n{section}\ntrou dans le deuxieme champ")
check_trou()

def encode_echap() :
    """\@
    \n\-
    \n\--
    \n\---
    \n\-)
    """
    for type, sections in sas.items() :
        for section in sections :
            for i in range(len(section)) :
                section[i] = section[i].replace("\@", "@")
                section[i] = section[i].replace("\n\-", "\n-")
                section[i] = section[i].replace("\n\--", "\n--")
                section[i] = section[i].replace("\n\---", "\n---")
                section[i] = section[i].replace("\n\-)", "\n-)")
encode_echap()

def trim_fields() :
    global sas
    for type, sections in sas.items() :
        for section in sections :
            for i in range(len(section)) :
                section[i] = section[i].strip()
trim_fields()

def encode_new_line() :
    global sas
    for type, sections in sas.items() :
        for section in sections :
            for i in range(len(section)) :
                section[i] = section[i].replace("\n", "<br />")
encode_new_line()

def first_quote() :
    """encoder le premier caractere \" dun champ par &quot;"""
    global sas
    for type, sections in sas.items() :
        for section in sections :
            for i in range(len(section)) :
                if section[i].startswith('"') :
                    section[i] = "&quot;" + section[i][1:]
first_quote()

print_sas()

file_name = {
    "c1" : "1 - 1",
    "c2" : "2 - 2",
    "c3" : "1 - 3",
    "t1" : "3 - 1",
    "t2" : "4 - 2",
    "t3" : "3 - 3",
    "a" : "anglais"
}

def print_sizes() :
    for type, sections in sas.items() :
        print(f"{file_name[type]} : {len(sections)}")
print_sizes()

# création des fichiers.

# si le sas est vide
if not any(sas.values()) :
    exit("sas vide")

def write_sections(section_name, nb_fields, end_field, end_section) :
    if sas[section_name] :
        with open(os.path.join(output_dir, f"{file_name[section_name]}.txt"), "w") as f :
            for section in sas[section_name] :
                for i in range(nb_fields - 1) :
                    f.write(section[i] + end_field)
                f.write(section[nb_fields - 1] + end_section)

write_sections("c1", 2, "\t", "\n")
write_sections("c2", 3, "\t", "\n")
write_sections("c3", 2, "\t", "\n")
write_sections("t1", 2, "\t", "\n")
write_sections("t2", 3, "\t", "\n")
write_sections("t3", 2, "\t", "\n")
write_sections("a", 4, "\n", "\n-\n")

# copie des images

fichiers = os.listdir(image_source_dir)

def is_in_sas(fichier) :
    for type, sections in sas.items() :
        for section in sections :
            for field in section :
                if fichier in field :
                    return True
    return False

for fichier in fichiers :
    if is_in_sas(fichier) :
        os.rename(os.path.join(image_source_dir, fichier), os.path.join(image_dest_dir, fichier))

input("appuyez sur entrée pour supprimer les fichiers créés et réinitialiser le sas.")

for type, section in sas.items() :
    if section :
        os.remove(f"{file_name[type]}.txt")

os.remove(os.path.join(trash_dir, "9.txt"))
for i in range(8, -1, -1) :
    os.rename(os.path.join(trash_dir, f"{i}.txt"), os.path.join(trash_dir, f"{i + 1}.txt"))
shutil.copy(sas_path, f"{trash_dir}/0.txt")
with open(sas_path, "w") as f :
    f.write("-\n")

print(f"log : {trash_dir}/0.txt")
