#!/opt/local/bin/python3.10

import re
import os
import shutil

sas_path = "sas.txt"
image_source_dir = "."
image_dest_dir = "."
trash_dir = "."
output_dir = "."
# sas_path = "/Users/quentinhauuy/Documents/à rentrer/sas.txt"
# image_source_dir = "/Users/quentinhauuy/Downloads"
# image_dest_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/collection.media"
# trash_dir = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/sas.trash"
# output_dir = "/Users/quentinhauuy/Downloads"

def get_sas() :
    """ renvoie le contenu trimé du sas """
    with open(sas_path, "r") as f :
        return f.read()
sas = get_sas()

def starts_with_separator() :
    if sas.startswith(('---', '--', '-)', '-')) :
        return True
    return False

if not starts_with_separator() :
    exit("erreur : le sas ne commence pas par un séparateur")

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

def check_img_src() :
    """ verifier les noms des img """
    for content in re.findall(formats["img"], sas) :
        if re.search(r'[^\w\s\-\(\)\.]', content) :
            exit(f"erreur : nom d'image interdit : {content}")
check_img_src()

if "\t" in sas :
    sas = sas.replace("\t", "    ")

def trim_format() :
    """ trim les balises et les trous """
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
        sas = sas.replace("{{" + f"c{a}::{b}{c}" + "}}", "{{" + f"c{a}::{b.strip()}{'::' if d.strip() else ''}{d.strip()}" + "}}")
trim_format()

def get_first_separator() :
    for sep in '---', '--', '-)', '-' :
        if sas.startswith(sep) :
            return sep
    return None

def first_split() :
    global sas
    sep = get_first_separator()
    sas = ["\n" + sep] + re.split(r'(\n---|\n--|\n-\)|\n-)', sas[len(sep):]) # ["\n-", "a", "\n-", "b", ...]
    sas = [sas[i:(i + 2)] for i in range(0, len(sas), 2)] # [["\n-", "a"], ["\n-", "b"], ...]
first_split()
# sas est maintenant un truc du genre [["\n-", "a"], ["\n-", "b"], ...]

def rename_keys(sections) :
    result = {}
    result["1"] = sections["\n-"]
    result["2"] = sections["\n--"]
    result["3"] = sections["\n---"]
    result["a"] = sections["\n-)"]
    return result

def second_split() :
    """ divise le sas entre les sections 1, 2, 3 et a"""
    global sas
    result = {"\n-": [], "\n--" : [], "\n---" : [], "\n-)" : []}
    for sep, section in sas :
        result[sep].append(section)
    sas = rename_keys(result)
second_split()

def get_t(sections) :
    """ renvoie les sections qui contiennent un trou """
    result = []
    for section in sections :
        if re.search(formats["trou"], section) :
            result.append(section)
    return result

def distribute() :
    """ distribue les sections entre c1, c2, c3, t1, t2, t3 et a """
    global sas
    result = {"c1" : [], "c2" : [], "c3" : [], "t1" : [], "t2" : [], "t3" : [], "a" : []}
    result["a"] = sas["a"]
    result["t1"] = get_t(sas["1"])
    result["t2"] = get_t(sas["2"])
    result["t3"] = get_t(sas["3"])
    result["c1"] = [section for section in sas["1"] if section not in result["t1"]]
    result["c2"] = [section for section in sas["2"] if section not in result["t2"]]
    result["c3"] = [section for section in sas["3"] if section not in result["t3"]]
    sas = result
distribute()

def print_sas() :
    global sas
    for type, sections in sas.items() :
        if sections :
            print(f": {type} :")
            print(sections)

def get_split(sections, nb_fields) :
    """ renvoie la liste des listes de champs pour un type de section """
    for i in range(len(sections)) :
        if (len(re.findall(r"(?<!\\)@", sections[i])) > nb_fields - 1) :
            exit("trop de champs dans la section :\n" + sections[i])
        sections[i] = re.split(r"(?<!\\)@", sections[i])
        if nb_fields == 4 and len(sections[i]) == 2 : # pour l'anglais quand 2 champs seulement sont donnés
            sections[i].extend(['', ''])
            sections[i][1], sections[i][2] = sections[i][2], sections[i][1]
        if (len(sections[i]) < nb_fields) :
            sections[i].extend([''] * (nb_fields - len(sections[i])))
    return sections

def split_fields() :
    """split les champs des sections"""    
    global sas
    for sections in sas["c1"], sas["c3"], sas["t1"], sas["t2"], sas["t3"] : # les sections qui ont 2 champs
        sections = get_split(sections, 2)
    sas["c2"] = get_split(sas["c2"], 3)
    sas["a"] = get_split(sas["a"], 4)
split_fields()

def remove_empty() :
    """ parcourt les sections. si tous les champs d'une section sont vides, la section est supprimée """
    global sas
    for type in sas :
        sas[type] = [section for section in sas[type] if any([field.strip() for field in section])]
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
        if (sections) :
            print(f"{file_name[type]} : {len(sections)}")
# print_sizes()

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

# création des fichiers.
write_sections("c1", 2, "\t", "\n")
write_sections("c2", 3, "\t", "\n")
write_sections("c3", 2, "\t", "\n")
write_sections("t1", 2, "\t", "\n")
write_sections("t2", 3, "\t", "\n")
write_sections("t3", 2, "\t", "\n")
write_sections("a", 4, "\n", "\n-\n")

# copie des images

def is_in_sas(fichier) :
    """ renvoie ecq fichier est mentionné dans le sas """
    for type, sections in sas.items() :
        for section in sections :
            for field in section :
                if fichier in field :
                    return True
    return False

def move_img() :
    """ déplace les images """
    fichiers = os.listdir(image_source_dir)
    for fichier in fichiers :
        if is_in_sas(fichier) :
            os.rename(os.path.join(image_source_dir, fichier), os.path.join(image_dest_dir, fichier))
move_img()

# input("appuyez sur entrée pour supprimer les fichiers créés et réinitialiser le sas.")

for type, section in sas.items() :
    if section :
        os.remove(f"{file_name[type]}.txt")

# mise à jour de la poubelle

# os.remove(os.path.join(trash_dir, "9.txt"))
# for i in range(8, -1, -1) :
#     os.rename(os.path.join(trash_dir, f"{i}.txt"), os.path.join(trash_dir, f"{i + 1}.txt"))
# shutil.copy(sas_path, f"{trash_dir}/0.txt")
# with open(sas_path, "w") as f :
#     f.write("-\n")

# print(f"log : {trash_dir}/0.txt")
