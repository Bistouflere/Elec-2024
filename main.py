from machine import Pin
import time

# Configuration des pins pour les sorties vers le décodeur 74LS47
data_pins = [Pin(17, Pin.OUT),Pin(18, Pin.OUT),Pin(19, Pin.OUT),Pin(16, Pin.OUT)]

# Définition du sensor
pir = Pin(0, Pin.IN)

# Définition de la led
led = Pin(15, Pin.OUT)

# Configuration des pins pour la sélection des afficheurs 7 segments
segment_pins = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT)]


# Tableau des valeurs binaires correspondant aux chiffres 0-9
digit_to_binary = [
    [0, 0, 0, 0],  # 0
    [0, 0, 0, 1],  # 1
    [0, 0, 1, 0],  # 2
    [0, 0, 1, 1],  # 3
    [0, 1, 0, 0],  # 4
    [0, 1, 0, 1],  # 5
    [0, 1, 1, 0],  # 6
    [0, 1, 1, 1],  # 7
    [1, 0, 0, 0],  # 8
    [1, 0, 0, 1]   # 9
]

def connecterWifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connexion au WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Connecté au réseau WiFi:', wlan.ifconfig())


def run_server():
    connecter_wifi("AndroidAPDA52", "qoyl0884")

def display_digit(digit):
    """Affiche un chiffre sur le décodeur 74LS47."""
    binary_value = digit_to_binary[digit]
    for pin, value in zip(data_pins, binary_value):
        pin.value(value)

def select_segment(segment_index):
    """Active un afficheur 7 segments en fonction de l'index donné."""
    for i, pin in enumerate(segment_pins):
        if i == segment_index:
            pin.value(1)
        else:
            pin.value(0)

def display_time(minutes, seconds):
    """Affiche le temps restant en minutes et secondes."""
   
    min_units = minutes % 10
    sec_tens = seconds // 10
    sec_units = seconds % 10
    
    digits = [ min_units, sec_tens, sec_units]
    for i in range(3):  # Nous avons 3 afficheurs 7 segments
        select_segment(i)
        display_digit(digits[i])
        time.sleep(0.001)  # Temps pour stabiliser l'affichage
        select_segment(-1)  # Désactive tous les afficheurs avant de passer au suivant

def countdown(minutes):
    """Démarre le décompteur pour les minutes spécifiées."""
    total_seconds = minutes * 60
    while total_seconds >= 0:
        mins = total_seconds // 60
        secs = total_seconds % 60
        for _ in range(200):  # Afficher les segments pendant 1 seconde (200 * 5ms)
            display_time(mins, secs)
        total_seconds -= 1

# Boucle principale pour afficher des chiffres de 0 à 9 en boucle
while True:
    motion_detected = pir.value()
    led.value(0)
    # Si un mouvement est détecté, imprimer un message
    if motion_detected:
        led.toggle()
        countdown(3)
        led.value(0)
        time.sleep(1)
    
