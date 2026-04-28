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

def simuler_machine_universelle(code_m, entree_x, debug=True):
    """
    Implémentation de la Question 9 :
    Simule une machine M (décrite par code_m) sur l'entrée entree_x.
    """
    # 1. Préparation des rubans
    # Ruban 1 : <M>#x
    ruban1 = list(f"{code_m}#{entree_x}")
    # Ruban 2 : contient x (ruban de travail de M)
    ruban2 = list(entree_x) if entree_x else ["_"]
    # Ruban 3 : état actuel de M (commence à '0')
    ruban3 = ["0"]

    # On crée une configuration à 3 rubans pour la MTU
    config_mtu = Configuration(
        etat_actuel="START_UNI",
        rubans=[ruban1, ruban2, ruban3],
        tetes=[0, 0, 0]
    )

    # Analyse du code <M> pour extraire les transitions
    # Format attendu : etat_in|lu|ecrit|dir|etat_out
    transitions_m = []
    parties = code_m.split('|')
    for i in range(0, len(parties), 5):
        if i + 4 < len(parties):
            transitions_m.append({
                'q_in': parties[i],
                'lu': parties[i+1],
                'ecrit': parties[i+2],
                'dir': parties[i+3],
                'q_out': parties[i+4]
            })

    # 2. Boucle de simulation
    while "".join(config_mtu.rubans[2]) != "1":  # Tant que l'état sur Ruban 3 n'est pas '1'
        etat_m = "".join(config_mtu.rubans[2])
        # On lit le symbole sur le ruban 2 (celui de M)
        pos_m = config_mtu.tetes[1]
        symbole_m = config_mtu.rubans[1][pos_m] if pos_m < len(config_mtu.rubans[1]) else "_"
        
        # Traduction du symbole vide pour le codage <M>
        symbole_cherche = "[]" if symbole_m == "_" else symbole_m

        # Recherche de la transition correspondante
        trans_trouvee = None
        for t in transitions_m:
            if t['q_in'] == etat_m and t['lu'] == symbole_cherche:
                trans_trouvee = t
                break
        
        if not trans_trouvee:
            print(f"MTU : Pas de transition pour l'état {etat_m} et symbole {symbole_m}")
            break

        # Application de la transition
        # Mise à jour du ruban 3 (état)
        config_mtu.rubans[2] = list(trans_trouvee['q_out'])
        
        # Mise à jour du ruban 2 (travail)
        symbole_a_ecrire = "_" if trans_trouvee['ecrit'] == "[]" else trans_trouvee['ecrit']
        config_mtu.rubans[1][pos_m] = symbole_a_ecrire
        
        # Déplacement tête ruban 2
        d = trans_trouvee['dir']
        if d == ">": config_mtu.tetes[1] += 1
        elif d == "<": config_mtu.tetes[1] = max(0, config_mtu.tetes[1] - 1)

        if debug:
            print(f"Simulation M : État {etat_m} -> {trans_trouvee['q_out']} | Ruban2: {''.join(config_mtu.rubans[1])}")

    return config_mtu.rubans[1] # Retourne le résultat final sur le ruban de simulation

def simuler_mtu_avec_compteur(code_m, entree_x, n, debug=True):
    """
    Question 10 : Machine Universelle avec gestion d'un compteur d'étapes.
    L'entrée est <M>#x#n. On simule M sur x pendant n étapes maximum.
    """
    # 1. Initialisation des 4 rubans
    ruban1 = list(f"{code_m}#{entree_x}#{n}") # Code + entrée + n
    ruban2 = list(entree_x) if entree_x else ["_"] # Travail de M
    ruban3 = ["0"] # État actuel de M
    ruban4 = ["1"] * n # Compteur : n bâtons (unaire) pour n étapes 

    config_mtu = Configuration(
        etat_actuel="START_COUNT",
        rubans=[ruban1, ruban2, ruban3, ruban4],
        tetes=[0, 0, 0, 0]
    )

    # Parsing des transitions (identique à Q9)
    transitions_m = []
    parties = code_m.split('|')
    for i in range(0, len(parties), 5):
        if i + 4 < len(parties):
            transitions_m.append({
                'q_in': parties[i], 'lu': parties[i+1],
                'ecrit': parties[i+2], 'dir': parties[i+3], 'q_out': parties[i+4]
            })

    # 2. Boucle de simulation avec vérification du compteur
    etapes_faites = 0
    
    # On s'arrête si : état final '1' OU compteur vide (ruban 4 fini)
    while "".join(config_mtu.rubans[2]) != "1" and etapes_faites < n:
        etat_m = "".join(config_mtu.rubans[2])
        pos_m = config_mtu.tetes[1]
        
        # Lecture sur ruban de travail
        symbole_m = config_mtu.rubans[1][pos_m] if pos_m < len(config_mtu.rubans[1]) else "_"
        symbole_cherche = "[]" if symbole_m == "_" else symbole_m

        # Recherche transition
        trans = next((t for t in transitions_m if t['q_in'] == etat_m and t['lu'] == symbole_cherche), None)
        
        if not trans:
            print(f"Arrêt : Pas de transition trouvée.")
            break

        # --- EXÉCUTION DU PAS ---
        # Mise à jour État (Ruban 3)
        config_mtu.rubans[2] = list(trans['q_out'])
        
        # Mise à jour Travail (Ruban 2)
        config_mtu.rubans[1][pos_m] = "_" if trans['ecrit'] == "[]" else trans['ecrit']
        
        # Déplacement tête Ruban 2
        if trans['dir'] == ">": config_mtu.tetes[1] += 1
        elif trans['dir'] == "<": config_mtu.tetes[1] = max(0, config_mtu.tetes[1] - 1)

        # --- GESTION DU COMPTEUR (Ruban 4) ---
        # On "consomme" une étape sur le ruban 4 
        if config_mtu.tetes[3] < len(config_mtu.rubans[3]):
            config_mtu.rubans[3][config_mtu.tetes[3]] = "." # On marque l'étape comme faite
            config_mtu.tetes[3] += 1
        
        etapes_faites += 1

        if debug:
            print(f"Étape {etapes_faites}/{n} | État M: {etat_m} | Symbole: {symbole_m}")

    # Conclusion de la simulation
    if etapes_faites >= n and "".join(config_mtu.rubans[2]) != "1":
        print(f"\nSTOP : Limite de {n} étapes atteinte. M ne s'est pas arrêtée.")
    elif "".join(config_mtu.rubans[2]) == "1":
        print(f"\nSUCCÈS : M s'est arrêtée en {etapes_faites} étapes.")

    return config_mtu.rubans[1]

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
    # 1. On choisit une machine à simuler (ex: comparaison.mt)
    fichier_machine = "comparaison.mt"
    mot_test = "10#11"  # Exemple d'entrée x pour la machine M
    
    print(f"=== TEST QUESTION 9 : MACHINE UNIVERSELLE ===")
    
    # 2. On génère le codage <M> via ta fonction de la Question 7 [cite: 36]
    code_m = question_7_encodage(fichier_machine)
    
    if code_m:
        print(f"Codage <M> récupéré : {code_m}")
        print(f"Entrée x : {mot_test}")
        print("-" * 30)
        
        # 3. Appel de la fonction de la Question 9 
        # Elle va simuler M sur x en utilisant les 3 rubans
        resultat_ruban = simuler_machine_universelle(code_m, mot_test, debug=True)
        
        # 4. Affichage du résultat final laissé sur le ruban de simulation
        print("-" * 30)
        print(f"Résultat final sur le ruban de simulation : {''.join(resultat_ruban)}")
    else:
        print("Erreur : Impossible de générer le codage de la machine.")

    # Paramètres de test
    fichier = "comparaison.mt"
    mot = "110#111"
    nb_etapes_max = 50 # Le 'n' de la question 10 
    
    code_m = question_7_encodage(fichier)
    
    if code_m:
        print(f"=== TEST QUESTION 10 (Limite: {nb_etapes_max} étapes) ===")
        resultat = simuler_mtu_avec_compteur(code_m, mot, nb_etapes_max)
        print(f"Ruban final : {''.join(resultat)}")