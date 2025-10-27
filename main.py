import sys
import os
import re
import shutil
from send2trash import send2trash
import pyperclip
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# initialiser les variables de configuration avec les arguments du script
if len(sys.argv) != 6 :
    exit(f"{RED}erreur : nombre d'arguments incorrect{RESET}\nil faut :\n- sas_path\n- images_src_dir\n- images_dst_dir\n- output_dir\n- log_dir")
sas_path = sys.argv[1]
images_src_dir = sys.argv[2]
images_dst_dir = sys.argv[3]
output_dir = sys.argv[4]
log_dir = sys.argv[5]

def print_args() :
    print(f"- sas_path : {sas_path}")
    print(f"- images_src_dir : {images_src_dir}")
    print(f"- images_dst_dir : {images_dst_dir}")
    print(f"- output_dir : {output_dir}")
    print(f"- log_dir : {log_dir}")

# vérifier les variables de configuration
if not os.path.isfile(sas_path) :
    print(f"{RED}erreur : sas_path invalide{RESET}")
    print_args()
    exit()
if not os.path.isdir(images_src_dir) :
    print(f"{RED}erreur : images_src_dir invalide{RESET}")
    print_args()
    exit()
if not os.path.isdir(images_dst_dir) :
    print(f"{RED}erreur : images_dst_dir invalide{RESET}")
    print_args()
    exit()
if not os.path.isdir(output_dir) :
    print(f"{RED}erreur : output_dir invalide{RESET}")
    print_args()
    exit()
if not os.path.isdir(log_dir) :
    print(f"{RED}erreur : log_dir invalide{RESET}")
    print_args()
    exit()

# init le sas
with open(sas_path, "r") as f :
    sas = "\n" + f.read()

if not sas.strip().startswith(('---', '--', '-)', '-')) :
    exit(f"{RED}erreur : le sas ne commence pas par un séparateur{RESET}")

# diviser le sas en sections
sas = re.split(r'(\n---|\n--|\n-\)|\n-)', sas) # ["\n-", "a", "\n-", "b", ...]
sas = [sas[i:(i + 2)] for i in range(1, len(sas), 2)] # [["\n-", "a"], ["\n-", "b"], ...]

# regrouper les sections selon le séparateur dans un dictionnaire

sas2 = {"\n-": [], "\n--": [], "\n---": [], "\n-)": []}
for sep, section in sas :
    sas2[sep].append(section)

# séparateur -> nouveau nom de section
get_new_key = {
    "\n-": "1",
    "\n--": "2",
    "\n---": "3",
    "\n-)": "ms"
}

sas = {get_new_key[sep] : section for sep, section in sas2.items()}

# sas est maintenant un dictionnaire avec [ clés : "1", "2", "3", "ms" ] et [ valeur : la liste des sections correspondantes ]

# nom d'un format -> regex
formats = {
    "img": r"<img src=\"([\s\S]*?)\" />",
    "span": r"<span style=\"color:red;\">([\s\S]*?)</span>",
    "sup": r"<sup>([\s\S]*?)</sup>",
    "sub": r"<sub>([\s\S]*?)</sub>",
    "b": r"<b>([\s\S]*?)</b>",
    "trou" : r"\{\{c\d+::([\s\S]*?)(?:::([\s\S]*?))?\}\}", # ["champ principal", "champ d'indice"]
    "trou complet" : r"\{\{c(\d+)::([\s\S]*?)(::([\s\S]*?))?\}\}", # ["numéro", "champ principal", "vide si pas d'indice", "champ d'indice"]
    "phonetique" : r'(?<!\\)//([\s\S]*?)(?<!\\)//'
}

# séparer les sections 1, 2, 3 en c1, c2, c3, t1, t2, t3

def get_t(sections) :
    """ renvoie la sous-liste de "sections" des sections qui contiennent un trou """
    result = []
    for section in sections :
        if re.search(formats["trou"], section) :
            result.append(section)
    return result

sas2 = {}
sas2["t1"] = get_t(sas["1"])
sas2["t2"] = get_t(sas["2"])
sas2["t3"] = get_t(sas["3"])
sas2["c1"] = [section for section in sas["1"] if section not in sas2["t1"]]
sas2["c2"] = [section for section in sas["2"] if section not in sas2["t2"]]
sas2["c3"] = [section for section in sas["3"] if section not in sas2["t3"]]
sas2["ms"] = sas["ms"]
sas = sas2

# sas est maintenant un dictionnaire avec [ clés : "c1", "c2", "c3", "t1", "t2", "t3", "ms" ] et [ valeur : la liste des sections correspondantes ]

# vérifier les images des sections ms
for section in sas["ms"] :
    if re.search(formats["img"], section) :
        pyperclip.copy(section)
        exit(f"{RED}erreur : image trouvée{RESET}\nsection ms copiée :\n{YELLOW}{section}{RESET}")

# vérifier et déplacer les images
for type, sections in sas.items() :
    for section in sections :
        names = re.findall(formats["img"], section)
        for name in names :
            name = name.strip()
            name_src = os.path.join(images_src_dir, name)
            name_dst = os.path.join(images_dst_dir, name)
            if not name :
                pyperclip.copy(section)
                exit(f"{RED}erreur : image vide{RESET}\nsection {type} copiée :\n{YELLOW}{section}{RESET}")
            elif not re.fullmatch(r"^[\w \-\(\)\.]+$", name, flags=re.ASCII) :
                pyperclip.copy(section)
                exit(f"{RED}erreur : nom d'image invalide{RESET}\nnom : \"{name}\"\nautorisés :\n- lettre\n- chiffre\n- espace\n- underscore\n- tiret\n- parenthèse\n- point\nsection {type} copiée :\n{YELLOW}{section}{RESET}")
            elif not os.path.exists(name_src) and not os.path.exists(name_dst) :
                pyperclip.copy(section)
                exit(f"{RED}erreur : image introuvable{RESET} (ni dans images_src_dir ni dans images_dst_dir)\nnom : \"{name}\"\nsection {type} copiée :\n{YELLOW}{section}{RESET}")
            elif os.path.exists(name_src) :
                shutil.move(name_src, name_dst)

# diviser les sections en champs trimés

def get_split(sections, type, nb_fields) :
    """ renvoie le split de "sections" en champs trimés """
    result = []
    for i in range(len(sections)) :
        if (len(re.findall(r"(?<!\\)@", sections[i])) > nb_fields - 1) :
            pyperclip.copy(sections[i])
            exit(f"{RED}erreur : trop de changements de champs{RESET}\nsection {type} ({nb_fields} champs) copiée :\n{YELLOW}{sections[i]}{RESET}")
        new = [s.strip() for s in re.split(r"(?<!\\)@", sections[i])]
        if nb_fields == 4 and len(new) == 2 : # pour mosalingua, quand 2 champs seulement sont donnés
            new.insert(1, "")
            new.append("")
        if (len(new) < nb_fields) :
            new.extend([""] * (nb_fields - len(new)))
        result.append(new)
    return result

sas2 = {"c1" : [], "c2" : [], "c3" : [], "t1" : [], "t2" : [], "t3" : [], "ms" : []}
for type in "c1", "c3", "t1", "t2", "t3" : # les sections qui ont 2 champs
    sas2[type] = get_split(sas[type], type, 2)
sas2["c2"] = get_split(sas["c2"], "c2", 3)
sas2["ms"] = get_split(sas["ms"], "ms", 4)

# une section donnée est maintenant appairée dans sas2 avec la liste de ses champs trimés.
# par exemple :
# sas["c1"] = [" a@b ", "blabla", ...]
# sas2["c1"] = [["a", "b"], ["blabla", ""], ...]

# vérifier les premiers champs
for type, sections in sas.items() :
    for i in range(len(sections)) :
        if any(sas2[type][i]) :
            if not sas2[type][i][0] :
               pyperclip.copy(sas[type][i])
               exit(f"{RED}erreur : premier champ vide{RESET}\nsection {type} copiée :\n{YELLOW}{sas[type][i]}{RESET}")

# vérifier les deuxièmes champs des types c2
for i in range(len(sas["c2"])) :
    if sas2["c2"][i][0] and not sas2["c2"][i][1] :
        pyperclip.copy(sas["c2"][i])
        exit(f"{RED}erreur : deuxième champ vide{RESET}\nsection c2 copiée :\n{YELLOW}{sas["c2"][i]}{RESET}")

# vérifier les troisièmes champs des types ms
for i in range(len(sas["ms"])) :
    if sas2["ms"][i][0] and not sas2["ms"][i][2] :
        pyperclip.copy(sas["ms"][i])
        exit(f"{RED}erreur : champ Français vide{RESET}\nsection ms copiée :\n{YELLOW}{sas["ms"][i]}{RESET}")

# vérifier les deuxièmes champs des types t1, t2, t3
for type in "t1", "t2", "t3" :
    for i in range(len(sas[type])) :
        if sas2[type][i][0] and re.search(formats["trou"], sas2[type][i][1]) :
            pyperclip.copy(sas[type][i])
            exit(f"{RED}erreur : trou dans le deuxième champ{RESET}\nsection {type} copiée :\n{YELLOW}{sas[type][i]}{RESET}")

# retirer les sections vides
sas = {}
for type, sections in sas2.items() :
    sections = [section for section in sections if any(section)]
    if sections :
        sas[type] = sections

if not any(sas.values()) :
    exit(f"{RED}erreur : sas vide{RESET}")

# fin des vérifications

for sections in sas.values() :
    for section in sections :
        for i in range(len(section)) :

            # encoder les tabulations
            section[i] = section[i].replace("\t", "    ")

            # trimer les lignes de leurs espaces
            section[i] = "\n".join([line.strip() for line in section[i].split("\n")])

            # trimer les textes de trou
            for a, b, c, d in re.findall(formats["trou complet"], section[i]) :
                section[i] = section[i].replace("{{" + f"c{a}::{b}{c}" + "}}", "{{" + f"c{a}::{b.strip()}{'::' if d.strip() else ''}{d.strip()}" + "}}")

            # trimer les textes phonétiques et encoder les "//"
            for a in re.findall(formats["phonetique"], section[i]) :
                section[i] = section[i].replace(f"//{a}//", f"/{a.strip()}/")

            # trimer les textes de balise et remplacer temporairement les chevrons de balise
            for a in re.findall(formats["img"], section[i]) :
                section[i] = section[i].replace(f"<img src=\"{a}\" />", f"BROKET_LEFTimg src=\"{a.strip()}\" /BROKET_RIGHT")
            for a in re.findall(formats["span"], section[i]) :
                section[i] = section[i].replace(f"<span style=\"color:red;\">{a}</span>", f"BROKET_LEFTspan style=\"color:red;\"BROKET_RIGHT{a.strip()}BROKET_LEFT/spanBROKET_RIGHT")
            for a in re.findall(formats["sup"], section[i]) :
                section[i] = section[i].replace(f"<sup>{a}</sup>", f"BROKET_LEFTsupBROKET_RIGHT{a.strip()}BROKET_LEFT/supBROKET_RIGHT")
            for a in re.findall(formats["sub"], section[i]) :
                section[i] = section[i].replace(f"<sub>{a}</sub>", f"BROKET_LEFTsubBROKET_RIGHT{a.strip()}BROKET_LEFT/subBROKET_RIGHT")
            for a in re.findall(formats["b"], section[i]) :
                section[i] = section[i].replace(f"<b>{a}</b>", f"BROKET_LEFTbBROKET_RIGHT{a.strip()}BROKET_LEFT/bBROKET_RIGHT")

            # encoder les chevrons et rétablir les chevrons de balise
            section[i] = section[i].replace("<", "&lt;")
            section[i] = section[i].replace(">", "&gt;")
            section[i] = section[i].replace("BROKET_LEFT", "<")
            section[i] = section[i].replace("BROKET_RIGHT", ">")

            # encoder les premiers guillemets
            if section[i].startswith('"') :
                section[i] = "&quot;" + section[i][1:]

            # supprimer les échappements devant "@", "//" et "-"
            section[i] = section[i].replace("\\@", "@")
            section[i] = section[i].replace("\\//", "//")
            section[i] = section[i].replace("\\-", "-")

            # encoder les retours à la ligne
            section[i] = section[i].replace("\n", "<br />")

# encoder les champs vides des sections ms
for section in sas.get("ms", []) :
    for i in range(len(section)) :
        if section[i] == '' :
            section[i] = "<p></p>"

# type de paquet -> nombre de sections
lens = {
    "1" : len(sas.get("c1", [])) + len(sas.get("t1", [])),
    "2" : len(sas.get("c2", [])) + len(sas.get("t2", [])),
    "3" : len(sas.get("c3", [])) + len(sas.get("t3", [])),
    "ms" : len(sas.get("ms", []))
}

# print
for type, l in lens.items() :
    if lens[type] :
        print(f"● {type} : {l}")

# supprimer les précédents fichiers de sortie
for file_name in os.listdir(output_dir) :
    file_path = os.path.join(output_dir, file_name)
    send2trash(file_path)

# type de section -> nom de fichier
file_names = {
    "c1" : "1 - 1",
    "c2" : "2 - 2",
    "c3" : "1 - 3",
    "t1" : "3 - 1",
    "t2" : "4 - 2",
    "t3" : "3 - 3",
    "ms" : "mosalingua"
}

def create_output_file(type, nb_fields, end_field, end_section) :
    if type in sas :
        with open(os.path.join(output_dir, f"{file_names[type]}.txt"), "w") as f :
            if type == "ms" :
                f.write("-\n")
            for section in sas[type] :
                for i in range(nb_fields - 1) :
                    f.write(section[i] + end_field)
                f.write(section[nb_fields - 1] + end_section)

# création des fichiers de sortie
create_output_file("c1", 2, "\t", "\n")
create_output_file("c2", 3, "\t", "\n")
create_output_file("c3", 2, "\t", "\n")
create_output_file("t1", 2, "\t", "\n")
create_output_file("t2", 2, "\t", "\n")
create_output_file("t3", 2, "\t", "\n")
create_output_file("ms", 4, "\n", "\n-\n")

# mise à jour des logs
log_9_path = os.path.join(log_dir, "9.txt")
if os.path.exists(log_9_path) :
    send2trash(log_9_path)
for i in range(8, -1, -1) :
    a = os.path.join(log_dir, f"{i}.txt")
    b = os.path.join(log_dir, f"{i + 1}.txt")
    if os.path.exists(a) :
        os.rename(a, b)
shutil.copy(sas_path, os.path.join(log_dir, "0.txt"))

# mise à jour du sas
with open(sas_path, "w") as f :
    f.write("-" + "\n" * 20)
