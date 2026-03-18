// État I : On cherche le premier bit de z
I, 0 -> VU_0, _, r
I, 1 -> VU_1, _, r
I, # -> BOUCLE, #, r  // z est fini, si y n'est pas fini alors z < y

// On a lu un 0 dans z, on traverse # pour voir le bit correspondant dans y
VU_0, 0 -> VU_0, 0, r
VU_0, 1 -> VU_0, 1, r
VU_0, # -> COMP_0, #, r

// On a lu un 1 dans z
VU_1, 0 -> VU_1, 0, r
VU_1, 1 -> VU_1, 1, r
VU_1, # -> COMP_1, #, r

// Comparaison effective
COMP_0, 0 -> RETOUR, _, l // 0 == 0, on continue
COMP_0, 1 -> F, 1, s       // 0 < 1, GAGNÉ (arrêt)
COMP_1, 1 -> RETOUR, _, l // 1 == 1, on continue
COMP_1, 0 -> BOUCLE, 0, r // 1 > 0, PERDU (boucle)

// Retour au début de z pour le bit suivant
RETOUR, 0 -> RETOUR, 0, l
RETOUR, 1 -> RETOUR, 1, l
RETOUR, # -> RETOUR, #, l
RETOUR, _ -> I, _, r

// État de boucle infinie
BOUCLE, 0 -> BOUCLE, 0, r
BOUCLE, 1 -> BOUCLE, 1, r
BOUCLE, # -> BOUCLE, #, r
BOUCLE, _ -> BOUCLE, _, l