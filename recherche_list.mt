// Ruban 0: Entrée (x#w1#w2...), Ruban 1: Zone de travail
// Format: etat, lu0, lu1 -> suivant, ecrit0, ecrit1, dir0, dir1

// PHASE 1 : Copie de x sur le Ruban 1
I, 0, _ -> I, 0, 0, r, r
I, 1, _ -> I, 1, 1, r, r
I, #, _ -> RECULER, #, _, s, l

// PHASE 2 : Reculer la tête du Ruban 1 au début de x
// On cherche le vide '_' à gauche du mot copié
RECULER, #, 0 -> RECULER, #, 0, s, l
RECULER, #, 1 -> RECULER, #, 1, s, l
RECULER, #, _ -> COMPARER, #, _, r, r

// PHASE 3 : Comparaison bit à bit entre Ruban 0 et Ruban 1
COMPARER, 0, 0 -> COMPARER, 0, 0, r, r
COMPARER, 1, 1 -> COMPARER, 1, 1, r, r

// Cas de succès : les deux mots finissent en même temps
COMPARER, #, _ -> F, #, _, s, s
COMPARER, _, _ -> F, _, _, s, s

// Cas d'échec : mismatch de bit ou de longueur
COMPARER, 0, 1 -> SAUTER, 0, 1, r, s
COMPARER, 1, 0 -> SAUTER, 1, 0, r, s
COMPARER, #, 0 -> SAUTER, #, 0, r, s
COMPARER, 0, _ -> SAUTER, 0, _, r, s

// PHASE 4 : Sauter le mot actuel sur le Ruban 0
// On doit accepter 0 ou 1 sur le Ruban 0, et peu importe (0, 1 ou _) sur le Ruban 1
SAUTER, 0, 0 -> SAUTER, 0, 0, r, s
SAUTER, 1, 0 -> SAUTER, 1, 0, r, s
SAUTER, 0, 1 -> SAUTER, 0, 1, r, s
SAUTER, 1, 1 -> SAUTER, 1, 1, r, s
SAUTER, 0, _ -> SAUTER, 0, _, r, s
SAUTER, 1, _ -> SAUTER, 1, _, r, s

// On a trouvé le séparateur, on réinitialise la recherche
SAUTER, #, 0 -> RECULER, #, 0, s, l
SAUTER, #, 1 -> RECULER, #, 1, s, l
SAUTER, #, _ -> RECULER, #, _, s, l

// Si on arrive au bout du ruban 0 sans avoir trouvé x
SAUTER, _, 0 -> BOUCLE, _, 0, s, s
SAUTER, _, 1 -> BOUCLE, _, 1, s, s
SAUTER, _, _ -> BOUCLE, _, _, s, s

BOUCLE, _, _ -> BOUCLE, _, _, s, s