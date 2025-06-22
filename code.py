"""
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
Version: 1.09 (Modified for FOSS release - with password)
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

# Create WiFi hotspot with a password
# For community release, this password should be clearly documented and/or changeable.
# For security in deployment, use a strong, unique password.
wifi.radio.start_ap(ssid="Picowide", password="simpletest")
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

# Console monitoring
monitor_enabled = False
console_buffer = []

def console_print(message):
    """
    Add a message to the console buffer for web monitoring.
    
    :param str message: Message to add to console output
    :return: None
    :rtype: None
    """
    global console_buffer
    if monitor_enabled:
        console_buffer.append(message)
        # Keep buffer size manageable
        if len(console_buffer) > 100:
            console_buffer = console_buffer[-50:]

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
        
        # Add console output for monitoring
        status = "LED ON" if led_state else "LED OFF"
        console_print(status)

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
    the web interface. Returns the next action text for the button.
    
    :param Request request: The HTTP request object
    :return: Next button action text ("Blinky On" or "Blinky Off")
    :rtype: Response
    """
    global blinky_enabled
    try:
        blinky_enabled = not blinky_enabled
        next_action = "Blinky Off" if blinky_enabled else "Blinky On"
        return Response(request, next_action, content_type="text/plain")
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

@server.route("/run-monitor", methods=["POST"])
def run_monitor(request: Request):
    """
    Handle console monitor functionality toggle.
    
    This route toggles the console monitoring on/off when called from
    the web interface.
    
    :param Request request: The HTTP request object
    :return: Next button action text ("Monitor On" or "Monitor Off")
    :rtype: Response
    """
    global monitor_enabled
    try:
        monitor_enabled = not monitor_enabled
        next_action = "Monitor Off" if monitor_enabled else "Monitor On"
        if monitor_enabled:
            console_print("Console monitoring started")
        else:
            global console_buffer
            console_buffer = []  # Clear buffer when stopping
        return Response(request, next_action, content_type="text/plain")
    except Exception as e:
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

@server.route("/get-console", methods=["POST"])
def get_console(request: Request):
    """
    Get new console output for monitoring.
    
    This route returns any new console messages and clears the buffer.
    
    :param Request request: The HTTP request object
    :return: Console output messages
    :rtype: Response
    """
    global console_buffer
    try:
        if console_buffer:
            output = '\n'.join(console_buffer)
            console_buffer = []  # Clear after sending
            return Response(request, output, content_type="text/plain")
        else:
            return Response(request, "", content_type="text/plain")
    except Exception as e:
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

@server.route("/create-file", methods=["POST"])
def create_file(request: Request):
    """
    Handle file creation requests.
    
    This route creates a new empty file with the specified name on the
    filesystem. It checks for existing files to prevent overwriting.
    
    :param Request request: The HTTP request object containing form data
    :return: Success confirmation or error message
    :rtype: Response
    
    Form Data Expected:
        - filename: Name of the new file to create
    """
    try:
        filename = request.form_data.get('filename', '')
        
        if not filename:
            return Response(request, "No filename specified", content_type="text/plain")
        
        # Check if file already exists
        try:
            with open(filename, 'r'):
                return Response(request, f"Error: File '{filename}' already exists", content_type="text/plain")
        except OSError:
            # File doesn't exist, create it
            try:
                with open(filename, 'w') as f:
                    f.write('')  # Create empty file
                return Response(request, f"File '{filename}' created successfully!", content_type="text/plain")
            except OSError as e:
                return Response(request, f"Error: Could not create file '{filename}' - {str(e)}", content_type="text/plain")
                
    except Exception as e:
        print(f"Error in create_file: {e}")
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

@server.route("/save-file", methods=["POST"])
def save_file(request: Request):
    """
    Handle file saving requests from the editor.
    
    :param Request request: The HTTP request object containing form data
    :return: Success confirmation or error message
    :rtype: Response
    """
    try:
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

@server.route("/delete-file", methods=["POST"])
def delete_file(request: Request):
    """
    Handle file deletion requests.
    
    :param Request request: The HTTP request object containing form data
    :return: Success confirmation or error message
    :rtype: Response
    """
    try:
        filename = request.form_data.get('filename', '')
        
        if not filename:
            return Response(request, "No filename specified", content_type="text/plain")
        
        try:
            os.remove(filename)
            return Response(request, f"File '{filename}' deleted successfully!", content_type="text/plain")
        except OSError as e:
            return Response(request, f"Error: Could not delete file '{filename}' - {str(e)}", content_type="text/plain")
            
    except Exception as e:
        print(f"Error in delete_file: {e}")
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
