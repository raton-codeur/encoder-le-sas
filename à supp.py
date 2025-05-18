
sas = sas.replace("\t", "    ")

# trimer les lignes de leurs espaces
sas = "\n".join([line.strip() for line in sas.split("\n")])

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

# supprimer les échappements pour les changements de sections comme \n\- ou \n\-) par exemple
for sections in sas.values() :
    for i in range(len(sections)) :
        sections[i] = re.sub(r"\n\\(---|--|-\)|-)(?!\\)", r"\n\1", sections[i])
        sections[i] = re.sub(r"\n\\\\(---|--|-\)|-)", r"\n\\\1", sections[i])

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
