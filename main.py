import sys
import os
import re
import shutil
from send2trash import send2trash

# initialiser les variables de configuration avec les arguments du script
if len(sys.argv) != 6 :
    exit("erreur : nombre d'arguments incorrect. il faut :\n- sas_path\n- images_src_dir\n- images_dst_dir\n- output_dir\n- log_dir")
sas_path = sys.argv[1]
images_src_dir = sys.argv[2]
images_dst_dir = sys.argv[3]
output_dir = sys.argv[4]
log_dir = sys.argv[5]

# vérifier les variables de configuration
if not os.path.exists(sas_path) :
    exit(f"erreur : le fichier du sas ({sas_path}) n'existe pas")
if not os.path.exists(images_src_dir) :
    exit(f"erreur : le dossier source des images ({images_src_dir}) n'existe pas")
if not os.path.exists(images_dst_dir) :
    exit(f"erreur : le dossier de destination des images ({images_dst_dir}) n'existe pas")
d = os.path.dirname(output_dir) or "."
if not os.path.exists(d) :
    exit(f"erreur : le dossier parent du dossier d'output ({d}) n'existe pas")
if not os.path.exists(log_dir) :
    exit(f"erreur : le dossier des logs ({log_dir}) n'existe pas")

# init le sas 
with open("sas.txt", "r") as f:
    sas = "".join(f"{i + 1:4d}{line}" for i, line in enumerate(f))



with open(sas_path, "r") as f :
    sas = "\n" + f.read()

if not sas.strip().startswith(('---', '--', '-)', '-')) :
    exit("erreur : le sas ne commence pas par un séparateur")

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

# vérifier et déplacer les images
for sections in sas.values() :
    for section in sections :
        names = re.findall(formats["img"], section)
        for name in names :
            name = name.strip()
            name_src = os.path.join(images_src_dir, name)
            name_dst = os.path.join(images_dst_dir, name)
            if not name :
                exit(f"erreur : image vide dans la section :\n{section}")
            elif not re.fullmatch(r"^[\w \-\(\)\.]+$", name, flags=re.ASCII) :
                exit(f"erreur : nom d'image invalide dans la section :\n{section}\nautorisés : lettres chiffres espace _ - ( ) .")
            elif not os.path.exists(name_src) and not os.path.exists(name_dst) :
                exit(f"erreur : l'image {name} n'a pas été trouvée (ni dans {images_src_dir} ni dans {images_dst_dir}). section :\n{section}")
            elif os.path.exists(name_src) :
                shutil.move(name_src, name_dst)

# séparer les sections 1, 2, 3 en c1, c2, c3, t1, t2, t3

sas2 = {"c1" : [], "c2" : [], "c3" : [], "t1" : [], "t2" : [], "t3" : [], "ms" : sas["ms"]}

def get_t(sections) :
    """ renvoie la sous-liste des sections qui contiennent un trou """
    result = []
    for section in sections :
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



