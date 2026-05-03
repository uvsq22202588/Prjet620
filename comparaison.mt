// État I : On cherche le premier bit non lu de z
I, 0 -> VU_0, ., r     // On remplace le bit lu par .
I, 1 -> VU_1, ., r     // On remplace le bit lu par .
I, . -> I, ., r        // On passe par-dessus les bits déjà consommés
I, # -> BOUCLE, #, r   // Si on arrive au # sans avoir tranché, les mots sont égaux (donc z < y est faux)

// On a lu un 0 dans z, on traverse pour voir le bit correspondant dans y
VU_0, 0 -> VU_0, 0, r
VU_0, 1 -> VU_0, 1, r
VU_0, . -> VU_0, ., r
VU_0, # -> COMP_0, #, r

// On a lu un 1 dans z
VU_1, 0 -> VU_1, 0, r
VU_1, 1 -> VU_1, 1, r
VU_1, . -> VU_1, ., r
VU_1, # -> COMP_1, #, r

// Comparaison effective (on ignore les . des anciennes comparaisons)
COMP_0, . -> COMP_0, ., r
COMP_1, . -> COMP_1, ., r

COMP_0, 0 -> RETOUR, ., l // 0 == 0, on continue (remplace par .)
COMP_0, 1 -> F, 1, s      // 0 < 1, GAGNÉ (arrêt)
COMP_1, 1 -> RETOUR, ., l // 1 == 1, on continue (remplace par .)
COMP_1, 0 -> BOUCLE, 0, r // 1 > 0, PERDU (boucle infinie)

// Cas où le deuxième mot est plus court (erreur)
COMP_0, _ -> BOUCLE, _, l
COMP_1, _ -> BOUCLE, _, l

// Retour au début de z pour le bit suivant
RETOUR, 0 -> RETOUR, 0, l
RETOUR, 1 -> RETOUR, 1, l
RETOUR, # -> RETOUR, #, l
RETOUR, . -> RETOUR, ., l // On doit repasser sur les points
RETOUR, _ -> I, _, r      // Quand on touche le vrai vide de gauche, on repart