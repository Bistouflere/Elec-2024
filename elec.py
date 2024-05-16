from machine import Pin
import time

# Définition des broches pour les afficheurs à 7 segments
sept_seg_select = [
    Pin(22, Pin.OUT),  # Broche pour sélectionner le premier afficheur
    Pin(21, Pin.OUT),  # Broche pour sélectionner le deuxième afficheur
    Pin(20, Pin.OUT)   # Broche pour sélectionner le troisième afficheur
]

# Tableau de correspondance des chiffres en BCD pour les afficheurs à 7 segments
decodeur_mapping = [
    (0, 0, 0, 0),  # 0
    (0, 0, 0, 1),  # 1
    (0, 0, 1, 0),  # 2
    (0, 0, 1, 1),  # 3
    (0, 1, 0, 0),  # 4
    (0, 1, 0, 1),  # 5
    (0, 1, 1, 0),  # 6
    (0, 1, 1, 1),  # 7
    (1, 0, 0, 0),  # 8
    (1, 0, 0, 1)   # 9
]

def affichage(segments):
    # Afficher le chiffre spécifié sur les afficheurs à 7 segments
    for pin, state in zip(sept_seg_select, segments):
        pin.value(state)

def décompte():
    for minute in range(3, -1, -1):  
        for second in range(59, -1, -1):  
            for unity in range(10, -1, -1):
                for i in range(3):
                    # Sélectionner l'afficheur à activer
                    sept_seg_select[i].value(1)
                    
                    # Afficher le chiffre sur l'afficheur sélectionné
                    affichage(decodeur_mapping[minute // 10 if i == 0 else 
                                                minute % 10 if i == 1 else 
                                                second // 10 if i == 2 else 
                                                second % 10])
                    
                    # Désélectionner l'afficheur pour le prochain tour de boucle
                    sept_seg_select[i].value(0) 
                    
                    # Attendre un court instant pour l'animation
                    time.sleep(0.005) 
    
    # Fin du compte à rebours
    print("Décompte terminé !")

# Exécution de la fonction de décompte
décompte()
