import re
import os
import shutil
from send2trash import send2trash
import sys

# initialiser les variables de configuration avec les arguments du script
if len(sys.argv) != 6 :
    exit("erreur : nombre d'arguments incorrect. il faut :\n- sas_path\n- images_src_dir\n- images_dest_dir\n- output_dir\n- log_dir")
sas_path = sys.argv[1]
images_src_dir = sys.argv[2]
images_dest_dir = sys.argv[3]
output_dir = sys.argv[4]
log_dir = sys.argv[5]

# vérifier les variables de configuration
if not os.path.exists(sas_path) :
    exit(f"erreur : le fichier du sas ({sas_path}) n'existe pas")
if not os.path.exists(images_src_dir) :
    exit(f"erreur : le dossier source des images ({images_src_dir}) n'existe pas")
if not os.path.exists(images_dest_dir) :
    exit(f"erreur : le dossier de destination des images ({images_dest_dir}) n'existe pas")
d = os.path.dirname(output_dir) or "."
if not os.path.exists(d) :
    exit(f"erreur : le dossier parent du dossier d'output ({d}) n'existe pas")
if not os.path.exists(log_dir) :
    exit(f"erreur : le dossier des logs ({log_dir}) n'existe pas")

# init le sas
with open(sas_path, "r") as f :
    sas = "\n" + f.read()

sas = sas.replace("\t", "    ")

# trimer les lignes de leurs espaces
sas = "\n".join([line.strip() for line in sas.split("\n")])

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

sas2 = sas.strip()
if not sas2.startswith(('---', '--', '-)', '-')) :
    exit("erreur : le sas ne commence pas par un séparateur")

# trimer les textes de balises, trous et phonétique.
# les // de phonétique sont remplacés par /.
# les chevrons de balises sont temporairement remplacés par une autre string.
for i in re.findall(formats["img"], sas) :
    sas = sas.replace(f"<img src=\"{i}\" />", f"BROKET_LEFTimg src=\"{i.strip()}\" /BROKET_RIGHT")
for i in re.findall(formats["span"], sas) :
    sas = sas.replace(f"<span style=\"color:red;\">{i}</span>", f"BROKET_LEFTspan style=\"color:red;\"BROKET_RIGHT{i.strip()}BROKET_LEFT/spanBROKET_RIGHT")
for i in re.findall(formats["sup"], sas) :
    sas = sas.replace(f"<sup>{i}</sup>", f"BROKET_LEFTsupBROKET_RIGHT{i.strip()}BROKET_LEFT/supBROKET_RIGHT")
for i in re.findall(formats["sub"], sas) :
    sas = sas.replace(f"<sub>{i}</sub>", f"BROKET_LEFTsubBROKET_RIGHT{i.strip()}BROKET_LEFT/subBROKET_RIGHT")
for i in re.findall(formats["b"], sas) :
    sas = sas.replace(f"<b>{i}</b>", f"BROKET_LEFTbBROKET_RIGHT{i.strip()}BROKET_LEFT/bBROKET_RIGHT")
for a, b, c, d in re.findall(formats["trou complet"], sas) :
    sas = sas.replace("{{" + f"c{a}::{b}{c}" + "}}", "{{" + f"c{a}::{b.strip()}{'::' if d.strip() else ''}{d.strip()}" + "}}")
for i in re.findall(formats["phonetique"], sas) :
    sas = sas.replace(f"//{i}//", f"/{i.strip()}/")

# remplacer les chevrons et les chevrons temporaires
sas = sas.replace("<", "&lt;")
sas = sas.replace(">", "&gt;")
sas = sas.replace("BROKET_LEFT", "<")
sas = sas.replace("BROKET_RIGHT", ">")

# supprimer l'échappement des \//
sas = sas.replace("\\//", "//")

# diviser le sas en sections
sas = re.split(r'(\n---|\n--|\n-\)|\n-)', sas) # ["\n-", "a", "\n-", "b", ...]
sas = [sas[i:(i + 2)] for i in range(0, len(sas), 2)] # [["\n-", "a"], ["\n-", "b"], ...]

# regrouper les sections selon le séparateur dans un dictionnaire

sas2 = {"\n-": [], "\n--" : [], "\n---" : [], "\n-)" : []}
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

# sas est maintenant un dictionnaire avec les clés "1", "2", "3", "ms" et les valeurs les sections correspondantes

# supprimer les échappements pour les changements de sections comme \n\- ou \n\-) par exemple
for sections in sas.values() :
    for i in range(len(sections)) :
        sections[i] = re.sub(r"\n\\(---|--|-\)|-)(?!\\)", r"\n\1", sections[i])
        sections[i] = re.sub(r"\n\\\\(---|--|-\)|-)", r"\n\\\1", sections[i])

# séparer les sections 1, 2, 3 en c1, c2, c3, t1, t2, t3

sas2 = {"c1" : [], "c2" : [], "c3" : [], "t1" : [], "t2" : [], "t3" : [], "ms" : sas["ms"]}

def get_t(sections) :
    """ renvoie la sous-liste des sections qui contiennent un trou """
    result = []
    for section in a :
        if re.search(formats["trou"], section) :
            result.append(section)
    return result

sas2["t1"] = get_t(sas["1"])
sas2["t2"] = get_t(sas["2"])
sas2["t3"] = get_t(sas["3"])
sas2["c1"] = [section for section in sas["1"] if section not in sas2["t1"]]
sas2["c2"] = [section for section in sas["2"] if section not in sas2["t2"]]
sas2["c3"] = [section for section in sas["3"] if section not in sas2["t3"]]
sas = sas2

# sas est maintenant un dictionnaire avec les clés "c1", "c2", "c3", "t1", "t2", "t3", "ms" et les valeurs les sections correspondantes

# diviser les sections en champs

def get_split(sections, nb_fields) :
    """ renvoie le split de "sections" en champs """
    for i in range(len(sections)) :
        if (len(re.findall(r"(?<!\\)@", sections[i])) > nb_fields - 1) :
            exit("trop de champs dans la section :\n" + sections[i])
        sections[i] = re.split(r"(?<!\\)@", sections[i])
        if nb_fields == 4 and len(sections[i]) == 2 : # pour mosalingua, quand 2 champs seulement sont donnés
            sections[i].insert(1, '')
            sections[i].append('')
        if (len(sections[i]) < nb_fields) :
            sections[i].extend([''] * (nb_fields - len(sections[i])))
    return sections

for sections in sas["c1"], sas["c3"], sas["t1"], sas["t2"], sas["t3"] : # les sections qui ont 2 champs
    sections = get_split(sections, 2)
sas["c2"] = get_split(sas["c2"], 3)
sas["ms"] = get_split(sas["ms"], 4)

# supprimer les échappements pour @
for sections in sas.values() :
    for section in sections :
        for i in range(len(section)) :
            section[i] = section[i].replace("\\@", "@")

# trimer les champs
for sections in sas.values() :
    for section in sections :
        for i in range(len(section)) :
            section[i] = section[i].strip()

# supprimer les sections vides
for type, sections in sas.items() :
    sas[type] = [section for section in sections if any(section)]

# vérifier les premiers champs
for type, sections in sas.items() :
    for section in sections :
        if not section[0] :
            exit(f"erreur : premier champ vide dans une section de type {type} :\n{section}")

# vérifier les deuxièmes champs des types c2
for section in sas["c2"] :
    if section[1] == '' :
        exit(f"erreur : deuxième champ vide pour un type c2 :\n{section}")

# vérifier le troisième champ des sections ms
for section in sas["ms"] :
    if not section[2] :
        exit(f"erreur : champ vide pour le Français dans une carte ms :\n{section}")

# vérifier qu'il n'y a pas de trous dans les deuxièmes champs
for type in "t1", "t2", "t3" :
    for section in sas[type] :
        if re.search(formats["trou"], section[1]) :
            exit(f"erreur : trou dans le deuxième champ d'une section de type {type} :\n{section}")

# vérifier et déplacer les images
for sections in sas.values() :
    for section in sections :
        for field in section :
            names = re.findall(formats["img"], field)
            for name in names :
                if not name :
                    exit(f"erreur : image vide dans la section :\n{section}")
                elif not re.fullmatch(r"^[\w \-\(\)\.]+$", name, flags=re.ASCII) :
                    exit(f"erreur : nom d'image interdit dans la section :\n{section}\nautorisés : lettres chiffres _ ' ' - ( ) .")
                elif not os.path.exists(os.path.join(images_src_dir, name)) and not os.path.exists(os.path.join(images_dest_dir, name)) :
                    exit(f"erreur : l'image {name} n'a pas été trouvée (ni dans le dossier {images_src_dir} ni dans le dossier {images_dest_dir}). section :\n{section}")
                elif os.path.exists(os.path.join(images_src_dir, name)) :
                    shutil.move(os.path.join(images_src_dir, name), os.path.join(images_dest_dir, name))

# remplacer les champs vides de ms
for section in sas["ms"] :
    for i in range(len(section)) :
        if section[i] == '' :
            section[i] = "<p></p>"

# encoder les retours à la ligne
for type, sections in sas.items() :
    for section in sections :
        for i in range(len(section)) :
            section[i] = section[i].replace("\n", "<br />")

# encoder les premiers guillemets
for sections in sas.values() :
    for section in sections :
        for i in range(len(section)) :
            if section[i].startswith('"') :
                section[i] = "&quot;" + section[i][1:]

if not any(sas.values()) :
    exit("erreur : sas vide")

# print
for type, sections in sas.items() :
    if sections :
        print(f"--- {type} ({len(sections)}) ---")
        print(sections)

# supprimer le dossier d'output précédent
if os.path.exists(output_dir) :
    send2trash(output_dir)

file_names = {
    "c1" : "1 - 1",
    "c2" : "2 - 2",
    "c3" : "1 - 3",
    "t1" : "3 - 1",
    "t2" : "4 - 2",
    "t3" : "3 - 3",
    "ms" : "mosalingua"
}

def write_sections(section_name, nb_fields, end_field, end_section) :
    if sas[section_name] :
        if not os.path.exists(output_dir) :
            os.makedirs(output_dir)
        with open(os.path.join(output_dir, f"{file_names[section_name]}.txt"), "w") as f :
            if section_name == "ms" :
                f.write("-\n")            
            for section in sas[section_name] :
                for i in range(nb_fields - 1) :
                    f.write(section[i] + end_field)
                f.write(section[nb_fields - 1] + end_section)

# création des fichiers
write_sections("c1", 2, "\t", "\n")
write_sections("c2", 3, "\t", "\n")
write_sections("c3", 2, "\t", "\n")
write_sections("t1", 2, "\t", "\n")
write_sections("t2", 2, "\t", "\n")
write_sections("t3", 2, "\t", "\n")
write_sections("ms", 4, "\n", "\n-\n")

# mise à jour des fichiers de logs et du sas
log_9_path = os.path.join(log_dir, "9.txt")
if os.path.exists(log_9_path) :
    send2trash(log_9_path)
for i in range(8, -1, -1) :
    a = os.path.join(log_dir, f"{i}.txt")
    b = os.path.join(log_dir, f"{i + 1}.txt")
    if os.path.exists(a) :
        os.rename(a, b)
shutil.copy(sas_path, f"{log_dir}/0.txt")
with open(sas_path, "w") as f :
    f.write("-" + "\n" * 40)
