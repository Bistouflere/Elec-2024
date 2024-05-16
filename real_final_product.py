import network
import usocket as socket
from machine import Pin, Timer
import time

SSID = "AndroidAPDA52"
PASSWORD = "qoyl0884"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass

print("Connected to Wi-Fi")
print("IP address:", wifi.ifconfig()[0])

html = """<!DOCTYPE html>
<html>
<head>
<title>Raspberry Pi Pico W Web Server</title>
<meta charset="utf-8">
<style>
body {
    font-family: Arial;
    background-color: #a1a3e3;
}
h2 {
    text-align: center;
}
.encadre, h2 {
    margin: 50px 20px;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
</style>
</head>
<body>
<h2>Gestion des lumières de la maison</h2>
<div class="encadre">
    <h3>Consommation de l'ampoule</h3>
    <p>L'ampoule a été allumée au total pendant <span id="light_time">0s</span> aujourd'hui</p>
    <p>L'ampoule a consommé au total <span id="energie_time">0</span>kW aujourd'hui</p>
    <label for="watts">Consommation de l'ampoule (watts/h):</label>
    <input type="number" id="watts" name="watts">
    <button onclick="consommation()">Appliquer</button><br><br>
    <label for="consommation_max">Définir la consommation maximum de l'ampoule (watts):</label>
    <input type="number" id="consommation_max" name="consommation_max">
    <button onclick="set_consommation_max()">Appliquer</button>
</div>
<div class="encadre">
    <h3>Changer la couleur de la LED</h3>
    <button onclick="changeColor('red')">Red</button>
    <button onclick="changeColor('green')">Green</button>
    <button onclick="changeColor('blue')">Blue</button>
</div>
<div class="encadre">
    <h3>Changer le nombre de minutes du timer</h3>
    <label for="countdown">Timer:</label>
    <input type="number" id="countdown" name="countdown" min="1" max="9">
    <button onclick="changeTimer()">Appliquer</button>
</div>
<script>
function changeColor(color) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/color?value=" + color, true);
    xhr.send();
}
function changeTimer() {
    var countdownValue = document.getElementById("countdown").valueAsNumber;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/timer?value=" + countdownValue, true);
    xhr.send();
}
function consommation() {
    var wattsValue = document.getElementById("watts").valueAsNumber;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/watts?value=" + wattsValue, true);
    xhr.send();
}
function set_consommation_max() {
    var maxValue = document.getElementById("consommation_max").valueAsNumber;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/max?value=" + maxValue, true);
    xhr.send();
}
function updateLightTime() {
    var xhrLightTime = new XMLHttpRequest();
    xhrLightTime.open("GET", "/light_time", true);
    xhrLightTime.onload = function() {
        if (xhrLightTime.status == 200) {
            let light_time = parseFloat(xhrLightTime.responseText);
            document.getElementById("light_time").innerText = light_time + "s";

            // Nouvelle requête pour obtenir la consommation en watts
            var xhrWatts = new XMLHttpRequest();
            xhrWatts.open("GET", "/watts", true);
            xhrWatts.onload = function() {
                if (xhrWatts.status == 200) {
                    console.log(xhrWatts.responseText)
                    let watts = parseFloat(xhrWatts.responseText);
                    let energy = (light_time / 3600) * watts;
                    document.getElementById("energie_time").innerText = energy.toFixed(2) + " kW";
                }
            };
            xhrWatts.send();
        }
    };
    xhrLightTime.send();
}
setInterval(updateLightTime, 1000);
</script>
</body>
</html>
"""

led_red = Pin(13, Pin.OUT)
led_green = Pin(15, Pin.OUT)
led_blue = Pin(14, Pin.OUT)

led_interrupt = Pin(12, Pin.OUT)

current_color = None
current_timer = 1
current_watts_value = 9
current_max_value = 9000
light_time = 0

def handle_request(client_socket):
    global current_color, current_timer, current_watts_value, current_max_value, light_time
    try:
        request_data = client_socket.recv(1024)
        request = request_data.decode("utf-8")
        url = request.split(' ')[1]
        
        if url.startswith("/color?value="):
            color = url.split('=')[1]
            current_color = color 
            if color == "red":
                led_red.on()
                led_green.off()
                led_blue.off()
            elif color == "green":
                led_red.off()
                led_green.on()
                led_blue.off()
            elif color == "blue":
                led_red.off()
                led_green.off()
                led_blue.on()
        if url.startswith("/timer?value="):
            timer = url.split('=')[1]
            timer_value = int(timer)
            current_timer = timer_value
            print(f"{current_timer}")
        if url.startswith("/watts?value="):
            watts = url.split('=')[1]
            watts_value = int(watts)
            current_watts_value = watts_value
            print(f"{current_watts_value}")
        if url.startswith("/max?value="):
            value = url.split('=')[1]
            max_value = int(value)
            current_max_value = max_value
            print(f"{current_max_value}")
        if url == "/light_time":
            client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
            client_socket.send(f"{light_time:.1f}")
            client_socket.close()
            return
        if url == "/watts":
            client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
            client_socket.send(f"{current_watts_value}")
            client_socket.close()
            return
        
        response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\nConnection: close\r\n\r\n".format(len(html))
        client_socket.send(response_headers.encode("utf-8"))
        client_socket.send(html.encode("utf-8"))
    except Exception as e:
        print("Error handling request:", e)
    finally:
        client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(5)

data_pins = [Pin(17, Pin.OUT), Pin(18, Pin.OUT), Pin(19, Pin.OUT), Pin(16, Pin.OUT)]
pir = Pin(0, Pin.IN)
segment_pins = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT)]

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
    
    digits = [min_units, sec_tens, sec_units]
    for i in range(3): 
        select_segment(i)
        display_digit(digits[i])
        time.sleep(0.001)  
        select_segment(-1)

def countdown(minutes):
    """Démarre le décompteur pour les minutes spécifiées."""
    total_seconds = minutes * 60
    while total_seconds >= 0:
        mins = total_seconds // 60
        secs = total_seconds % 60
        for _ in range(200): 
            display_time(mins, secs)
        total_seconds -= 1
        
def energie_consomme(time, watts):
    time_hours = time / 3600
    consommation = time_hours * watts
    return consommation

def pir_interrupt_handler(pin):
    """Gestionnaire d'interruption pour le capteur PIR."""
    global current_color, light_time, current_watts_value, current_max_value
    if pin.value() == 1:
        if energie_consomme(light_time, current_watts_value) < current_max_value:
            led_interrupt.off()
        if current_color == "red":
            led_red.on()
        elif current_color == "green":
            led_green.on()
        elif current_color == "blue":
            led_blue.on()
        elif current_color == None:
            led_green.on()
        start = time.time()
        countdown(current_timer)
        led_red.off()
        led_green.off()
        led_blue.off()
        end = time.time()
        time_on = (end-start)
        light_time += time_on
        if energie_consomme(light_time, current_watts_value) >= current_max_value:
            led_interrupt.on()
        energie_test = energie_consomme(light_time, current_watts_value)
        print(f"{light_time}")
        print(f"{energie_test}")
        print(f"{current_max_value}")
        

pir.irq(trigger=Pin.IRQ_RISING, handler=pir_interrupt_handler)

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print("Client connected:", client_address)
        handle_request(client_socket)
except KeyboardInterrupt:
    print("Server is shutting down")
finally:
    server_socket.close()
