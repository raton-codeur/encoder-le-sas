le sas est un texte de la forme :
séparateur
section
séparateur
section
...
séparateur
section

base, taper, écrire : des paquets de [cartes / flashcards] sur Anki.

un séparateur peut être :
● - ⟶ base
● -- ⟶ taper
● --- ⟶ écrire
● -vf : vrai / faux ⟶ base
● -r : raccourci aText ⟶ taper
● -o : orthographe ⟶ taper
● -a : anglais ⟶ Mosalingua
sur la ligne d'un séparateur, il ne peut pas y avoir autre chose que le séparateur en lui-même, excepté des caractères blancs aux extrémités de la ligne. par exemple, la ligne "   - \t " est un séparateur, alors que la ligne "- a" ne l'est pas.
un caractère blanc peut être (notamment) un espace, une tabulation ou un retour à la ligne.

une section peut être de type :
● c1 : carte 1, une flashcard basique à [ 2 champs : Recto, Verso ].
● c2 : carte 2, une flashcard à taper à [ 3 champs : Recto, Verso, Extra ].
● c3 : carte 3, une flashcard à écrire à [ 2 champs : Recto, Verso ].
● t1 : trou 1, un texte à trous basique à [ 2 champs : Texte, Extra ].
● t2 : trou 2, un texte à trous à taper à [ 2 champs : Texte, Extra ].
● t3 : trou 3, un texte à trous à écrire à [ 2 champs : Texte, Extra ].
● vf : vrai / faux, une flashcard basique à [ 2 champs : Recto, Verso ].
● r : raccourci aText, une flashcard à taper à [ 2 champs : Recto, Verso ].
● o : orthographe, une flashcard à taper à [ 3 champs : Recto, Verso, Extra ].
● a : anglais, une flashcard Mosalingua à [ 4 champs : Anglais, Extra Anglais, Français, Extra Français ].

une section est identifiée par le séparateur qui la précède et par son contenu. en particulier, on a :
● (le séparateur) "-" identifie (les sections de type) "c1" et "t1"
● (le séparateur) "--" identifie (les sections de type) "c2" et "t2"
● (le séparateur) "---" identifie (les sections de type) "c3" et "t3".
cependant, un·e (section de type) "t" comporte au moins un·e (chaine de caractères) "{{c" + [ un nombre ] + "::" (+ [ du texte ]) + "}}". c'est ce qui la différencie de son homologue (de type) "c".

une section ou un champ ne contenant que des caractères blancs est considéré comme étant vide.
un changement de champ est indiqué par (le caractère) "@" (peu importe sa position dans la section).
toutes les sections non vides doivent avoir un premier champ non vide ; et toutes les sections non vides, sauf celles de type "t", doivent avoir un deuxième champ non vide. à part cela, il n'est pas nécessaire que tous les champs soient non vides ni même spécifiés dans le sas (par un changement de champ (avec "@")). par exemple, une section à 3 champs peut n'avoir que 2 champs (non vides) spécifiés dans le sas ou 3 champs spécifiés avec un dernier champ vide. une section "t" peut n'avoir qu'un champ spécifié (non vide) dans le sas ou qu'un premier champ non vide spécifié suivi d'un deuxième champ vide. en revenche, une section à 2 champs qui n'est pas de type "t" devra avoir avoir 2 champs non vides et une section à 3 champs ne peut pas avoir un champ vide entre deux champs non vides.

on veut vérifier que la structure du sas est correcte et produire différents fichiers correspondant aux différents types des sections du sas mis en forme. une telle section, mise en forme, est dite "encodée".
dans un type de fichier produit donné, excepté pour (le type de section) "a", il doit y avoir une section encodée par ligne. dans une section encodée, les retours à la ligne doivent être indiqués par (la chaîne de caractères) "<br />" et un changement de champ doit être indiqué par une tabulation. en outre, il ne devrait pas y avoir de tabulation dans le sas. s'il y en a, on doit les remplacer par (la chaîne de caractères) "    " et en informer l'utilisateur.
dans une section encodée, le nombre de champs (donc de tabulations) doit être précisément respecté, selon la définition du type de la section, même si un champ est vide ou n'est pas spécifié dans le sas.
un champ encodé ne doit pas commencer ou finir par un caractère blanc et, dans un champ encodé, une ligne ne doit pas avoir de caractère blanc à ses extrémités.
si un champ commence par (le caractère) '"', alors celui-ci doit être encodé par (la chaîne de caractères) "&quot;".

dans le fichier des sections encodées (de type) "a", les retours à la ligne doivent être indiqués par (la chaîne de caractères) "<br />", un changement de champ doit être indiqué par un retour à ligne et un changement de section doit être indiqué par (la chaîne de caractères) "\n-\n".
un champ encodé ne doit pas commencer ou finir par un caractère blanc et, dans un champ encodé, une ligne ne doit pas avoir de caractère blanc à ses extrémités. si un champ est vide ou n'est pas spécifié dans le sas, il doit être encodé par (la chaîne de caractères) "<p></p>".

dans le sas, le caractère "@" indiquant un changement de champ ne doit pas être encodé dans le fichier produit. il doit être supprimé ou, plus précisément, remplacé par une tabulation. pour pouvoir encoder (le caractère) "@" sans indiquer de changement de champ, on doit utiliser (dans le sas) (le caractère) "@" immédiatement précédé du caractère (d'échappement) "\". (le caractère d'échappement) "\" ne doit alors pas être encodé.
s'il y a plus de changements de champ que de changements de champ possibles dans une section, alors les changements de champ surnuméraires doivent être ignorés : on doit rester dans le dernier champ et les (caractères de changement de champ) "@" surnuméraires doivent être encodés comme des caractères normaux. par ailleurs, on doit informer l'utilisateur que des changements de champ surnuméraires ont été trouvés.
les champs sont remplis de manière séquentielle selon la définition de la section. toutefois, il y a une exception pour les sections de type "a". en effet, lorsque deux champs sont spécifiés pour une section "a", ce sont les champs "Anglais" et "Français". pour 3 champs, ce sont bien de nouveau "Anglais", "Extra Anglais" et "Français".

tous les (caractères) "<" du sas doivent être encodés par "&lt;" et tous les (caractères) ">" doivent être encodés par "&gt;", sauf dans le cas des balises suivantes :
● <img src="" />
● <span style="color:red;"> et </span>
● <sup> et </sup>
● <sub> et </sub>
● <b> et </b>
(les caractères) "<" et ">" y sont alors encodés normalement.
par ailleurs, il doit y avoir du texte dans l· (attribut) "src" de (la balise) "img", entre les balises <span style="color:red;"> et </span>, <sup> et </sup>, <sub> et </sub> et <b> et </b>. ces textes ne doivent pas être composés uniquement de caractères blancs et, pour les encoder, on doit supprimer les caractères blancs de leurs extrémités.
le texte dans l· (attribut) "src" de (une balise) "img" ne doit pas contenir de (caractères) "@". de plus, une fois les caractères blancs de ses extrémités retirés, si ce texte comporte un caractère qui n'est pas
● alphanumérique
● un espace
● un tiret
● un underscore
● une parenthèse
● un point
alors l'image devra être renommée "RENOMMAGE_AUTOMATIQUE_" + [ un numéro unique ] (en gardant son format).

un trou est une chaîne de caractères de la forme "{{c" + [ un nombre ] + "::" + [ A : un texte ] + "}}" ou "{{c" + [ un nombre ] + "::" + [ A : un texte ] + "::" + [ B : un texte ] + "}}".
le texte d'un trou est vide s'il est composé uniquement de caractères blancs.
[ le texte A d'un trou ] peut être vide uniquement si le texte B est présent dans le trou et qu'il n'est pas vide. de la même façon, [ le texte B d'un trou ] peut être vide uniquement si le texte A n'est pas vide.
pour encoder le texte d'un trou, on doit supprimer les caractères blancs de ses extrémités.
aucun trou ne doit être dans le deuxième champ d'une section (de type) "t".

un commentaire peut être introduit dans le sas en utilisant (la chaîne de caractères) "@@". tout texte qui se trouve entre deux (chaînes de caractères) "@@" dans le sas est un commentaire. les commentaires ne doivent pas être encodés mais afficher sur la sortie standard (sans caractère blanc aux extrémités). plus précisément, les (chaînes de caractères) "@@", le texte du commentaire et les caractères blancs qui entourent le commentaire seront encodés comme un unique retour à la ligne.
si un commentaire n'est pas fermé, alors tout se passe comme si le sas se terminait par (la chaîne de caractères) "@@".

enfin, on veut déplacer les images du dossier des téléchargements vers le dossier des images d'Anki et on veut pouvoir supprimer rapidement le sas et tous les fichiers textes créés.

