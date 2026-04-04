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
        lignes = [l.split('//')[0].strip() for l in f if l.split('//')[0].strip()]
    
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

def question_7_encodage(nom_fichier):
    machine = charger_machine(nom_fichier) #On charge la machine
    if not machine:
        return None

    if machine.nb_rubans > 1:   # Machine à un seul ruban seulement
        print(f"Le codage <M> est fait pour 1 ruban (Fichier: {nom_fichier})")

    # Mapping des états (Initial=0, Final=1 et les autres en binaire)
    mapping_etats = {machine.etat_initial: "0", machine.etat_final: "1"}
    autres_etats = sorted(list(machine.etats - {machine.etat_initial, machine.etat_final}))
    for i, etat in enumerate(autres_etats):
        # On génère une représentation binaire (ex: 00, 01, 10...)
        mapping_etats[etat] = bin(i)[2:].zfill(2)

    # On transforme les deplacements de bases avec le nouveau vocabulaire 
    mapping_dirs = {'r': '>', 'l': '<', 's': '-', '>': '>', '<': '<', '-': '-'}
    symbole_blanc = "[]" # ducoup ca c'est le carré du nouv vocabulaire

    # Format d'une transition selon l'exemple : etat_in | lu | ecrit | dir | etat_out
    elements_du_codage = []
    
    for (etat_in, syms_lus), (etat_out, syms_ecrits, dirs) in sorted(machine.transitions.items()):
        # On prend le premier élément de chaque tuple (car k=1)
        lu = syms_lus[0] if syms_lus[0] != '_' else symbole_blanc
        ecrit = syms_ecrits[0] if syms_ecrits[0] != '_' else symbole_blanc
        direction = mapping_dirs[dirs[0].lower()]
        
        # On ajoute tout les éléments qu'on a créer à la liste 
        elements_du_codage.extend([mapping_etats[etat_in],lu,ecrit,direction,mapping_etats[etat_out]])
   
    codage_final = "|".join(elements_du_codage)  # On rejoint tout avec le séparateur '|'
    
    return codage_final


def question_8_binaire(codage_q7):
    """Transforme le codage <M> en binaire pur et donne sa valeur entière (Question 8)"""
    # Dictionnaire pour transformer les symboles en bits  (4 bits par symbole)
    table = {
        '0': '0000', '1': '0001', '|': '0010', '[': '0011',
        ']': '0100', '<': '0101', '>': '0110', '-': '0111', '#': '1000'
    }
    
    #Conversion caractère par caractère en binaire 
    codage_bin = ""
    for char in codage_q7:
        if char in table:
            codage_bin += table[char]

    # On transforme la chaine binaire en valeure entiere 
    valeur_entiere = int(codage_bin, 2) if codage_bin else 0
    return codage_bin, valeur_entiere

def teste(fichier, mot):
    machine1 = charger_machine(fichier)
    if machine1:
        resultat, success = simuler(machine1, mot)
        if success:
            print("\nCalcul terminé avec succès.")
        else:
            print("\nCalcul terminé avec échec.")

if __name__ == "__main__":
    # Liste des machines à tester pour la Question 8
    fichiers_tests = ["exemple.mt", "comparaison.mt"] 
    
    print("=== RÉSOULTATS QUESTION 8 ===")
    
    for fichier in fichiers_tests:
        print(f"\n--- Machine : {fichier} ---")
        
        # Récupération du codage Q7
        code_q7 = question_7_encodage(fichier)
        if code_q7:
            print(f"Codage <M> : {code_q7}")
            
            # Conversion Q8
            code_bin, valeur = question_8_binaire(code_q7)
            
            print(f"Codage Binaire : {code_bin[:80]}...") # On coupe car c'est long
            print(f"Valeur entière : {valeur}")
        else:
            print("Erreur lors du chargement ou du codage.")