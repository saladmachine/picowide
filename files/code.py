import wifi 
import socketpool
import ipaddress
from adafruit_httpserver import Server, Request, Response

# Create hotspot
wifi.radio.start_ap(ssid="Picowide")
wifi.radio.set_ipv4_address_ap(
    ipv4=ipaddress.IPv4Address("192.168.4.1"),
    netmask=ipaddress.IPv4Address("255.255.255.0"), 
    gateway=ipaddress.IPv4Address("192.168.4.1")
)

# Start server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/", debug=False)

# Module management
loaded_module = None

@server.route("/")
def serve_index(request: Request):
    with open("index.html", "r") as f:
        return Response(request, f.read(), content_type="text/html")

@server.route("/styles.css")
def serve_styles(request: Request):
    with open("styles.css", "r") as f:
        return Response(request, f.read(), content_type="text/css")

@server.route("/test", methods=["POST"])
def test_button(request: Request):
    return Response(request, "Button works!", content_type="text/plain")

@server.route("/run-blinky", methods=["POST"])
def run_blinky(request: Request):
    global loaded_module
    try:
        loaded_module = __import__("pico_blinky")
        return Response(request, "Blinky started!", content_type="text/plain")
    except Exception as e:
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

server.start("192.168.4.1", port=80)
print("Picowide ready at http://192.168.4.1")

while True:
    server.poll()
    
    # Update loaded module if present
    if loaded_module and hasattr(loaded_module, 'update_blinky'):
        loaded_module.update_blinky()