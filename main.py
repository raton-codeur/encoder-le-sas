import sys
import os
import re
import shutil
from send2trash import send2trash

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





