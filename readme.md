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

il y a 6 possibilités de flashcards Anki correspondant à 6 **sections** différentes possibles :
- `c1` pour type 1 et paquet 1
- `c2` pour type 2 et paquet 2
- `c3` pour type 1 et paquet 3
- `t1` pour type 3 et paquet 1
- `t2` pour type 4 et paquet 2
- `t3` pour type 3 et paquet 3

il y a aussi les sections `ms` pour les flashcards Mosalingua, avec les champs (basés sur Mosalingua Anglais :) `Anglais`, `Extra Anglais`, `Français` et `Extra Français`.
ça fait donc 7 sections différentes possibles.

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

un **changement de champ** au sein d'une section est indiqué par `@`.

un **caractère blanc** est un espace, un retour à la ligne ou une tabulation.

**trimer** un texte signifie lui retirer ses caractères blancs aux extrémités. on dit qu'on *trim* le texte et qu'il est *trimé*.

un champ, ou plus généralement un texte, est **vide** s'il ne contient que des caractères blancs. une section est vide si tous ses champs sont vides.

les **balises** peuvent être :

- `<img src="" />`
- `<span style="color:red;">` et `</span>`
- `<sup>` et `</sup>`
- `<sub>` et `</sub>`
- `<b>` et `</b>`

un **texte de balise** fait référence au contenu de l'attribut *src* de la balise *img* ou au texte contenu entre les balises `<span style="color:red;">` et `</span>`, `<sup>` et `</sup>`, `<sub>` et `</sub>` ou `<b>` et `</b>`.

une **image** est un texte représentant un chemin vers un fichier.

# ce qu'on veut faire

on veut vérifier qu'il n'y a pas d'erreur dans le sas. sinon, on doit pouvoir remonter facilement à la source de l'erreur.

on veut **encoder** le sas, c'est-à-dire le diviser en plusieurs fichiers formatés.

chaque fichier produit doit correspondre à un type de section :
- `1 - 1.txt` pour les sections `c1`
- `2 - 2.txt` pour les sections `c2`
- `1 - 3.txt` pour les sections `c3`
- `3 - 1.txt` pour les sections `t1`
- `4 - 2.txt` pour les sections `t2`
- `3 - 3.txt` pour les sections `t3`
- `mosalingua.txt` pour les sections `ms`

on veut aussi vérifier que les images citées dans le sas existent et les déplacer dans un nouveau dossier.

enfin, on veut réinitialiser le sas et supprimer les fichiers créés. on veut garder une copie des 10 derniers sas traités.

# ce qu'il faut vérifier dans le sas

le texte de l'attribut *src* d'une balise *img* doit correspondre à un fichier existant et, une fois trimé, il ne doit pas contenir autre chose que : espace, caractère alphanumérique, tiret, underscore, parenthèse, point.

aucun trou ne doit être dans le deuxième champ d'une section de type `t`.

il n'est pas nécessaire que tous les champs soient non vides ni même spécifiés par un changement de champ. cependant, une section non vide doit avoir un premier champ non vide et une section de type `c2` doit avoir au moins ses 2 premiers champs non vides.

il ne doit pas y avoir plus de changements de champ que ce qui est possible dans une section.

si on veut utiliser la chaine de caractères `\n-` sans indiquer de changement de section, on doit utiliser `\n\-`. c'est la même logique pour les autres séparateurs.

si on veut utiliser le caractère `@` sans indiquer de changement de champ, on doit utiliser `\@`.

# règles d'encodage

## pour toutes les sections

les tabulations doivent être encodées par 4 espaces.

les champs, les textes de balise et les textes de trou doivent être trimés.
les lignes doivent être trimées de leurs espaces. par exemple, `\n a` doit devenir `\na`.

les retours à la ligne doivent être encodés par `<br />`.

le nombre de champs encodé doit toujours être respecté (même si le nombre de *@* ne correspond pas, par exemple). il doit donc toujours y avoir le bon nombre de changements de champ encodés.

si un champ trimé commence par `"`, alors ce caractère doit être encodé par `&quot;`.

`<` doit être encodé par `&lt;` et `>` doit être encodé par `&gt;` (sauf pour les balises définies précédemment).

## pour toutes les sections sauf `ms`

il doit y avoir une section encodée par ligne.

les changements de champ doivent être encodés par `\t`.

## pour les sections `ms`

lorsque seulement deux champs sont spécifiés, ce sont les champs `Anglais` et `Français`.

les changements de section doivent être encodés par `\n-\n`.

les changements de champ doivent être encodés par `\n`.

les champs vides doivent être encodés par `<p></p>`.
