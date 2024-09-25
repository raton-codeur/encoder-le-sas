# infos générales
le `sas` est un fichier texte qui contient une succession de `séparateurs` et de `sections`

il y a 3 paquets de flashcards sur Anki :
● "1 - base"
● "2 - taper"
● "3 - écrire"

il y a 4 types de flashcards Anki :
● "1 - carte" composé des champs "Recto" et "Verso"
● "2 - carte à taper" composé des champs "Recto", "Verso" et "Extra"
● "3 - trou" composé des champs "Texte" et "Extra"
● "4 - trou à taper" composé des champs "Texte" et "Extra"

il y a 6 possibilités de flashcards Anki correspondant à 6 sections différentes possibles dans le sas :
● "c1" pour type 1 et paquet 1
● "c2" pour type 2 et paquet 2
● "c3" pour type 1 et paquet 3
● "t1" pour type 3 et paquet 1
● "t2" pour type 4 et paquet 2
● "t3" pour type 3 et paquet 3
il y a aussi les sections d'anglais ("a") pour les flashcards Mosalingua, avec les champs "Anglais", "Extra Anglais", "Français" et "Extra Français"

un séparateur peut être :
● "\n-" pour le paquet 1
● "\n--" pour le paquet 2
● "\n---" pour le paquet 3
● "\n-a" pour l'anglais
si on veut utiliser ses chaines dans le sas pour autre chose que séparer des sections, on doit échapper le premier caractère non blanc avec un antislash. par exemple : "\n\-" deviendra "\n-".

une section est identifiée par le séparateur qui la précède et par son contenu. en effet :
● (le séparateur) "-)" identifie (les sections de type) c1 et t1
● (le séparateur) "" identifie (les sections de type) c2 et t2
● (le séparateur) "-)-" identifie (les sections de type) c3 et t3 ; mais un·e (section de type) "t" comporte au moins un·e (chaine de caractères) "{{c" + [ un nombre ] + "::" (+ [ du texte ]) + "}}". c'est ce qui la différencie de son homologue (de type) "c".

un changement de champ est indiqué par (le caractère) "@". si on veut encoder (le caractère) "@" (sans changement de champ) il faut utiliser "\@".
un champ ne contenant que des caractères blancs est considéré comme étant vide.
une section dont tous les champs sont vide est considérée comme étant vide.
une section non vide doit avoir un premier champ non vide.
une section c2 doit avoir au moins ses 2 premiers champs non vides.
il n'est pas nécessaire que tous les champs soient non vides ni même spécifiés dans le sas (par un changement de champ (avec "@")).

# ce qu'on veut faire
on veut vérifier que la structure du sas est correcte et produire différents fichiers correspondant aux différents types des sections du sas mis en forme. une telle section, mise en forme, est "encodée".
dans un type de fichier produit donné, excepté pour (le type de section) "a", il doit y avoir une section encodée par ligne. dans une section encodée, les retours à la ligne doivent être indiqués par (la chaîne de caractères) "<br />" et un changement de champ doit être indiqué par une tabulation. en outre, il ne doit pas y avoir de tabulation dans le sas.
dans une section encodée, le nombre de champs (donc de tabulations) doit être précisément respecté, selon la définition du type de la section, même si un champ est vide ou n'est pas spécifié dans le sas.
un champ encodé ne doit pas commencer ou finir par un caractère blanc et, dans un champ encodé, une ligne ne doit pas avoir de caractère blanc à ses extrémités.
si un champ commence par (le caractère) '"', alors celui-ci doit être encodé par (la chaîne de caractères) "&quot;".

le fichier des sections c1 doit s'appeler "1 - 1"
le fichier des sections c2 doit s'appeler "2 - 2"
le fichier des sections c3 doit s'appeler "1 - 3"
le fichier des sections t1 doit s'appeler "3 - 1"
le fichier des sections t2 doit s'appeler "4 - 2"
le fichier des sections t3 doit s'appeler "3 - 3"
le fichier des sections a doit s'appeler "anglais"

dans le fichier des sections (encodées) de type "a", les retours à la ligne doivent être indiqués par (la chaîne de caractères) "<br />", un changement de champ doit être indiqué par un retour à ligne et un changement de section doit être indiqué par (la chaîne de caractères) "\n-\n".
un champ encodé ne doit pas commencer ou finir par un caractère blanc et, dans un champ encodé, une ligne ne doit pas avoir de caractère blanc à ses extrémités. si un champ est vide ou n'est pas spécifié dans le sas, il doit être encodé par (la chaîne de caractères) "<p></p>".

s'il y a plus de changements de champ que de changements de champ possibles dans une section, alors c'est une erreur.
les champs sont remplis de manière séquentielle selon la définition de la section. toutefois, il y a une exception pour les sections de type "a". en effet, lorsque deux champs sont spécifiés pour une section "a", ce sont les champs "Anglais" et "Français". pour 3 champs, ce sont bien de nouveau "Anglais", "Extra Anglais" et "Français".

tous les (caractères) "<" du sas doivent être encodés par "&lt;" et tous les (caractères) ">" doivent être encodés par "&gt;", sauf dans le cas des balises suivantes :
● <img src="" />
● <span style="color:red;"> et </span>
● <sup> et </sup>
● <sub> et </sub>
● <b> et </b>
(les caractères) "<" et ">" y sont alors encodés normalement.
par ailleurs, il doit y avoir du texte dans l· (attribut) "src" de (la balise) "img", entre les balises <span style="color:red;"> et </span>, <sup> et </sup>, <sub> et </sub> et <b> et </b>. ces textes ne doivent pas être composés uniquement de caractères blancs et, pour les encoder, on doit supprimer les caractères blancs de leurs extrémités.
le texte dans l· (attribut) "src" de (une balise) "img" dépouillé de ses caractères blancs aux extrémités ne doit pas contenir autre chose que : espace, caractère alphanumérique, tiret, underscore, parenthèse, point.

un trou est une chaîne de caractères de la forme "{{c" + [ un nombre ] + "::" + [ A : un texte ] + "}}" ou "{{c" + [ un nombre ] + "::" + [ A : un texte ] + "::" + [ B : un texte ] + "}}".
le texte d'un trou est vide s'il est composé uniquement de caractères blancs.
[ le texte A d'un trou ] peut être vide uniquement si le texte B est présent dans le trou et qu'il n'est pas vide. de la même façon, [ le texte B d'un trou ] peut être vide uniquement si le texte A n'est pas vide.
pour encoder le texte d'un trou, on doit supprimer les caractères blancs de ses extrémités.
aucun trou ne doit être dans le deuxième champ d'une section (de type) "t".

enfin, on veut déplacer les images du dossier des téléchargements vers le dossier des images d'Anki et on veut pouvoir supprimer rapidement le sas et tous les fichiers textes créés.



# divers
un caractère blanc est un espace, un retour à la ligne ou une tabulation
