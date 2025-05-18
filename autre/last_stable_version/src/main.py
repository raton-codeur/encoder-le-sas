#!/opt/local/bin/python3.10

import re
import os
import shutil
from config import *
from send2trash import send2trash

def rm_output_dir() :
    """ supprime le dossier d'output précédent """
    if os.path.exists(output_dir) :
        send2trash(output_dir)
rm_output_dir()

def get_sas() :
    """ renvoie le contenu trimé du sas """
    with open(sas_path, "r") as f :
        return f.read().strip()
sas = get_sas()

sas = sas.replace("\t", "    ")

def trim_lines() :
    """ trim les lignes de leurs espaces """
    global sas
    sas = "\n".join([line.strip() for line in sas.split("\n")])
trim_lines()

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

def starts_with_separator() :
    return sas.startswith(('---', '--', '-)', '-'))

if not starts_with_separator() :
    exit("erreur : le sas ne commence pas par un séparateur")

def trim_format() :
    """ trim les balises, les trous, la phonétique.
    les // de phonétique sont remplacés par /
    les chevrons de balises sont temporairement remplacés par une autre string
    """
    global sas
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
trim_format()

def delete_echap_phonetique() :
    """ supprime l'échappement des \// """
    global sas
    sas = sas.replace("\\//", "//")
delete_echap_phonetique()

def replace_chevrons() :
    """ remplace les chevrons et les chevrons temporaires """
    global sas
    sas = sas.replace("<", "&lt;")
    sas = sas.replace(">", "&gt;")
    sas = sas.replace("BROKET_LEFT", "<")
    sas = sas.replace("BROKET_RIGHT", ">")
replace_chevrons()

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
    result["ms"] = sections["\n-)"]
    return result

def second_split() :
    """ divise le sas entre les sections 1, 2, 3 et ms"""
    global sas
    result = {"\n-": [], "\n--" : [], "\n---" : [], "\n-)" : []}
    for sep, section in sas :
        result[sep].append(section)
    sas = rename_keys(result)
second_split()
# le sas est maintenant un dictionnaire avec les clés "1", "2", "3" et "ms" et les valeurs les sections correspondantes

def delete_echap_at_beginning() :
    """ supprime les échappements pour les changements de sections comme \n\- ou \n\-) par exemple """
    global sas
    for sections in sas.values() :
        for i in range(len(sections)) :
            sections[i] = re.sub(r"\n\\(---|--|-\)|-)(?!\\)", r"\n\1", sections[i])
            sections[i] = re.sub(r"\n\\\\(---|--|-\)|-)", r"\n\\\1", sections[i])
delete_echap_at_beginning()

def get_t(sections) :
    """ renvoie la liste des sections de "sections" qui contiennent un trou """
    result = []
    for section in sections :
        if re.search(formats["trou"], section) :
            result.append(section)
    return result

def distribute() :
    """ distribue les sections entre c1, c2, c3, t1, t2, t3 et ms """
    global sas
    result = {"c1" : [], "c2" : [], "c3" : [], "t1" : [], "t2" : [], "t3" : [], "ms" : []}
    result["ms"] = sas["ms"]
    result["t1"] = get_t(sas["1"])
    result["t2"] = get_t(sas["2"])
    result["t3"] = get_t(sas["3"])
    result["c1"] = [section for section in sas["1"] if section not in result["t1"]]
    result["c2"] = [section for section in sas["2"] if section not in result["t2"]]
    result["c3"] = [section for section in sas["3"] if section not in result["t3"]]
    sas = result
distribute()
# le sas est maintenant un dictionnaire avec les clés "c1", "c2", "c3", "t1", "t2", "t3" et "ms" et les valeurs les sections correspondantes

def print_sas() :
    global sas
    for type, sections in sas.items() :
        if sections :
            print(f"--- {type} ({len(sections)}) ---")
            print(sections)

def get_split(sections, nb_fields) :
    """ renvoie le split de "sections" en champs """
    for i in range(len(sections)) :
        if (len(re.findall(r"(?<!\\)@", sections[i])) > nb_fields - 1) :
            exit("trop de champs dans la section :\n" + sections[i])
        sections[i] = re.split(r"(?<!\\)@", sections[i])
        if nb_fields == 4 and len(sections[i]) == 2 : # pour l'anglais quand 2 champs seulement sont donnés
            sections[i].insert(1, '')
            sections[i].append('')
        if (len(sections[i]) < nb_fields) :
            sections[i].extend([''] * (nb_fields - len(sections[i])))
    return sections

def split_fields() :
    """split les champs des sections"""
    global sas
    for sections in sas["c1"], sas["c3"], sas["t1"], sas["t2"], sas["t3"] : # les sections qui ont 2 champs
        sections = get_split(sections, 2)
    sas["c2"] = get_split(sas["c2"], 3)
    sas["ms"] = get_split(sas["ms"], 4)
split_fields()

def delete_echap_at_at() :
    """ supprime les échappements pour les @ """
    global sas
    for sections in sas.values() :
        for section in sections :
            for i in range(len(section)) :
                section[i] = section[i].replace("\\@", "@")
delete_echap_at_at()

def trim_fields() :
    """ trim les champs """
    global sas
    for sections in sas.values() :
        for section in sections :
            for i in range(len(section)) :
                section[i] = section[i].strip()
trim_fields()

def remove_empty_sections() :
    """ parcourt les sections. si tous les champs d'une section sont vides, la section est supprimée """
    global sas
    for type, sections in sas.items() :
        sas[type] = [section for section in sections if any(section)]
remove_empty_sections()

def check_trou() :
    """ vérifie qu'il n'y a pas de trou dans les deuxièmes champs """
    for type in "t1", "t2", "t3" :
        for section in sas[type] :
            if re.search(formats["trou"], section[1]) :
                exit(f"erreur : trou dans le champ d'indice. section de type {type} :\n{section}\n")
check_trou()

def check_first_field() :
    """ vérifie que les sections ont un premier champ non vide """
    for type, sections in sas.items() :
        for section in sections :
            if section[0] == '' :
                exit(f"erreur : premier champ vide. section de type {type} :\n{section}")
check_first_field()

def check_c2() :
    """ vérifie que les sections de c2 ont un deuxième champ non vide """
    for section in sas["c2"] :
        if section[1] == '' :
            exit(f"erreur : deuxième champ vide pour un type c2 :\n{section}")
check_c2()

def check_ms_fields() :
    """ vérifie que les sections ms ont 2 champs non vides """
    for section in sas["ms"] :
        if section[2] == '' :
            exit(f"erreur : champ vide pour le Français dans une carte ms :\n{section}")
check_ms_fields()

def img_name_is_not_ok(name):
    motif = rf"^[\w \-\(\)\.]+$"
    return not re.fullmatch(motif, name, flags=re.ASCII)

def do_imgs() :
    """ vérifie que les images existent, ont un nom correct et les déplace de images_src à images_dest. """
    for sections in sas.values() :
        for section in sections :
            for field in section :
                names = re.findall(formats["img"], field)
                for name in names :

                    if not name :
                        exit(f"erreur : image vide dans la section :\n{section}")
                    elif img_name_is_not_ok(name) :
                        exit(f"erreur : nom d'image interdit dans la section :\n{section}\nautorisés : lettres chiffres _ ' ' - ( ) .")
                    elif not os.path.exists(os.path.join(images_src_dir, name)) and not os.path.exists(os.path.join(images_dest_dir, name)) :
                        exit(f"erreur : l'image {name} n'a pas été trouvée (ni dans le dossier {images_src_dir} ni dans le dossier {images_dest_dir}). section :\n{section}")
                    elif os.path.exists(os.path.join(images_src_dir, name)) :
                        shutil.move(os.path.join(images_src_dir, name), os.path.join(images_dest_dir, name))
do_imgs()

def get_empty_ms() :
    """ remplace les champs vides de type ms par <p></p> """
    global sas
    for section in sas["ms"] :
        for i in range(len(section)) :
            if section[i] == '' :
                section[i] = "<p></p>"
get_empty_ms()

def encode_new_line() :
    """ encode les \n par <br /> """
    global sas
    for type, sections in sas.items() :
        for section in sections :
            for i in range(len(section)) :
                section[i] = section[i].replace("\n", "<br />")
encode_new_line()

def first_quote() :
    """encode le premier caractere \" dun champ par &quot;"""
    global sas
    for sections in sas.values() :
        for section in sections :
            for i in range(len(section)) :
                if section[i].startswith('"') :
                    section[i] = "&quot;" + section[i][1:]
first_quote()

# si le sas est vide
if not any(sas.values()) :
    exit("sas vide")

print_sas()

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

# création des fichiers.
def create_files() :
    write_sections("c1", 2, "\t", "\n")
    write_sections("c2", 3, "\t", "\n")
    write_sections("c3", 2, "\t", "\n")
    write_sections("t1", 2, "\t", "\n")
    write_sections("t2", 2, "\t", "\n")
    write_sections("t3", 2, "\t", "\n")
    write_sections("ms", 4, "\n", "\n-\n")
create_files()

def edit_logs() :
    """ met à jour les logs et le sas """
    
    log_9_path = os.path.join(log_dir, "9.txt")
    if os.path.exists(log_9_path) :
        send2trash(log_9_path)
    for i in range(8, -1, -1) :
        src = os.path.join(log_dir, f"{i}.txt")
        dst = os.path.join(log_dir, f"{i + 1}.txt")
        if os.path.exists(src):
            os.rename(src, dst)

    shutil.copy(sas_path, f"{log_dir}/0.txt")
    with open(sas_path, "w") as f :
        f.write("-\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
edit_logs()

