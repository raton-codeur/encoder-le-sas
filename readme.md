# infos générales et définitions

**`\t`** représente le caractère *tabulation horizontale*.

**`\n`** représente le caractère *retour à la ligne*.

le **sas** est un fichier texte. il contient une succession de **séparateurs** et de **sections**.

il y a 3 **paquets** de flashcards Anki :
- `1 - base`
- `2 - taper`
- `3 - écrire`

il y a 4 **types** de flashcards Anki :
- `1 - carte` composé des **champs** `Recto` et `Verso`
- `2 - carte à taper` composé des champs `Recto`, `Verso` et `Extra`
- `3 - trou` composé des champs `Texte` et `Extra`
- `4 - trou à taper` composé des champs `Texte` et `Extra`

il y a 6 combinaisons de [ paquet et type ] correspondant à 6 **sections** différentes possibles :
- `c1` pour type 1 et paquet 1
- `c2` pour type 2 et paquet 2
- `c3` pour type 1 et paquet 3
- `t1` pour type 3 et paquet 1
- `t2` pour type 4 et paquet 2
- `t3` pour type 3 et paquet 3

il y a aussi les sections `ms` pour les flashcards Mosalingua, avec les champs (basés sur Mosalingua Anglais) `Anglais`, `Extra Anglais`, `Français` et `Extra Français`.
ça fait donc 7 sections différentes possibles.

un changement de champ est indiqué par le caractère *@*.

un **séparateur** peut être :
- `\n-` pour le paquet 1
- `\n--` pour le paquet 2
- `\n---` pour le paquet 3
- `\n-)` pour mosalingua

une section est identifiée non seulement par le séparateur qui la précède mais aussi par son contenu. en effet :

- `\n-` identifie `c1` et `t1`
- `\n--` identifie `c2` et `t2`
- `\n---` identifie `c3` et `t3`

cependant, une section de type `t` comporte au moins un **trou**. c'est ce qui la différencie de son homologue de type `c`.

un **trou** est une chaîne de caractères de la forme `{{c` + [ un nombre ] + `::` + [ un texte ] (+ `::` + [ un texte ]) + `}}`.

une **insertion de prononciation** est chaîne de caractères de la forme `//` + [ un **texte (phonétique)** ] + `//`.

un **caractère blanc** est un espace, un retour à la ligne ou une tabulation.

**trimer** un texte signifie supprimer tous les caractères blancs de ses extrémités. on dit qu'on **trim** le texte et qu'il est **trimé**.

un champ ou un texte est **vide** s'il ne contient que des caractères blancs. à l'inverse, il est **rempli**. une section est vide si tous ses champs sont vides.

les **balises** du sas sont :

- `<img src="" />`
- `<span style="color:red;">` et `</span>`
- `<sup>` et `</sup>`
- `<sub>` et `</sub>`
- `<b>` et `</b>`

un **texte de balise** fait référence au contenu de l'attribut *src* de la balise *img* ou au texte contenu entre les balises `<span style="color:red;">` et `</span>`, `<sup>` et `</sup>`, `<sub>` et `</sub>` ou `<b>` et `</b>`.

une **image_path** est une chaîne de caractères représentant un chemin vers un fichier.

# les arguments

- **sas_path** : le chemin vers le fichier du sas.
- **images_src_dir** : le chemin vers le dossier source des images.
- **images_dst_dir** : le chemin vers le dossier de destination des images.
- **output_dir** : le chemin vers le dossier où seront générés les fichiers de sortie.
- **log_dir** : le chemin vers le dossier de sauvegarde des sas traités.

# ce qu'on veut faire

on veut vérifier qu'il n'y a pas d'erreur, ni dans les arguments, ni dans le sas. s'il y en a une, on veut l'afficher assez précisément.

on veut **encoder** le sas, c'est-à-dire le diviser en plusieurs fichiers formatés. chaque fichier produit doit correspondre à une section :
- `1 - 1.txt` pour les sections `c1`
- `2 - 2.txt` pour les sections `c2`
- `1 - 3.txt` pour les sections `c3`
- `3 - 1.txt` pour les sections `t1`
- `4 - 2.txt` pour les sections `t2`
- `3 - 3.txt` pour les sections `t3`
- `mosalingua.txt` pour les sections `ms`

on dit que le texte d'un tel fichier est **encodé**.

on veut réinitialiser le sas et garder une copie des 10 derniers sas traités.

on veut déplacer les images correspondant aux image_paths dans `images_dst_dir` (si elles n'y sont pas déjà).

# ce qu'il faut vérifier dans le sas

il ne doit pas y avoir de balise *img* dans une section de type `ms`.

le texte d'une balise *img* doit correspondre à un fichier existant dans `images_src_dir` ou `images_dst_dir` et, une fois trimé, il ne doit pas contenir autre chose que : *espace*, *caractère alphanumérique*, *tiret*, *underscore*, *parenthèse*, *point*.

il ne doit pas y avoir plus de changements de champ que ce qu’une section permet.

les sections vides sont ignorées.

il n'est pas nécessaire que tous les champs d’une section soient remplis, ni même spécifiés par un changement de champ. cependant :
- toute section doit avoir son premier champ rempli ;
- une section de type `c2` doit aussi avoir son deuxième champ rempli ;
- une section de type `ms` doit aussi avoir son champ `Français` rempli.

aucun trou ne doit être dans le deuxième champ d'une section de type `t`.

# règles d'encodage

## pour toutes les sections

le nombre de champs encodé doit toujours être respecté (même si le nombre de *@* ne correspond pas). il doit donc toujours y avoir le bon nombre de changements de champ encodé.

les tabulations doivent être encodées par 4 espaces.

les lignes doivent être trimées de leurs espaces. par exemple, `\n a b \n` doit être vu comme `\na b\n`.

les champs, les textes de trou, les textes phonétiques et les textes de balise doivent être trimés.

un `//` encadrant un texte phonétique doit être encodé par `/`.

`<` doit être encodé par `&lt;` et `>` doit être encodé par `&gt;` (sauf si utilisés dans une des balises du sas). `BROKET_LEFT` et `BROKET_RIGHT` ne doivent pas apparaître dans le sas car ils seront utilisés temporairement comme marqueurs lors du remplacement.

si un champ commence par `"`, alors ce caractère doit être encodé par `&quot;`.

les retours à la ligne doivent être encodés par `<br />`.

## pour toutes les sections sauf `ms`

il doit y avoir une section encodée par ligne. autrement dit, les changements de section doivent être encodés par `\n`.

les changements de champ doivent être encodés par `\t`.

## pour les sections `ms`

lorsque seulement deux champs sont spécifiés, ce sont les champs `Anglais` et `Français`.

les changements de section doivent être encodés par `\n-\n`.

les changements de champ doivent être encodés par `\n`.

les champs vides doivent être encodés par `<p></p>`.

## échappement

si on veut encoder `\n-` sans indiquer de changement de section, on doit utiliser `\n\-`. en contrepartie, si on veut encoder `\-` quelque part, on doit utiliser `\\-`.

si on veut encoder `@` sans indiquer de changement de champ, on doit utiliser `\@`. si on veut encoder `\@`, on doit utiliser `\\@`.

si on veut encoder `//` sans insérer de prononciation alors qu'il y a un autre `//` présent, on doit utiliser `\//` sur au moins un des `//`. si on veut encoder `\//`, on doit utiliser `\\//`.
