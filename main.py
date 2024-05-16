from machine import Pin
import time
import network
import usocket as socket

# Configuration des pins pour les sorties vers le décodeur 74LS47
data_pins = [Pin(17, Pin.OUT),Pin(18, Pin.OUT),Pin(19, Pin.OUT),Pin(16, Pin.OUT)]

# Définition du sensor
pir = Pin(0, Pin.IN)

# Définition de la led
led_red = Pin(13, Pin.OUT)
led_green = Pin(15, Pin.OUT)
led_blue = Pin(14, Pin.OUT)
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

# Configure the Wi-Fi connection
SSID = "AndroidAPDA52"
PASSWORD = "qoyl0884"

# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

# Wait until connected
while not wifi.isconnected():
    pass

# Print the IP address once connected
print("Connected to Wi-Fi")
print("IP address:", wifi.ifconfig()[0])

# Define HTML content for the web page
html = """<!DOCTYPE html>
<html>
<head><title>Raspberry Pi Pico W Web Server</title></head>
<body>
<h1>Control LED RGB</h1>
<button onclick="changeColor('red')">Red</button>
<button onclick="changeColor('green')">Green</button>
<button onclick="changeColor('blue')">Blue</button>
<script>
function changeColor(color) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/color?value=" + color, true);
    xhr.send();
}
</script>
</body>
</html>
"""

# Define function to handle HTTP requests
def handle_request(client_socket):
    try:
        request_data = client_socket.recv(1024)
        # Print the received HTTP request (optional)
        print("Request:")
        print(request_data.decode("utf-8"))
        
        # Parse the HTTP request to extract the requested URL
        request = request_data.decode("utf-8")
        url = request.split(' ')[1]
        
        # Check if the request is for the color control
        if url.startswith("/color?value="):
            color = url.split('=')[1]
            # Turn on/off LED based on the color requested
            if color == "red":
                led_red.on()
                led_green.off()
                led_blue.off()
                led = Pin(13, Pin.OUT)
            elif color == "green":
                led_red.off()
                led_green.on()
                led_blue.off()
                led = Pin(15, Pin.OUT)
            elif color == "blue":
                led_red.off()
                led_green.off()
                led_blue.on()
                led = Pin(14, Pin.OUT)
        
        # Send HTTP response
        response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\nConnection: close\r\n\r\n".format(len(html))
        client_socket.send(response_headers.encode("utf-8"))
        client_socket.send(html.encode("utf-8"))
    except Exception as e:
        print("Error handling request:", e)
    finally:
        client_socket.close()

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific IP address and port
server_socket.bind(('0.0.0.0', 80))

# Set the socket to listen for incoming connections
server_socket.listen(5)


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
    client_socket, client_address = server_socket.accept()
    print("Client connected:", client_address)
    
    # Handle the HTTP request
    handle_request(client_socket)
    motion_detected = pir.value()
    led.value(0)
    # Si un mouvement est détecté, imprimer un message
    if motion_detected:
        led.toggle()
        countdown(1)
        led.value(0)
        time.sleep(1)
    
