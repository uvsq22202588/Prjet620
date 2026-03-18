class MT:
    def __init__(self, nb_rubans):
        self.nb_rubans = nb_rubans # 
        self.etats = set()         # Ensemble des noms d'états
        self.etat_initial = "I"    # Par défaut "I" 
        self.etat_final = "F"      # Par défaut "F" 
        self.alphabet_travail = {'0', '1', '#', '_', '.'} 
        
        # Les transitions seront stockées ainsi : 
        # {(etat_depuis, (caractères_lus)): (nouvel_etat, (caractères_écrits), (directions))}
        self.transitions = {}

class Configuration:
    def __init__(self, etat_actuel, rubans=None, tetes=None):
        self.etat_actuel = etat_actuel # 
        # Chaque ruban est une liste de caractères pour pouvoir les modifier facilement
        self.rubans = rubans if rubans else [] 
        # Position de la tête sur chaque ruban (index 0 par défaut)
        self.tetes = tetes if tetes else [0] * len(self.rubans)

    