from machine import Pin
import time

# Définition des broches pour le décodeur BCD
A = Pin(17, Pin.OUT)
B = Pin(18, Pin.OUT)
C = Pin(19, Pin.OUT)
D = Pin(16, Pin.OUT)

# Définition du sensor
pir = Pin(0, Pin.IN)

# Définition de la led
led = Pin(15, Pin.OUT)

# Définition des 7 segments
sept_seg = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT)]

# Tableau de correspondance pour les chiffres de 0 à 9 sur le décodeur BCD
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

# Fonction pour afficher un chiffre sur l'afficheur à sept segments
def afficher_chiffre(chiffre):
    # Vérifier si le chiffre est valide (0 à 9)
    if 0 <= chiffre <= 9:
        # Récupérer les valeurs du tableau de correspondance pour le chiffre donné
        a, b, c, d = decodeur_mapping[chiffre]
        # Appliquer ces valeurs aux broches du décodeur BCD
        A.value(a)
        B.value(b)
        C.value(c)
        D.value(d)
    else:
        print("Chiffre invalide")

# Boucle principale pour afficher des chiffres de 0 à 9 en boucle
while True:
    motion_detected = pir.value()
    led.value(0)
    # Si un mouvement est détecté, imprimer un message
    if motion_detected:
        led.toggle()
        for x in range(3):
            sept_seg[x].value(1)
            for chiffre in range(10):
                afficher_chiffre(chiffre)
                time.sleep(1)  # Délai d'une seconde entre chaque chiffre affiché
            sept_seg[x].value(0)
        led.value(0)
        time.sleep(1)
    
