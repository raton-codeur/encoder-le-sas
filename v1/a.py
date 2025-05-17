#!/opt/local/bin/python3.10

sas = "/Users/quentinhauuy/Documents/apprendre/sas_anki/sas.txt" # le chemin du sas.
f = open(sas, "r")
texte = f.read() # le texte du sas.
f.close()

# gestion des commentaires.
import regex as re
commentaires = [] # la liste des commentaires à afficher sur la sortie standard.
i = texte.find("@@") # l'indice du premier commentaire du sas.
if i != -1 :
    indices_commentaires = [] # une liste de couples [ indice dl· (chaîne de caractères) "@@" de début de commentaire, indice dl· (chaîne de caractères) "@@" de fin de commentaire ]
    while i != -1 :
        ii = texte.find("@@", i + 2)
        if ii == -1 :
            indices_commentaires.append((i, None))
            break
        indices_commentaires.append((i, ii))
        i = texte.find("@@", ii + 2)

    for i in range(len(indices_commentaires)) :
        commentaires.append(texte[(indices_commentaires[i][0] + 2):(indices_commentaires[i][1])])

    texte_sans_commentaire = [texte[:indices_commentaires[0][0]].strip()]
    for i in range(len(indices_commentaires) - 1) :
        texte_sans_commentaire.append(texte[(indices_commentaires[i][1] + 2):indices_commentaires[i + 1][0]].strip())
    if indices_commentaires[-1][1] != None :
        texte_sans_commentaire.append(texte[(indices_commentaires[-1][1] + 2):].strip())
    texte = "\n".join(texte_sans_commentaire)
# fin de gestion des commentaires.

# début de vérifications.
début = None # la première ligne du sas qui ne contient pas que des caractères blancs, sans caractère blanc à ses extrémités.
for ligne in texte.splitlines() :
    if ligne.strip() :
        début = ligne.strip()
        break
if début not in ("-", "--", "---", "-vf", "-o", "-r", "-a") :
    exit("erreur : le sas ne commence pas par un séparateur.")

if texte.find("\t") != -1 :
    texte = texte.replace("\t", "    ")
    commentaires.append("tabulation remplacée par 4 espaces.")

# vérification du contenu des balises et des trous.
sections = [i.strip() for i in re.split(r"-|--|---|-vf|-o|-r|-a", texte) if i.strip()] # la liste des (contenus des) sections du sas.
for section in sections :
    for i in re.findall(r"<img src=\"([\s\S]*?)\" />", section) : # le contenu d'un (attribut) "src" de (balise) "img".
        if not i.strip() :
            exit(f"erreur dans la section {repr(section)} : (attribut) \"src\" de (balise) \"img\" vide.")
        if i.find("@") != -1 :
            exit(f"erreur dans la section {repr(section)} : (caractère) \"@\" dans un (attribut) \"src\" de (balise) \"img\". ")
    for i in re.findall(r"<span style=\"color:red;\">([\s\S]*?)</span>", section) : # le contenu d'un·e (balise) "span".
        if not i.strip() :
            exit(f"erreur dans la section {repr(section)} : (balise) \"span\" vide.")
    for i in re.findall(r"<sup>([\s\S]*?)</sup>", section) : # le contenu d'un·e (balise) "sup".
        if not i.strip() :
            exit(f"erreur dans la section {repr(section)} : (balise) \"sup\" vide.")
    for i in re.findall(r"<sub>([\s\S]*?)</sub>", section) : # le contenu d'un·e (balise) "sub".
        if not i.strip() :
            exit(f"erreur dans la section {repr(section)} : (balise) \"sub\" vide.")
    for i in re.findall(r"<b>([\s\S]*?)</b>", section) : # le contenu d'un·e (balise) "b".
        if not i.strip() :
            exit(f"erreur dans la section {repr(section)} : (balise) \"b\" vide.")
    for i in re.findall(r"\{\{c\d+::([\s\S]*?)(::([\s\S]*?))?\}\}", section) : # une liste de triplets représentant le contenu d'un trou : [ texte A, "", "" ] ou [ texte A, "::" + texte B, texte B ]
        if (not i[0].strip() and not i[1].strip()) or (not i[0].strip() and not i[2].strip()) :
            exit(f"erreur dans la section {repr(section)} : trou vide.")
# fin des vérifications.

# remplacement des (caractères) "<" et ">".
texte = re.sub(r"<(?!(/?(b|sup|sub)>)|/span>|span style=\"color:red;\">|img src=\"((.|\n)+?)\" />)", "&lt;", texte)
texte = re.sub(r"(?<!<(/?(b|sup|sub)|/span|span style=\"color:red;\"|img src=\"((.|\n)+?)))>", "&gt;", texte)

# modification du contenu des balises et des trous.
for i in re.findall(r"<img src=\"([\s\S]*?)\" />", texte) : # le contenu d'un (attribut) "src" de (balise) "img".
    texte = texte.replace(f"<img src=\"{i}\" />", f"<img src=\"{i.strip()}\" />")
for i in re.findall(r"<span style=\"color:red;\">([\s\S]*?)</span>", texte) : # le contenu d'un·e (balise) "span".
    texte = texte.replace(f"<span style=\"color:red;\">{i}</span>", f"<span style=\"color:red;\">{i.strip()}</span>")
for i in re.findall(r"<sup>([\s\S]*?)</sup>", texte) : # le contenu d'un·e (balise) "sup".
    texte = texte.replace(f"<sup>{i}</sup>", f"<sup>{i.strip()}</sup>")
for i in re.findall(r"<sub>([\s\S]*?)</sub>", texte) : # le contenu d'un·e (balise) "sub".
    texte = texte.replace(f"<sub>{i}</sub>", f"<sub>{i.strip()}</sub>")
for i in re.findall(r"<b>([\s\S]*?)</b>", texte) : # le contenu d'un·e (balise) "b".
    texte = texte.replace(f"<b>{i}</b>", f"<b>{i.strip()}</b>")
for i in re.findall(r"\{\{c(\d+)::([\s\S]*?)(::([\s\S]*?))?\}\}", texte) : # une liste de quadruplets [ numéro d'un trou, contenu d'un trou, "", "" ] ou [ numéro d'un trou, contenu d'un trou, "::" + contenu d'un indice de trou, contenu d'un indice de trou ].
    texte = texte.replace("{{" + f"c{i[0]}::{i[1]}" + "}}", "{{" + f"c{i[0]}::{i[1].strip()}" + "}}")
    texte = texte.replace("{{" + f"c{i[0]}::{i[1]}::{i[3]}" + "}}", "{{" + f"c{i[0]}::{i[1].strip()}::{i[3].strip()}" + "}}")

c1 = [] # la liste des sections (de type) "c1", une liste de listes (correspondant aux champs de la section).
c2 = [] # la liste des sections (de type) "c2", une liste de listes (correspondant aux champs de la section).
c3 = [] # la liste des sections (de type) "c3", une liste de listes (correspondant aux champs de la section).
t1 = [] # la liste des sections (de type) "t1", une liste de listes (correspondant aux champs de la section).
t2 = [] # la liste des sections (de type) "t2", une liste de listes (correspondant aux champs de la section).
t3 = [] # la liste des sections (de type) "t3", une liste de listes (correspondant aux champs de la section).
vf = [] # la liste des sections (de type) "vf", une liste de listes (correspondant aux champs de la section).
r = [] # la liste des sections (de type) "r", une liste de listes (correspondant aux champs de la section).
o = [] # la liste des sections (de type) "o", une liste de listes (correspondant aux champs de la section).
a = [] # la liste des sections (de type) "a", une liste de listes (correspondant aux champs de la section).
sections = c1, c2, c3, t1, t2, t3, vf, r, o, a

# début du remplissage des sections.
# on veut remplir les sections sans se préoccuper des champs ni des textes à trous.
# on se base sur les séparateurs et on met les (sections de type) "t" dans leurs (sections de type) "c" correspondants.
contenu = [] # le contenu d'une section, une liste de (contenus de) lignes.
section_courante = [] # la section dans laquelle on doit ajouter "contenu". le contenu des premières lignes (vides) étant ajouté à "[]", elle seront bien ignorées.
for ligne in texte.splitlines() :
    ligne = ligne.strip()
    if ligne in ("-", "--", "---", "-vf", "-o", "-r", "-a") : # si la ligne est un séparateur.
        section_courante.append("\n".join(contenu))
        contenu = []

        # mise à jour de "section_courante".
        if ligne == "-" :
            section_courante = c1
        elif ligne == "--" :
            section_courante = c2
        elif ligne == "---" :
            section_courante = c3
        elif ligne == "-vf" :
            section_courante = vf
        elif ligne == "-o" :
            section_courante = o
        elif ligne == "-r" :
            section_courante = r
        else : # -a.
            section_courante = a
    else :
        contenu.append(ligne)
if contenu != [] : # s'il n'y a pas de séparateur à la fin du sas.
    section_courante.append("\n".join(contenu))

# les (sections de type) "t" sont dans leurs (sections de type) "c" correspondants.
# on veut mettre les (sections de type) "t" dans leurs bonnes sections.
for i, sections_mélangées in enumerate((c1, c2, c3)) : # sections_mélangées : une liste de sections d'un (même) paquet Anki à séparer selon ses sections (de type) "c" et "t".
# i = 0 <-> (section de type) "c1" <-> (paquet) "base"
# i = 2 <-> (section de type) "c2" <-> (paquet) "à taper"
# i = 3 <-> (section de type) "c3" <-> (paquet) "à écrire".
    sections_mélangées = sections_mélangées.copy()
    for section in sections_mélangées : # une section (de type) "c" ou "t".
        if re.search(r"\{\{c\d+::(.|\n)*\}\}", section) :
            if i == 0 : # si la section est basique.
                t1.append(section)
                c1.remove(section)
            elif i == 1 : # si la section est à taper.
                t2.append(section)
                c2.remove(section)
            else : # si la section est à écrire.
                t3.append(section)
                c3.remove(section)

# "c1", "c2", "c3", "t1", "t2", "t3", "vf", "r", "o" et "a" sont maintenant des listes de chaînes de caractères.

# traitement des champs.
# on veut vérifier le nombre de champs et le contenu de chaque section.
# on veut supprimer les sections vides, séparer et encoder les champs.
for i, sections_type in enumerate(sections) : # sections_type : une liste de sections du même type.
    nombre_de_champs = None # le nombre de champs théorique des sections de "sections_type".
    if i in (0, 2, 3, 4, 5, 6, 7) : # pour "c1", "c3", "t1", "t2", "t3", "vf" et "r".
        nombre_de_champs = 2
    elif i in (1, 8) : # pour "c2" et "o".
        nombre_de_champs = 3
    else : # i == 9 pour "a".
        nombre_de_champs = 4

    sections_type_copie = sections_type.copy()
    for indice_section in range(len(sections_type_copie)) :
        section = sections_type_copie[indice_section]
        sections_type.remove(section)

        champs = re.split(r"(?<!\\)@", section, nombre_de_champs - 1) # la liste des champs de "section" spécifiés dans le sas.

        # début de vérifications.
        if len(re.findall(r"(?<!\\)@", section)) > (nombre_de_champs - 1) :
            commentaires.append(f"\"@\" non échappé dans la section {repr(section)}")

        vide = True
        for champ in champs :
            if champ.strip() :
                vide = False
                break
        if not vide :
            if not champs[0].strip() :
                exit(f"erreur dans la section {repr(section)} : premier champ vide.")
            if i not in (3, 4, 5) : # si la section n'est pas de type "t".
                if (len(champs) < 2) or not champs[1].strip() :
                    exit(f"erreur dans la section {repr(section)} : 2e champ vide.")
            else : # la section est de type "t".
                if len(champs) >= 2 : # si (le champ) "Extra" est spécifié.
                    if re.search(r"\{\{c\d+::(.|\n)*\}\}", champs[1]) :
                        exit(f"erreur dans la section {repr(section)} : trou dans (le champ) \"Extra\".")
        # fin de vérifications.

            # encodage de la section.
            if i == 9 and len(champs) == 2 : # si la section est de type "a" et que 2 champs seulement sont spécifiés dans le sas.
                champs.insert(1, "")
            nouveaux_champs = []
            for champ in champs :
                nouveau_champ = champ.strip().replace("\n", "<br />")
                nouveau_champ = nouveau_champ.replace("\\@", "@")
                nouveaux_champs.append(nouveau_champ)
            nouveaux_champs.extend([''] * (nombre_de_champs - len(nouveaux_champs)))
            sections_type.append(nouveaux_champs)

# "c1", "c2", "c3", "t1", "t2", "t3", "vf", "r", "o" et "a" sont maintenant des listes de listes de chaînes de caractères.

# remplacement des guillemets initiaux par "&quot;"
for i in range(len(sections)) :
    for j in range(len(sections[i])) :
        for k in range(len(sections[i][j])) :
            if sections[i][j][k].startswith('"') :
                sections[i][j][k] = "&quot;" + sections[i][j][k][1:]

espion = [] # le contenu des sections non vides, par types ; une chaîne de caractères.
taille_des_sections = [] # la taille de chaque [ type de section ] non vide, une chaîne de caractères.
if c1 :
    espion.append(f"c1 : {c1}\n-\n")
    taille_des_sections.append(f"c1 : {len(c1)}\n-\n")
if c2 :
    espion.append(f"c2 : {c2}\n-\n")
    taille_des_sections.append(f"c2 : {len(c2)}\n-\n")
if c3 :
    espion.append(f"c3 : {c3}\n-\n")
    taille_des_sections.append(f"c3 : {len(c3)}\n-\n")
if t1 :
    espion.append(f"t1 : {t1}\n-\n")
    taille_des_sections.append(f"t1 : {len(t1)}\n-\n")
if t2 :
    espion.append(f"t2 : {t2}\n-\n")
    taille_des_sections.append(f"t2 : {len(t2)}\n-\n")
if t3 :
    espion.append(f"t3 : {t3}\n-\n")
    taille_des_sections.append(f"t3 : {len(t3)}\n-\n")
if vf :
    espion.append(f"vf : {vf}\n-\n")
    taille_des_sections.append(f"vf : {len(vf)}\n-\n")
if r :
    espion.append(f"r : {r}\n-\n")
    taille_des_sections.append(f"r : {len(r)}\n-\n")
if o :
    espion.append(f"o : {o}\n-\n")
    taille_des_sections.append(f"o : {len(o)}\n-\n")
if a :
    espion.append(f"a : {a}\n-\n")
    taille_des_sections.append(f"a : {len(a)}\n-\n")
espion = "".join(espion)
taille_des_sections = "".join(taille_des_sections)

if not(any((c1, c2, c3, t1, t2, t3, vf, r, o, a))) :
    print("sas vide.\n-")
else :
    print("contenus :\n" + espion, end = "")
    print("tailles :\n" + taille_des_sections, end = "")

if commentaires :
    print("commentaires :")
    for commentaire in commentaires :
        print(commentaire.strip(), "\n-")

# création des fichiers.
for i, sections_type in enumerate(sections) : # une liste de sections du même type.
    if sections_type :
        nom = [nom for nom, valeur in locals().items() if valeur is sections_type][0] # un nom de type de section.
        f = open("/Users/quentinhauuy/Downloads/" + nom + ".txt", "w")
        for section in sections_type : # une section de "sections_type", une liste de champs.
            f.write(section[0])
            for champ in section : # un champ de "section".
                if champ is not section[0] :
                    if i != 9 : # si la section n'est pas de type "a".
                        f.write("\t")
                        f.write(champ)
                    else :
                        f.write("\n")
                        if champ :
                            f.write(champ)
                        else :
                            f.write("<p></p>")
            if i != 9 :
                f.write("\n")
            else :
                f.write("\n-\n")
        f.close()

# déplacement des images.
source = "/Users/quentinhauuy/Downloads" # le dossier des téléchargements.
cible = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/collection.media" # le dossier des images d'Anki.
# on veut déplacer les images de "source" vers "cible".
import os
fichiers = os.listdir(source) # la liste des fichiers de "source".
for fichier in fichiers :
    if fichier.endswith(".png") or fichier.endswith(".jpg") or fichier.endswith(".jpeg") or fichier.endswith(".gif") or fichier.endswith(".bmp") or fichier.endswith(".tiff") or fichier.endswith(".webp") or fichier.endswith(".svg") or fichier.endswith(".PNG") or fichier.endswith(".JPG") or fichier.endswith(".JPEG") or fichier.endswith(".GIF") or fichier.endswith(".BMP") or fichier.endswith(".TIFF") or fichier.endswith(".WEBP") or fichier.endswith(".SVG") :
        os.rename(os.path.join(source, fichier), os.path.join(cible, fichier))

# on veut donner la possibilité à l'utilisateur de supprimer rapidement le sas et les fichiers texte créés.
input("appuyez sur entrée pour supprimer le sas et les fichiers créés.")

# suppression des fichiers.
for fichier in fichiers :
    if re.search(r"(c1|c2|c3|t1|t2|t3|vf|r|o|a)\.txt", fichier) :
        os.remove(os.path.join(source, fichier))

# sauvegarde et suppression du sas.
corbeille = "/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/sas.trash"
# on veut garder dans "corbeille" une sauvegarde des 10 derniers sas encodés.
os.remove(os.path.join(corbeille, "9.txt"))
for i in range(8, -1, -1) :
    os.rename(os.path.join(corbeille, str(i) + ".txt"), os.path.join(corbeille, str(i + 1) + ".txt"))
import shutil
shutil.copy(sas, corbeille + "/0.txt")
f = open(sas, "w")
f.write("-\n")
f.close()
