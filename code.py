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
import gc # Added for memory management

# --- NEW: Config Import ---
try:
    import config
except ImportError:
    print("config.py not found. Using default values for power saving.")
    class Config:
        WIFI_AP_TIMEOUT_MINUTES = 10  # Default timeout in minutes if config.py is missing
    config = Config()

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

# --- NEW/MODIFIED: WiFi Timeout Variables and Activity Tracker ---
last_activity_time = time.monotonic()
WIFI_TIMEOUT_SECONDS = config.WIFI_AP_TIMEOUT_MINUTES * 60
last_timeout_check_log_time = time.monotonic() # For periodic + logging
ap_is_off_and_logged = False # NEW: Flag to prevent repeated shutdown messages after AP is off
timeout_disabled = False # NEW: Flag to disable automatic timeout when user takes control

def shut_down_wifi_and_sleep(sleep_duration=None):
    """
    Shuts down the Wi-Fi Access Point and optionally puts the board to sleep.
    If sleep_duration is None, it means a permanent low-power state requiring
    a physical power cycle to restart the hotspot.
    """
    # This function now assumes the caller (check_wifi_timeout or power_save_mode)
    # has determined that a shutdown is needed and not already logged.
    console_print("Initiating Wi-Fi shutdown and power saving mode...")
    if wifi.radio.enabled: # Only call stop_ap if it's currently enabled
        wifi.radio.stop_ap()
        console_print("Wi-Fi AP shut down.")
    else:
        # This branch should ideally not be hit if ap_is_off_and_logged logic works,
        # but kept for robustness.
        console_print("Wi-Fi AP already off (or never started).")

    # MODIFIED: Remove sleep functionality to allow other Pico operations to continue
    if sleep_duration is not None:
        console_print(f"Light sleep disabled - Pico continues other operations.")
    else:
        console_print("Wi-Fi shutdown complete. Other Pico operations continue. Requires physical power cycle to restart hotspot.")


def check_wifi_timeout():
    """
    Checks if the Wi-Fi AP has timed out due to inactivity and shuts it down.
    Provides periodic console output only when AP is active.
    """
    global last_activity_time, last_timeout_check_log_time, ap_is_off_and_logged, timeout_disabled
    
    # NEW: Skip timeout logic entirely if user has disabled automatic timeout
    if timeout_disabled:
        return
    
    current_time = time.monotonic()

    # If Wi-Fi AP is currently enabled
    if wifi.radio.enabled:
        # Log periodic checks every few seconds
        if (current_time - last_timeout_check_log_time >= min(10, WIFI_TIMEOUT_SECONDS / 2 if WIFI_TIMEOUT_SECONDS > 20 else 1)):
            elapsed_time = round(current_time - last_activity_time, 1)
            remaining_time = round(WIFI_TIMEOUT_SECONDS - elapsed_time, 1)
            console_print(f"Wi-Fi AP active. Inactivity: {elapsed_time}s / Remaining: {remaining_time}s")
            last_timeout_check_log_time = current_time

        # Check if timeout has occurred AND we haven't already logged the shutdown for this state
        if (current_time - last_activity_time > WIFI_TIMEOUT_SECONDS) and not ap_is_off_and_logged:
            console_print(f"--- Wi-Fi AP timed out after {config.WIFI_AP_TIMEOUT_MINUTES} minutes of inactivity. ---")
            shut_down_wifi_and_sleep() # Call the common shutdown function
            ap_is_off_and_logged = True # IMPORTANT: Set flag AFTER shutdown is triggered and logged
    elif not wifi.radio.enabled and not ap_is_off_and_logged:
        # This branch ensures that if the AP was manually turned off,
        # or if the board started without AP enabled, it logs its status once.
        # However, for our timeout/button case, ap_is_off_and_logged will be set to True
        # by the shutdown process, so this specific block will mostly serve
        # if there's a unique unlogged "AP off" state.
        console_print("Wi-Fi AP is currently off (and status not yet logged this cycle).")
        ap_is_off_and_logged = True


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
    # Always print to serial console for debugging purposes
    print(f"[PicoWide]: {message}") 
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
        #console_print(status) # Uncomment to show each on/off cycle on the console
        # console_print(status) # Removed to avoid spamming console during timeout test

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

"""
Commented out test button code here and in index.html
"""
#@server.route("/test", methods=["POST"])
#def test_button(request: Request):
#   """
#   Handle test button functionality to verify connection.
#    
#    :param Request request: The HTTP request object
#   :return: Plain text response confirming functionality
#   :rtype: Response
#   """
#   return Response(request, "Button works!", content_type="text/plain")

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
        console_print("Blinky on" if blinky_enabled else "Blinky off")        
        return Response(request, next_action, content_type="text/plain")
    except Exception as e:
        return Response(request, f"Error: {str(e)}", content_type="text/plain")

# --- NEW: Hotspot Control Route ---
@server.route("/toggle-hotspot-control", methods=["POST"])
def toggle_hotspot_control(request: Request):
   """
   Handles requests to toggle between keeping hotspot open and immediate shutdown.
   When timeout is disabled, provides immediate shutdown option.
   When timeout is enabled, disables timeout and keeps hotspot open.
   """
   global timeout_disabled, ap_is_off_and_logged
   
   if not timeout_disabled:
       # User wants to keep hotspot open (disable timeout)
       timeout_disabled = True
       console_print("Automatic timeout disabled. Hotspot will remain open until manually closed.")
       return Response(request, "Close Hotspot", content_type="text/plain")
   else:
       # User wants to close hotspot immediately
       console_print("Received request to close hotspot immediately.")
       shut_down_wifi_and_sleep()
       ap_is_off_and_logged = True
       return Response(request, "Hotspot closed. Physical power cycle needed to restart.", content_type="text/plain")

# --- LEGACY: Power Save Route (kept for compatibility) ---
@server.route("/power-save", methods=["POST"])
def power_save_mode(request: Request):
    """
    Handles requests to enter power-saving mode.
    Shuts down Wi-Fi AP and signals a permanent low-power state.
    Requires a physical power cycle to restart the hotspot.
    """
    global ap_is_off_and_logged
    if not ap_is_off_and_logged: # Only log manual shutdown once
        console_print("Received request to enter power-save mode.")
        shut_down_wifi_and_sleep()
        ap_is_off_and_logged = True # Set flag after manual shutdown is triggered and logged
    return Response(request, "Power saving mode activated. Wi-Fi AP shut down. Physical power cycle needed to restart.", content_type="text/plain")

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
console_print(f"Wi-Fi AP timeout set to {config.WIFI_AP_TIMEOUT_MINUTES} minutes ({WIFI_TIMEOUT_SECONDS} seconds).")


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
    
    # NEW: Check Wi-Fi timeout periodically and log progress
    check_wifi_timeout()
    
    # NEW: Add a small delay and garbage collection for stability
    time.sleep(0.1) # Prevents busy-waiting and allows some time for other tasks
    gc.collect() # Periodically run garbage collection