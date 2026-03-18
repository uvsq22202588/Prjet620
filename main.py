import re

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

def charger_machine(nom_fichier):
    # On lit d'abord pour déterminer le nombre de rubans (k)
    # Dans ce format, le nombre de symboles lus avant '->' donne k
    with open(nom_fichier, 'r') as f:   
        lignes = [l.strip() for l in f if l.strip() and not l.startswith('//')]
    
    # Vérification de sécurité
    if not lignes:
        print(f"Erreur : Le fichier {nom_fichier} est vide ou ne contient aucune transition valide.")
        return None 
    
    # Analyse de la première transition pour déduire k
    premiere_transition = lignes[0].split('->')[0].split(',')
    k = len(premiere_transition) - 1
    
    ma_mt = MT(nb_rubans=k)
    
    for ligne in lignes:
        # On sépare la partie gauche et droite de la flèche
        gauche, droite = ligne.split('->')
        
        # Partie gauche : etat, s1, s2...
        elements_g = [e.strip() for e in gauche.split(',')]
        etat_depuis = elements_g[0]
        symboles_lus = tuple(elements_g[1:])
        
        # Partie droite : nouvel_etat, e1, e2..., d1, d2...
        elements_d = [e.strip() for e in droite.split(',')]
        nouvel_etat = elements_d[0]
        # On sépare les symboles écrits des directions
        symboles_ecrits = tuple(elements_d[1:1+k])
        directions = tuple(elements_d[1+k:])
        
        # On remplit le dictionnaire de la machine [cite: 16]
        ma_mt.transitions[(etat_depuis, symboles_lus)] = (nouvel_etat, symboles_ecrits, directions)
        ma_mt.etats.add(etat_depuis)
        ma_mt.etats.add(nouvel_etat)
        
    return ma_mt

def creer_configuration_initiale(machine, mot_entree):
    # Le ruban 1 contient le mot, les autres rubans (k-1) sont vides
    rubans = []
    
    # Premier ruban avec le mot d'entrée
    rubans.append(list(mot_entree) if mot_entree else ['_'])
    
    # Rubans additionnels vides (on met au moins un symbole vide)
    for _ in range(machine.nb_rubans - 1):
        rubans.append(['_'])
    
    # Toutes les têtes de lecture sont à la position 0
    tetes = [0] * machine.nb_rubans
    
    return Configuration(etat_actuel="I", rubans=rubans, tetes=tetes)

def un_pas_de_calcul(machine, config):
    # 1. Lecture (on gère les indices négatifs ou trop grands)
    symboles_lus = []
    for i in range(machine.nb_rubans):
        pos = config.tetes[i]
        if 0 <= pos < len(config.rubans[i]):
            symboles_lus.append(config.rubans[i][pos])
        else:
            symboles_lus.append('_')
    
    symboles_lus = tuple(symboles_lus)
    
    # 2. Recherche transition
    cle = (config.etat_actuel, symboles_lus)
    if cle not in machine.transitions:
        return False 
    
    nouvel_etat, symboles_ecrits, directions = machine.transitions[cle]
    
    # 3. Mise à jour
    config.etat_actuel = nouvel_etat
    for i in range(machine.nb_rubans):
        # Gestion de l'écriture à gauche (index négatif)
        if config.tetes[i] < 0:
            # On ajoute un vide au début et on remet la tête à 0
            config.rubans[i].insert(0, '_')
            config.tetes[i] = 0
            
        pos = config.tetes[i]
        
        # Gestion de l'écriture à droite
        while pos >= len(config.rubans[i]):
            config.rubans[i].append('_')
            
        config.rubans[i][pos] = symboles_ecrits[i]
        
        # Déplacement SANS bloquer à 0
        d = directions[i].lower()
        if d in ['r', '>']:
            config.tetes[i] += 1
        elif d in ['l', '<']:
            config.tetes[i] -= 1 # On autorise -1, le prochain tour l'insérera à l'index 0
            
    return True
    
    # 2. On cherche la transition correspondante
    cle = (config.etat_actuel, symboles_lus)
    if cle not in machine.transitions:
        # Si aucune transition n'existe, la machine s'arrête (blocage)
        return False 
    
    nouvel_etat, symboles_ecrits, directions = machine.transitions[cle]
    
    # 3. Mise à jour de la configuration
    config.etat_actuel = nouvel_etat
    for i in range(machine.nb_rubans):
        pos = config.tetes[i]
        
        # On s'assure que le ruban est assez long pour écrire
        while pos >= len(config.rubans[i]):
            config.rubans[i].append('_')
            
        # Écriture du symbole
        config.rubans[i][pos] = symboles_ecrits[i]
        
        # Déplacement de la tête (L=gauche, R=droite, S=fixe)
        # Adapté du format turingmachinesimulator : 'l', 'r', 's' ou '<', '>', '-'
        d = directions[i].lower()
        if d in ['r', '>']:
            config.tetes[i] += 1
        elif d in ['l', '<']:
            config.tetes[i] = max(0, config.tetes[i] - 1) # On ne va pas à gauche de 0
            
    return True # Le pas a été effectué avec succès

def afficher_configuration(config):
    """Affiche l'état actuel et le contenu des rubans (Question 5)"""
    print(f"\nÉtat actuel : {config.etat_actuel}")
    for i, ruban in enumerate(config.rubans):
        # On crée une représentation visuelle du ruban
        contenu = "".join(ruban)
        # On place un curseur '^' sous la position de la tête
        curseur = " " * config.tetes[i] + "^"
        print(f"Ruban {i} : {contenu}")
        print(f"         {curseur}")

def simuler(machine, mot_entree, debug=True):
    """Simule le calcul jusqu'à l'état final (Question 4)"""
    # Initialisation
    config = creer_configuration_initiale(machine, mot_entree)
    
    nb_etapes = 0
    
    while config.etat_actuel != machine.etat_final:
        if debug:
            afficher_configuration(config)
        
        # On exécute un pas
        succes = un_pas_de_calcul(machine, config)
        
        # Si aucune transition n'est trouvée et qu'on n'est pas à l'état final
        if not succes:
            print("\nMachine bloquée : aucune transition trouvée.")
            return config, False
        
        nb_etapes += 1
        
        # Sécurité pour éviter les boucles infinies pendant tes tests
        if nb_etapes > 1000:
            print("\nArrêt : Limite d'étapes atteinte (boucle infinie probable).")
            return config, False

    # Affichage de la configuration finale
    if debug:
        print("\n--- État Final Atteint ---")
        afficher_configuration(config)
        
    return config, True


def teste(fichier, mot):
    machine1 = charger_machine(fichier)
    if machine1:
        resultat, success = simuler(machine1, mot)
        if success:
            print("\nCalcul terminé avec succès.")
        else:
            print("\nCalcul terminé avec échec.")

if __name__ == "__main__":
    # teste("comparaison.mt", "01#11")
    # teste("mult_unaire.mt", "11#111")
    teste("recherche_list.mt", "10#00#10#11")
