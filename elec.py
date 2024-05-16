from machine import Pin
import time

# Définition des broches pour le décodeur BCD
A = Pin(17, Pin.OUT)
B = Pin(18, Pin.OUT)
C = Pin(19, Pin.OUT)
D = Pin(16, Pin.OUT)

# Définition des broches pour les afficheurs à 7 segments
sept_seg = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT)]

# Tableau de correspondance des chiffres en BCD pour les décodeurs
BCD_mapping = [
    [0, 0, 0, 0],   # 0
    [1, 0, 0, 0],   # 1
    [0, 1, 0, 0],   # 2
    [1, 1, 0, 0],   # 3
    [0, 0, 1, 0],   # 4
    [1, 0, 1, 0],   # 5
    [0, 1, 1, 0],   # 6
    [1, 1, 1, 0],   # 7
    [0, 0, 0, 1],   # 8
    [1, 0, 0, 1]    # 9
]

def display_number(number):
    # Afficher le chiffre sur les afficheurs à 7 segments
    for pin, state in zip(sept_seg, BCD_mapping[number]):
        pin.value(state)

def timer(seconds):
    while seconds >= 0:
        # Affichage des secondes restantes sur les afficheurs à 7 segments
        display_number(seconds % 10)  # Affiche les unités des secondes
        time.sleep(1)  # Attente d'une seconde
        seconds -= 1

# Exemple d'utilisation : minuterie de 180 secondes (3 minutes)
try:
    timer(180)  # Démarrer la minuterie pour 180 secondes (3 minutes)
finally:
    # Éteindre les afficheurs à la fin de la minuterie
    display_number(0)  # Affiche "0" sur les afficheurs
