// Format: etat, lu1, lu2, lu3 -> suivant, ecrit1, ecrit2, ecrit3, dir1, dir2, dir3

// 1. Chercher un '1' sur le ruban 1
I, 1, _, _ -> CHERCHE_M, _, _, _, r, s, s
I, #, _, _ -> F, #, _, _, s, s, s  // Terminé quand on atteint le #

// 2. Aller après le # sur le ruban 1 pour trouver le début de 'm'
CHERCHE_M, 1, _, _ -> CHERCHE_M, 1, _, _, r, s, s
CHERCHE_M, #, _, _ -> COPIE_M, #, _, _, r, s, s

// 3. Parcourir le bloc 'm' et copier chaque '1' sur le ruban 3
COPIE_M, 1, _, _ -> COPIE_M, 1, _, 1, r, s, r
COPIE_M, _, _, _ -> RETOUR, _, _, _, l, s, s // Fin de 'm'

// 4. Revenir au début du ruban 1 pour traiter le '1' suivant
RETOUR, 1, _, _ -> RETOUR, 1, _, _, l, s, s
RETOUR, #, _, _ -> RETOUR, #, _, _, l, s, s
RETOUR, _, _, _ -> I, _, _, _, r, s, s