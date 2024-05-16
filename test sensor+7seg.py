from machine import Pin
import time
import network
import socket

# Définition des broches pour le décodeur BCD
A = Pin(17, Pin.OUT)
B = Pin(18, Pin.OUT)
C = Pin(19, Pin.OUT)
D = Pin(16, Pin.OUT)

# Définition du sensor
pir = Pin(0, Pin.IN)

# Définition de la led
led = Pin(15, Pin.OUT)
led_red = Pin(13, Pin.OUT)
led_green = Pin(14, Pin.OUT)
led_blue = Pin(15, Pin.OUT)

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


import network
import socket
from machine import Pin

# Configuration des broches pour les LEDs RGB
led_red = Pin(14, Pin.OUT)
led_green = Pin(13, Pin.OUT)
led_blue = Pin(12, Pin.OUT)

# Fonction pour configurer et démarrer le serveur web
def start_web_server():
    # Création d'un socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Lier le socket à l'adresse et au port souhaités
    server_address = ('', 80)  # Laisser l'adresse vide pour accepter les connexions entrantes sur toutes les interfaces
    server_socket.bind(server_address)

    # Ecouter les connexions entrantes
    server_socket.listen(1)
    print("Serveur web démarré. En attente de connexions...")

    while True:
        # Attendre une connexion entrante
        client_connection, client_address = server_socket.accept()
        print("Connexion depuis:", client_address)

        # Recevoir les données de la requête HTTP
        request_data = client_connection.recv(1024).decode()

        # Extraire la méthode HTTP et l'URI de la requête
        request_method = request_data.split(' ')[0]
        request_uri = request_data.split(' ')[1]

        # Traiter la requête
        if request_method == 'GET':
            if request_uri == '/red':
                led_red.on()
                led_green.off()
                led_blue.off()
            elif request_uri == '/green':
                led_red.off()
                led_green.on()
                led_blue.off()
            elif request_uri == '/blue':
                led_red.off()
                led_green.off()
                led_blue.on()

            # Envoyer une réponse HTTP
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nAction effectuée."
            client_connection.send(response.encode())
        else:
            # Envoyer une réponse HTTP pour les méthodes autres que GET
            response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\n\r\nMéthode non autorisée."
            client_connection.send(response.encode())

        # Fermer la connexion client
        client_connection.close()

# Connexion au WiFi
def connecterWifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connexion au WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Connecté au réseau WiFi:', wlan.ifconfig())

# Démarrer le serveur web et connecter au WiFi
connecterWifi("votre_ssid", "votre_mot_de_passe")
start_web_server()

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