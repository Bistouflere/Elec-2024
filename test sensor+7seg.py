import network
import usocket as socket
from machine import Pin

# Configure the Wi-Fi connection
SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

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

# Define LED pins
led_red = Pin(14, Pin.OUT)
led_green = Pin(13, Pin.OUT)
led_blue = Pin(12, Pin.OUT)

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
            elif color == "green":
                led_red.off()
                led_green.on()
                led_blue.off()
            elif color == "blue":
                led_red.off()
                led_green.off()
                led_blue.on()
        
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

# Main loop to accept and handle incoming connections
while True:
    # Accept incoming connection
    client_socket, client_address = server_socket.accept()
    print("Client connected:", client_address)
    
    # Handle the HTTP request
    handle_request(client_socket)
