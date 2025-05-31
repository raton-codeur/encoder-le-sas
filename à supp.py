






















# supprimer les sections vides
for type, sections in sas.items() :
    sas[type] = [section for section in sections if any(section)]
























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
