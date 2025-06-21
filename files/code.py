""" a
Picowide - Raspberry Pi Pico 2 W Web-based Development Environment

This module creates a WiFi hotspot and serves a web-based file editor interface
for developing directly on the Pico 2 W. It provides a complete IDE accessible
from any device connected to the Pico's WiFi network.

Core Features:
    - WiFi Access Point creation
    - Web-based file manager with CRUD operations
    - Real-time file editing through browser interface
    - Mobile-friendly responsive design

Technical Implementation:
    - Backend: CircuitPython with adafruit_httpserver
    - Frontend: Vanilla HTML/CSS/JavaScript
    - Access: Connect to "Picowide" WiFi → Navigate to 192.168.4.1

Author: Picowide Project
Version: 1.09
License: MIT
"""

import wifi
import socketpool
import ipaddress
import os
import board
import digitalio
import time
from adafruit_httpserver import Server, Request, Response

# =============================================================================
# CORE SYSTEM SETUP
# =============================================================================

# Create WiFi hotspot
wifi.radio.start_ap(ssid="Picowide")
wifi.radio.set_ipv4_address_ap(
    ipv4=ipaddress.IPv4Address("192.168.4.1"),
    netmask=ipaddress.IPv4Address("255.255.255.0"), 
    gateway=ipaddress.IPv4Address("192.168.4.1")
)

# Initialize server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/", debug=False)

# =============================================================================
# BLINKY FUNCTIONALITY SECTION
# =============================================================================
# This section can be removed when creating stripped-down versions for
# other projects. All LED blinky functionality is contained here.

# Configurable blink interval (seconds)
BLINK_INTERVAL = 0.25

# Setup LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Blink timing
last_blink = time.monotonic()
led_state = False
blinky_enabled = False

def update_blinky():
    """
    Update the LED blinky state based on timing interval.
    
    This function manages the onboard LED blinking pattern by checking
    if enough time has elapsed since the last blink and toggling the
    LED state accordingly. Only blinks when blinky_enabled is True.
    Called from the main loop.
    
    Global Variables:
        last_blink (float): Timestamp of last LED state change
        led_state (bool): Current LED state (True=on, False=off)
        blinky_enabled (bool): Whether blinking is currently active
        BLINK_INTERVAL (float): Time between blinks in seconds
    
    :return: None
    :rtype: None
    """
    global last_blink, led_state
    
    if not blinky_enabled:
        led.value = False  # Ensure LED is off when blinky is disabled
        return
        
    current_time = time.monotonic()
    
    if current_time - last_blink >= BLINK_INTERVAL:
        led_state = not led_state
        led.value = led_state
        last_blink = current_time

# =============================================================================
# BASE ROUTES (Core functionality - always needed)
# =============================================================================

@server.route("/")
def serve_index(request: Request):
    """
    Serve the main HTML interface.
    
    :param Request request: The HTTP request object
    :return: HTML response containing the web interface
    :rtype: Response
    """
    with open("index.html", "r") as f:
        return Response(request, f.read(), content_type="text/html")

@server.route("/styles.css")
def serve_styles(request: Request):
    """
    Serve the CSS stylesheet.
    
    :param Request request: The HTTP request object
    :return: CSS response containing styling information
    :rtype: Response
    """
    with open("styles.css", "r") as f:
        return Response(request, f.read(), content_type="text/css")

@server.route("/test", methods=["POST"])
def test_button(request: Request):
    """
    Handle test button functionality to verify connection.
    
    :param Request request: The HTTP request object
    :return: Plain text response confirming functionality
    :rtype: Response
    """
    return Response(request, "Button works!", content_type="text/plain")

@server.route("/run-blinky", methods=["POST"])
def run_blinky(request: Request):
    """
    Handle LED blinky functionality toggle.
    
    This route toggles the LED blinking pattern on/off when called from
    the web interface. The actual blinking is handled by update_blinky()
    in the main loop.
    
    :param Request request: The HTTP request object
    :return: Status message indicating current blinky state
    :rtype: Response
    """
    global blinky_enabled
    try:
        blinky_enabled = not blinky_enabled
        status = "ON" if blinky_enabled else "OFF"
        return Response(request, f"Blinky {status}", content_type="text/plain")
    except Exception as e:
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

# =============================================================================
# FILE MANAGEMENT SECTION
# =============================================================================
# This section can be removed when creating stripped-down versions for
# other projects. All file management functionality is contained here.

def list_all_files():
    """
    List all files in the CIRCUITPY root directory.
    
    This function scans the root filesystem and returns a list of all
    files and directories present. It handles OSError exceptions that
    may occur during filesystem access.
    
    :return: List of filenames found in root directory
    :rtype: list[str]
    
    Example:
        >>> files = list_all_files()
        >>> print(files)
        ['code.py', 'index.html', 'styles.css', 'secrets.py']
    """
    files = []
    try:
        for file in os.listdir("/"):
            files.append(file)
    except OSError:
        pass
    return files

def get_file_info(filename):
    """
    Get detailed information about a specific file.
    
    :param str filename: Name of the file to inspect
    :return: Dictionary containing file information or None if file doesn't exist
    :rtype: dict or None
    
    Example:
        >>> info = get_file_info("code.py")
        >>> print(info)
        {'name': 'code.py', 'size': 1234, 'type': 'file'}
    """
    try:
        stat = os.stat(filename)
        return {
            "name": filename,
            "size": stat[6],  # st_size
            "type": "directory" if stat[0] & 0x4000 else "file"
        }
    except OSError:
        return None

@server.route("/list-files", methods=["POST"])
def list_files(request: Request):
    """
    Handle file listing requests from the web interface.
    
    This route processes POST requests to list all files in the root
    directory. It formats the response as a plain text list suitable
    for parsing by the JavaScript frontend.
    
    :param Request request: The HTTP request object
    :return: Plain text response with file listing
    :rtype: Response
    
    Response Format:
        Files found:
        
        filename1.py
        filename2.html
        filename3.css
    """
    print("Handling list files request")
    all_files = list_all_files()
    
    if all_files:
        # Format files as a single column, one per line
        file_list = "\n".join(all_files)
        response_body = f"Files found:\n\n{file_list}"
    else:
        response_body = "No files found in CIRCUITPY root directory."
    
    return Response(request, response_body, content_type="text/plain")

@server.route("/select-file", methods=["POST"])
def select_file(request: Request):
    """
    Handle file selection requests.
    
    This route processes file selection from the web interface file list.
    It receives the filename via form data and prepares it for opening.
    
    :param Request request: The HTTP request object containing form data
    :return: Confirmation message with selected filename
    :rtype: Response
    
    Form Data Expected:
        - filename: Name of the selected file
    """
    try:
        # Get the filename from form data
        filename = request.form_data.get('filename', '')
        if filename:
            return Response(request, f"Open '{filename}'?", content_type="text/plain")
        else:
            return Response(request, "No file selected", content_type="text/plain")
    except Exception as e:
        print(f"Error in select_file: {e}")
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

@server.route("/open-file", methods=["POST"])
def open_file(request: Request):
    """
    Handle file opening requests for editing.
    
    This route reads the contents of a specified file and returns it
    for display in the web-based editor. It handles file reading errors
    gracefully and provides appropriate error messages.
    
    :param Request request: The HTTP request object containing form data
    :return: File contents formatted for editor or error message
    :rtype: Response
    
    Form Data Expected:
        - filename: Name of the file to open
        
    Response Format:
        File: filename.py
        
        [file contents here]
    """
    try:
        # Get the filename from form data
        filename = request.form_data.get('filename', '')
        if filename:
            # Read the file content
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                return Response(request, f"File: {filename}\n\n{content}", content_type="text/plain")
            except OSError:
                return Response(request, f"Error: Could not read file '{filename}'", content_type="text/plain")
        else:
            return Response(request, "No file specified", content_type="text/plain")
    except Exception as e:
        print(f"Error in open_file: {e}")
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

@server.route("/save-file", methods=["POST"])
def save_file(request: Request):
    """
    Handle file saving requests from the editor.
    
    This route receives file content from the web editor and writes it
    to the specified file on the filesystem. It provides comprehensive
    error handling for filesystem operations.
    
    :param Request request: The HTTP request object containing form data
    :return: Success confirmation or error message
    :rtype: Response
    
    Form Data Expected:
        - filename: Name of the file to save
        - content: Content to write to the file
        
    Note:
        Files saved via this interface may require a Pico restart to
        appear in the CIRCUITPY USB view due to filesystem sync timing.
    """
    try:
        # Get the filename and content from form data
        filename = request.form_data.get('filename', '')
        content = request.form_data.get('content', '')
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                return Response(request, f"File '{filename}' saved successfully!", content_type="text/plain")
            except OSError as e:
                return Response(request, f"Error: Could not save file '{filename}' - {str(e)}", content_type="text/plain")
        else:
            return Response(request, "No filename specified for saving", content_type="text/plain")
    except Exception as e:
        print(f"Error in save_file: {e}")
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

# =============================================================================
# SERVER STARTUP AND MAIN LOOP
# =============================================================================

# Start the server
server.start("192.168.4.1", port=80)
print("Picowide ready at http://192.168.4.1")

# Main server loop
while True:
    """
    Main server polling loop.
    
    This loop continuously polls the server for incoming requests and
    handles them appropriately. It also updates the LED blinky state
    on each iteration. Runs indefinitely until the device is reset
    or powered off.
    
    Note:
        This is a blocking loop that will consume the main thread.
        Any additional background tasks should be integrated here
        or handled via interrupts.
    """
    server.poll()
    
    # Update blinky LED state
    update_blinky()
