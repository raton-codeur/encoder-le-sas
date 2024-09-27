# infos générales et définitions

il y a 3 **paquets de flashcards** sur Anki :
- `1 - base`
- `2 - taper`
- `3 - écrire`

il y a 4 **types de flashcards** Anki :
- `1 - carte` composé des **champs** `Recto` et `Verso`
- `2 - carte à taper` composé des champs `Recto`, `Verso` et `Extra`
- `3 - trou` composé des champs `Texte` et `Extra`
- `4 - trou à taper` composé des champs `Texte` et `Extra`

**sas** est le fichier `/Users/quentinhauuy/Documents/à rentrer/sas.txt`. il contient une succession de **séparateurs** et de **sections**.

il y a 6 possibilités de flashcards Anki correspondant à 6 **sections** différentes possibles dans le sas :
- `c1` pour type 1 et paquet 1
- `c2` pour type 2 et paquet 2
- `c3` pour type 1 et paquet 3
- `t1` pour type 3 et paquet 1
- `t2` pour type 4 et paquet 2
- `t3` pour type 3 et paquet 3

il y a aussi les sections d'anglais (`a`) pour les flashcards Mosalingua, avec les champs `Anglais`, `Extra Anglais`, `Français` et `Extra Français`.  
ça fait donc 7 sections différentes possibles.

un **séparateur** dans le sas peut être :
- `\n-` pour le paquet 1
- `\n--` pour le paquet 2
- `\n---` pour le paquet 3
- `\n-a` pour l'anglais

une section est identifiée non seulement par le séparateur qui la précède mais aussi par son contenu. en effet :

- `\n-` identifie `c1` et `t1`
- `\n--` identifie `c2` et `t2`
- `\n---` identifie `c3` et `t3`

cependant, une section de type `t` comporte au moins un **trou**. c'est ce qui la différencie de son homologue de type `c`.

un **trou** est une chaîne de caractères de la forme `{{c` + [ un nombre ] + `::` + [ un texte ] (+ `::` + [ un texte ]) + `}}`.

un **changement de champ** au sein d'une section est indiqué par `@`.

un champ, ou plus généralement un texte, est **vide** s'il ne contient que des caractères blancs. une section est vide si tous ses champs sont vides.

le sas peut contenir des noms d'**images** qui se situent dans le dossier `/Users/quentinhauuy/Downloads`.

les **balises** du sas sont :

- `<img src="" />`
- `<span style="color:red;">` et `</span>`
- `<sup>` et `</sup>`
- `<sub>` et `</sub>`
- `<b>` et `</b>`

un **texte de balise** fait référence au contenu de l'attribut *src* de la balise *img* ou au texte contenu entre les balises `<span style="color:red;">` et `</span>`, `<sup>` et `</sup>`, `<sub>` et `</sub>` ou `<b>` et `</b>`.

# ce qu'on veut faire

on veut vérifier qu'il n'y a pas d'erreur dans le sas. si tout est correct, on veut **encoder** le sas, c'est-à-dire, le re-diviser en plusieurs fichiers formatés.

chaque fichier produit doit correspondre à un type de section :
- le fichier `1 - 1` pour les sections `c1`
- `2 - 2` pour les sections `c2`
- `1 - 3` pour les sections `c3`
- `3 - 1` pour les sections `t1`
- `4 - 2` pour les sections `t2`
- `3 - 3` pour les sections `t3`
- `anglais` pour les sections `a`

on veut aussi déplacer les images mensionnées dans le sas vers `/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/collection.media`.

dans un deuxième temps, on veut réinitialiser le sas et supprimer les fichiers créés. on veut garder une copie des derniers sas traités dans le dossier `/Users/quentinhauuy/Library/Application Support/Anki2/Quentin/sas.trash`.

# règles pour le sas

il n'est pas nécessaire que tous les champs soient non vides ni même spécifiés par un changement de champ. cependant, une section non vide doit avoir un premier champ non vide et une section de type `c2` doit avoir au moins ses 2 premiers champs non vides.  

il ne doit pas y avoir plus de changements de champ que ce qui est possible dans une section.

les textes de balise ne doivent pas être vides.

il ne doit pas y avoir de tabulation dans le fichier.

si on veut utiliser la chaine de caractères `\n-` sans indiquer de changement de section, on doit utiliser `\n\-`. c'est la même logique pour les autres séparateurs.

si on veut utiliser le caractère `@` sans indiquer de changement de champ, on doit utiliser `\@`.

# règles d'encodage

## pour toutes les sections

les retours à la ligne doivent être encodés par `<br />`.

les champs, les textes de balise et les textes de trou doivent être trimés.  
les lignes doivent être trimées de leurs espaces. par exemple, `\n a` doit devenir `\na`. 

le nombre de champs dans un texte encodé doit toujours être respecté (même si un champ est vide par exemple) avec un nombre de changements de champ conséquent.

si un champ commence par `"`, alors ce caractère doit être encodé par `&quot;`.

tous les `<` doivent être encodés par `&lt;` et tous les `>` doivent être encodés par `&gt;` (sauf pour les balises où ils sont encodés tels quels).

le texte de l'attribut *src* d'une balise *img*, une fois trimé, ne doit pas contenir autre chose que : espace, caractère alphanumérique, tiret, underscore, parenthèse, point.

aucun trou ne doit être dans le deuxième champ d'une section de type `t`.

## pour toutes les sections sauf `a`

il doit y avoir une section encodée par ligne.

les changements de champ doivent être encodés par `\t`.

## pour les sections `a`

les changements de section doivent être encodés par `\n-\n`.

les changements de champ doivent être encodés par `\n`.

les champs vides doivent être encodés par `<p></p>`.

lorsque seulement deux champs sont spécifiés, ce sont les champs `Anglais` et `Français`.

# divers

`\t` représente le caractère *tabulation horizontale*.

`\n` représente le caractère *retour à la ligne*.

un *caractère blanc* est un espace, un retour à la ligne ou une tabulation.

*trimer* un texte signifie lui retirer ses caractères blancs aux extrémités. on dit qu'on *trim* le texte et qu'il est *trimé*.
