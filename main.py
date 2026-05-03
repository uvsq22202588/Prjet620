import sys

class MT:
    def __init__(self, nb_rubans):
        self.nb_rubans = nb_rubans
        self.etats = set()
        self.etat_initial = "I"
        self.etat_final = "F"
        # dico des transitions format : (etat, lus) -> (nouvel_etat, ecrits, directions)
        self.transitions = {}

class Configuration:
    def __init__(self, etat_actuel, rubans=None, tetes=None):
        self.etat_actuel = etat_actuel
        self.rubans = rubans if rubans else []
        self.tetes = tetes if tetes else [0] * len(self.rubans)

def charger_machine(nom_fichier):
    try:
        with open(nom_fichier, 'r') as f:
            lignes = [l.split('//')[0].strip() for l in f if l.split('//')[0].strip()]
    except Exception:
        print(f"Impossible de lire le fichier {nom_fichier}")
        return None
    
    if not lignes:
        return None
    
    # On déduit k de la première ligne
    k = len(lignes[0].split('->')[0].split(',')) - 1
    mt = MT(k)
    
    for ligne in lignes:
        if '->' not in ligne:
            continue
            
        gauche, droite = ligne.split('->')
        el_g = [e.strip() for e in gauche.split(',')]
        el_d = [e.strip() for e in droite.split(',')]
        
        etat_in = el_g[0]
        lus = tuple(el_g[1:])
        
        etat_out = el_d[0]
        ecrits = tuple(el_d[1:1+k])
        dirs = tuple(el_d[1+k:])
        
        mt.transitions[(etat_in, lus)] = (etat_out, ecrits, dirs)
        mt.etats.add(etat_in)
        mt.etats.add(etat_out)
        
    return mt

def creer_config_initiale(machine, mot):
    rubans = [list(mot) if mot else ['_']]
    
    # On complète avec des rubans vides
    for _ in range(machine.nb_rubans - 1):
        rubans.append(['_'])
    
    tetes = [0] * machine.nb_rubans
    return Configuration("I", rubans, tetes)

def un_pas_de_calcul(machine, config):
    lus = []
    for i in range(machine.nb_rubans):
        pos = config.tetes[i]
        if 0 <= pos < len(config.rubans[i]):
            lus.append(config.rubans[i][pos])
        else:
            lus.append('_')
    
    cle = (config.etat_actuel, tuple(lus))
    
    if cle not in machine.transitions:
        return False # bloqué
    
    nouvel_etat, ecrits, dirs = machine.transitions[cle]
    config.etat_actuel = nouvel_etat
    
    for i in range(machine.nb_rubans):
        # Gestion du ruban infini à gauche
        if config.tetes[i] < 0:
            config.rubans[i].insert(0, '_')
            config.tetes[i] = 0
            
        # Gestion à droite
        while config.tetes[i] >= len(config.rubans[i]):
            config.rubans[i].append('_')
            
        config.rubans[i][config.tetes[i]] = ecrits[i]
        
        d = dirs[i].lower()
        if d in ['r', '>']: config.tetes[i] += 1
        elif d in ['l', '<']: config.tetes[i] -= 1
            
    return True

def afficher_config(config):
    print(f"\nÉtat : {config.etat_actuel}")
    for i, ruban in enumerate(config.rubans):
        contenu = "".join(ruban)
        curseur = " " * config.tetes[i] + "^"
        print(f"R{i} : {contenu}")
        print(f"     {curseur}")

def simuler(machine, mot, debug=True):
    config = creer_config_initiale(machine, mot)
    etapes = 0
    
    while config.etat_actuel != machine.etat_final:
        if debug: afficher_config(config)
        
        if not un_pas_de_calcul(machine, config):
            print("\n=> Arrêt : machine bloquée.")
            return config, False
        
        etapes += 1
        if etapes > 1000:
            print("\n=> Arrêt : boucle infinie probable.")
            return config, False

    if debug:
        print("\n--- FIN ---")
        afficher_config(config)
        
    return config, True

def q7_encodage(nom_fichier):
    mt = charger_machine(nom_fichier)
    if not mt: return None

    # Mapping états (0, 1, puis binaire)
    map_etats = {mt.etat_initial: "0", mt.etat_final: "1"}
    autres = sorted(list(mt.etats - {mt.etat_initial, mt.etat_final}))
    
    for i, e in enumerate(autres):
        map_etats[e] = bin(i)[2:].zfill(2)

    map_dirs = {'r': '>', 'l': '<', 's': '-', '>': '>', '<': '<', '-': '-'}
    
    elements = []
    for (etat_in, lus), (etat_out, ecrits, dirs) in sorted(mt.transitions.items()):
        lu = lus[0] if lus[0] != '_' else "[]"
        ecrit = ecrits[0] if ecrits[0] != '_' else "[]"
        direction = map_dirs[dirs[0].lower()]
        
        elements.extend([map_etats[etat_in], lu, ecrit, direction, map_etats[etat_out]])
   
    return "|".join(elements)

def q8_binaire(codage):
    table = {
        '0': '0000', '1': '0001', '|': '0010', '[': '0011',
        ']': '0100', '<': '0101', '>': '0110', '-': '0111', '#': '1000'
    }
    
    binaire = "".join(table[c] for c in codage if c in table)
    valeur = int(binaire, 2) if binaire else 0
    return binaire, valeur

def simuler_mtu(code_m, entree_x, debug=True):
    # Ruban 1 : <M>#x, Ruban 2 : x, Ruban 3 : état actuel
    r1 = list(f"{code_m}#{entree_x}")
    r2 = list(entree_x) if entree_x else ["_"]
    r3 = ["0"]

    config = Configuration("MTU", [r1, r2, r3], [0, 0, 0])

    # Parsing rapide du code de la machine simulée
    trans = {}
    parts = code_m.split('|')
    for i in range(0, len(parts), 5):
        if i + 4 < len(parts):
            trans[(parts[i], parts[i+1])] = (parts[i+2], parts[i+3], parts[i+4])

    etape = 0
    while True:
        etat_m = "".join([c for c in config.rubans[2] if c != "_"])
        pos2 = config.tetes[1]
        
        symb = config.rubans[1][pos2] if pos2 < len(config.rubans[1]) else "_"
        symb_cherche = "[]" if symb == "_" else symb

        if debug:
            print(f"MTU {etape} | État: {etat_m} | Lit: {symb} | R2: {''.join(config.rubans[1])}")

        if etat_m == "1":
            print("=> Succès: la machine a atteint l'état final.")
            break

        if (etat_m, symb_cherche) not in trans:
            print("=> Bloqué: aucune transition trouvée.")
            break

        ecrit, direction, etat_out = trans[(etat_m, symb_cherche)]

        config.rubans[2] = list(etat_out)
        
        symb_ecrit = "_" if ecrit == "[]" else ecrit
        while config.tetes[1] >= len(config.rubans[1]):
            config.rubans[1].append("_")
            
        config.rubans[1][config.tetes[1]] = symb_ecrit
        
        if direction == ">": config.tetes[1] += 1
        elif direction == "<": 
            config.tetes[1] -= 1
            if config.tetes[1] < 0:
                config.rubans[1].insert(0, '_')
                config.tetes[1] = 0

        etape += 1

    return config.rubans[1]

def simuler_mtu_compteur(code_m, entree_x, n, debug=True):
    n_unaire = "1" * n 
    
    r1 = list(f"{code_m}#{entree_x}#{n_unaire}")
    r2 = list(entree_x) if entree_x else ["_"]
    r3 = ["0"]
    r4 = list(n_unaire) if n > 0 else ["_"]

    config = Configuration("MTU_COUNT", [r1, r2, r3, r4], [0, 0, 0, 0])

    trans = {}
    parts = code_m.split('|')
    for i in range(0, len(parts), 5):
        if i + 4 < len(parts):
            trans[(parts[i], parts[i+1])] = (parts[i+2], parts[i+3], parts[i+4])

    etape = 0
    while True:
        etat_m = "".join([c for c in config.rubans[2] if c != "_"])
        pos2 = config.tetes[1]
        pos4 = config.tetes[3]
        
        symb = config.rubans[1][pos2] if pos2 < len(config.rubans[1]) else "_"
        symb_cherche = "[]" if symb == "_" else symb
        symb_cpt = config.rubans[3][pos4] if pos4 < len(config.rubans[3]) else "_"

        if debug:
            print(f"Étape {etape} | État: {etat_m} | Cpt: {symb_cpt} | R2: {''.join(config.rubans[1])}")

        if etat_m == "1":
            print(f"=> Succès: fini en {etape} étapes.")
            break
            
        if symb_cpt != "1":
            print(f"=> Arrêt: compteur vide ({n} étapes max).")
            break

        if (etat_m, symb_cherche) not in trans:
            print("=> Bloqué: pas de transition.")
            break

        ecrit, direction, etat_out = trans[(etat_m, symb_cherche)]

        config.rubans[2] = list(etat_out)
        
        symb_ecrit = "_" if ecrit == "[]" else ecrit
        while config.tetes[1] >= len(config.rubans[1]):
            config.rubans[1].append("_")
        config.rubans[1][config.tetes[1]] = symb_ecrit
        
        if direction == ">": config.tetes[1] += 1
        elif direction == "<": 
            config.tetes[1] -= 1
            if config.tetes[1] < 0:
                config.rubans[1].insert(0, '_')
                config.tetes[1] = 0

        # Maj du compteur
        config.rubans[3][pos4] = "." 
        config.tetes[3] += 1
        
        etape += 1

    return config.rubans[1]

def teste(fichier, mot):
    mt = charger_machine(fichier)
    if mt:
        simuler(mt, mot)

def executer_menu():
    print("\n--- MENU PROJET MT ---")
    print("1.  Q1-Q5 : Simulation (exemple.mt)")
    print("6a. Q6 : Comparaison (comparaison.mt)")
    print("6b. Q6 : Recherche (recherche_list.mt)")
    print("6c. Q6 : Mult unaire (mult_unaire.mt)")
    print("7-8. Q7/Q8 : Encodage et binaire")
    print("9.  Q9 : MTU (3 rubans)")
    print("10. Q10 : MTU avec Compteur (4 rubans)")
    print("q.  Quitter")

    while True:
        choix = input("\nChoix (ou 'q') : ").strip().lower()
        if choix in ['q', 'quit', 'exit']: break

        try:
            if choix == '1':
                teste("exemple.mt", "0011")
            elif choix == '6a':
                teste("comparaison.mt", "10#11")
            elif choix == '6b':
                teste("recherche_list.mt", "10#01#10#11")
            elif choix == '6c':
                teste("mult_unaire.mt", "11#111")
            elif choix in ['7', '8']:
                for f in ["exemple.mt", "comparaison.mt"]:
                    code = q7_encodage(f)
                    if code:
                        print(f"\nFichier : {f}")
                        print(f"Code : {code}")
                        bin_str, val = q8_binaire(code)
                        print(f"Binaire (début) : {bin_str[:50]}...")
                        print(f"Valeur : {val}")
            elif choix == '9':
                code = q7_encodage("comparaison.mt")
                res = simuler_mtu(code, "1010#1011")
                print(f"Résultat final : {''.join(res)}")
            elif choix == '10':
                code = q7_encodage("comparaison.mt")
                res = simuler_mtu_compteur(code, "110#111", 50)
                print(f"Ruban final : {''.join(res)}")
            else:
                # petite bidouille pour lancer du code depuis le terminal
                eval(choix)
        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        eval(sys.argv[1])
    else:
        executer_menu()