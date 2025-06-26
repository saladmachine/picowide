"""
Pico 2 W Hotspot File Editor + Interactive REPL + Serial Monitor with Non-blocking LED Control
============================================================================================
 
Complete web-based CircuitPython development environment with file editing,
interactive REPL, serial monitor functionality, and non-blocking LED operations.

Features:
- Creates WiFi hotspot "PicoTest" 
- Serves file editor at http://192.168.4.1
- Interactive REPL console with code execution
- Load and save files through web interface
- FILE BROWSER: List and select files in the root directory
- Auto-reboot when code.py is saved (enables live development)
- Send commands and see live console output
- Non-blocking LED blink control via web interface
- Variable inspection and namespace management

Hardware Requirements:
- Raspberry Pi Pico 2 W (RP2350)

Software Requirements:
- CircuitPython 9.2.7 or later
- adafruit_httpserver library
- No additional libraries needed!

Usage:
1. Upload this code as code.py to CIRCUITPY drive
2. Upload index.html and styles.css to CIRCUITPY drive
3. Connect to "PicoTest" WiFi network (no password)
4. Open browser to http://192.168.4.1
5. Use interactive REPL to execute Python commands
6. Use LED Control button to start/stop blinking
7. Use file browser to select and load files
8. Use file editor to load/save files
9. Saving code.py automatically reboots Pico for testing

Author: CircuitPython Interactive Development Environment
License: MIT License
Version: 2.4 - FIXED LED CONTROL ENDPOINT
"""

import time
import json
import wifi
import socketpool
import ipaddress
import board
import digitalio
import gc
import os
from adafruit_httpserver import Server, Request, Response

# Configuration
HOTSPOT_SSID = "PicoTest"
HOTSPOT_IP = "192.168.4.1"
HOTSPOT_NETMASK = "255.255.255.0"
HOTSPOT_GATEWAY = "192.168.4.1"

# Global variables for scheduled reboot and console monitoring
reboot_scheduled = 0
console_buffer = []
max_buffer_size = 1000

# REPL globals for maintaining execution context
repl_globals = {'__name__': '__main__'}
repl_locals = {}
command_history = []
max_history = 100

# LED setup and blink control
led = None
led_blink_enabled = False
led_last_toggle = 0
led_blink_interval = 0.5  # 500ms blink interval

# Try multiple ways to initialize the LED
try:
    if hasattr(board, 'LED'):
        led = digitalio.DigitalInOut(board.LED)
        led.switch_to_output(value=False)
        print("LED initialized using board.LED")
    elif hasattr(board, 'GP25'):
        # Fallback for Pico 2 W - LED is often on GP25
        led = digitalio.DigitalInOut(board.GP25)
        led.switch_to_output(value=False)
        print("LED initialized using board.GP25")
    else:
        print("Warning: No LED pin found")
except Exception as e:
    print(f"LED initialization error: {e}")
    led = None

def add_to_console(message):
    """Add message to console buffer."""
    global console_buffer
    
    console_buffer.append({
        'time': time.monotonic(),
        'message': str(message) + '\n'
    })
    
    # Limit buffer size
    if len(console_buffer) > max_buffer_size:
        console_buffer = console_buffer[-max_buffer_size:]

def execute_code(code_string):
    """Execute Python code and return result, output, and any errors."""
    global repl_globals, repl_locals
    
    result = None
    error = None
    output = ""
    
    # Create a custom print function that captures output
    captured_prints = []
    
    def capture_print(*args, **kwargs):
        # Convert all arguments to strings and join them
        text = ' '.join(str(arg) for arg in args)
        captured_prints.append(text)
    
    # Add our custom print to the execution environment
    repl_globals['print'] = capture_print
    
    try:
        # Try to eval first (for expressions)
        try:
            result = eval(code_string, repl_globals, repl_locals)
        except SyntaxError:
            # If eval fails, try exec (for statements)
            exec(code_string, repl_globals, repl_locals)
            result = None
            
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)}"
    
    finally:
        # Restore original print function (built-in)
        if 'print' in repl_globals:
            del repl_globals['print']
    
    # Join captured print statements
    if captured_prints:
        output = '\n'.join(captured_prints)
    
    return result, output, error

def update_led():
    """Non-blocking LED update - call this frequently in main loop."""
    global led_last_toggle
    
    if led is None or not led_blink_enabled:
        return
    
    current_time = time.monotonic()
    if current_time - led_last_toggle >= led_blink_interval:
        led.value = not led.value
        led_last_toggle = current_time
        status = 'ON' if led.value else 'OFF'
        print(f"LED: {status}")
        add_to_console(f"LED: {status}")

def create_hotspot():
    """Create WiFi hotspot for serving the editor interface."""
    print("=== PICO 2 W INTERACTIVE DEVELOPMENT ENVIRONMENT ===")
    add_to_console("=== PICO 2 W INTERACTIVE DEVELOPMENT ENVIRONMENT ===")
    print("Creating hotspot...")
    add_to_console("Creating hotspot...")
    
    try:
        # Create open WiFi hotspot
        wifi.radio.start_ap(ssid=HOTSPOT_SSID)
        
        # Configure IP addressing
        wifi.radio.set_ipv4_address_ap(
            ipv4=ipaddress.IPv4Address(HOTSPOT_IP),
            netmask=ipaddress.IPv4Address(HOTSPOT_NETMASK), 
            gateway=ipaddress.IPv4Address(HOTSPOT_GATEWAY)
        )
        
        message = f"SUCCESS: Hotspot created: {HOTSPOT_SSID}"
        print(message)
        add_to_console(message)
        message = f"SUCCESS: IP Address: {HOTSPOT_IP}"
        print(message)
        add_to_console(message)
        message = "SUCCESS: Security: Open (no password)"
        print(message)
        add_to_console(message)
        return True
        
    except Exception as e:
        message = f"FAILED to create hotspot: {e}"
        print(message)
        add_to_console(message)
        return False

# Initialize REPL environment with useful modules
def init_repl_environment():
    """Initialize REPL with common imports and variables."""
    global repl_globals
    
    # Add common modules to REPL environment
    repl_globals.update({
        'board': board,
        'digitalio': digitalio,
        'time': time,
        'gc': gc,
        'os': os,
        'led': led,
        'console_buffer': console_buffer,
        'add_to_console': add_to_console
    })
    
    add_to_console("REPL initialized with: board, digitalio, time, gc, os, led, console_buffer, add_to_console")

# Create hotspot
if not create_hotspot():
    print("Cannot continue without hotspot. Exiting.")
    raise SystemExit

# Initialize REPL environment
init_repl_environment()

# Initialize HTTP server
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/", debug=False)

@server.route("/")
def editor_page(request: Request):
    """Serve the main index.html page."""
    print("IDE page requested")
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
        return Response(request, html_content, content_type="text/html")
    except OSError:
        return Response(request, "index.html not found", content_type="text/plain")

@server.route("/styles.css")
def serve_css(request: Request):
    """Serve the CSS file."""
    try:
        with open("styles.css", "r") as f:
            css_content = f.read()
        return Response(request, css_content, content_type="text/css")
    except OSError:
        return Response(request, "styles.css not found", content_type="text/plain")

@server.route("/<filename>")
def serve_file(request: Request, filename: str):
    """Serve any file from the root directory."""
    try:
        # Determine content type based on file extension
        if filename.endswith('.html'):
            content_type = "text/html"
        elif filename.endswith('.css'):
            content_type = "text/css"
        elif filename.endswith('.js'):
            content_type = "application/javascript"
        elif filename.endswith('.json'):
            content_type = "application/json"
        else:
            content_type = "text/plain"
        
        print(f"Serving file: {filename}")
        with open(filename, "r") as f:
            file_content = f.read()
        return Response(request, file_content, content_type=content_type)
    except OSError:
        print(f"File not found: {filename}")
        return Response(request, f"File not found: {filename}", content_type="text/plain")

@server.route("/list_files")
def list_files(request: Request):
    """List files in the root directory."""
    try:
        # Get directory listing
        files = []
        
        # List files in root directory
        file_list = os.listdir("/")
        
        for filename in file_list:
            try:
                # Get file info
                stat_info = os.stat("/" + filename)
                
                # Check if it's a file or directory
                # For CircuitPython, stat()[0] contains the file mode
                # 0x8000 bit indicates regular file
                is_file = (stat_info[0] & 0x8000) != 0
                
                file_info = {
                    'name': filename,
                    'is_file': is_file,
                    'size': stat_info[6] if is_file else 0,  # File size
                    'modified': stat_info[8]  # Modification time
                }
                files.append(file_info)
                
            except OSError:
                # If we can't stat the file, just add basic info
                files.append({
                    'name': filename,
                    'is_file': True,
                    'size': 0,
                    'modified': 0
                })
        
        # Sort files: directories first, then files, both alphabetically
        files.sort(key=lambda x: (x['is_file'], x['name'].lower()))
        
        print(f"SUCCESS: Listed {len(files)} files")
        return Response(request, json.dumps(files), content_type="application/json")
        
    except Exception as e:
        error_msg = f"Error listing files: {e}"
        print(f"ERROR: {error_msg}")
        return Response(request, json.dumps({"error": error_msg}), content_type="application/json")

@server.route("/save_file", methods=["POST"])
def save_file(request: Request):
    """Save file to filesystem with auto-reboot for code.py."""
    global reboot_scheduled
    
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        content = data.get("content", "")
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        # Ensure filename doesn't start with / (we're saving to root)
        if filename.startswith('/'):
            filename = filename[1:]
        
        print(f"Saving file: {filename} ({len(content)} characters)")
        add_to_console(f"Saving file: {filename} ({len(content)} characters)")
        
        # Write file to filesystem
        with open(filename, 'w') as f:
            f.write(content)
        
        print(f"SUCCESS: File saved: {filename}")
        add_to_console(f"SUCCESS: File saved: {filename}")
        
        # Auto-reboot for code.py to enable live development
        if filename.lower() == "code.py":
            print("REBOOT: code.py saved - scheduling reboot in 2 seconds...")
            add_to_console("REBOOT: code.py saved - scheduling reboot in 2 seconds...")
            reboot_scheduled = time.monotonic() + 2
            return Response(request, f"File saved: {filename} - Rebooting to apply changes...", content_type="text/plain")
        else:
            return Response(request, f"File saved: {filename}", content_type="text/plain")
        
    except Exception as e:
        error_msg = f"Error saving file: {e}"
        print(f"ERROR: {error_msg}")
        add_to_console(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")

@server.route("/load_file", methods=["POST"])
def load_file(request: Request):
    """Load file from filesystem."""
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "").strip()
        
        if not filename:
            return Response(request, "Filename required", content_type="text/plain")
        
        print(f"Loading file: {filename}")
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except OSError:
            print(f"ERROR: File not found: {filename}")
            return Response(request, "File not found", content_type="text/plain")
        
        print(f"SUCCESS: File loaded: {filename} ({len(content)} characters)")
        response_data = {"content": content}
        return Response(request, json.dumps(response_data), content_type="application/json")
        
    except Exception as e:
        error_msg = f"Error loading file: {e}"
        print(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")

@server.route("/get_console")
def get_console(request: Request):
    """Get console output for web display."""
    try:
        return Response(request, json.dumps(console_buffer), content_type="application/json")
    except Exception as e:
        return Response(request, f"Error getting console: {e}", content_type="text/plain")

@server.route("/execute_command", methods=["POST"])
def execute_command(request: Request):
    """Execute REPL command and return result."""
    global command_history
    
    try:
        data = json.loads(request.body)
        command = data.get("command", "").strip()
        
        if not command:
            return Response(request, json.dumps({"error": "No command provided"}), content_type="application/json")
        
        # Add to command history
        if command not in command_history:
            command_history.append(command)
            if len(command_history) > max_history:
                command_history = command_history[-max_history:]
        
        # Add command to console
        add_to_console(f">>> {command}")
        
        # Execute the command
        result, output, error = execute_code(command)
        
        # Add output to console
        if output:
            add_to_console(output.rstrip())
        
        if error:
            add_to_console(f"ERROR: {error}")
        elif result is not None:
            add_to_console(repr(result))
        
        # Return response
        response_data = {
            "result": repr(result) if result is not None else None,
            "output": output,
            "error": error
        }
        
        return Response(request, json.dumps(response_data), content_type="application/json")
        
    except Exception as e:
        error_msg = f"Error executing command: {e}"
        print(f"ERROR: {error_msg}")
        add_to_console(f"SYSTEM ERROR: {error_msg}")
        return Response(request, json.dumps({"error": error_msg}), content_type="application/json")

@server.route("/get_variables")
def get_variables(request: Request):
    """Get current REPL variables for inspection."""
    try:
        # Get user-defined variables (exclude built-ins)
        user_vars = {}
        for name, value in repl_locals.items():
            if not name.startswith('_'):
                try:
                    user_vars[name] = repr(value)
                except:
                    user_vars[name] = f"<{type(value).__name__}>"
        
        # Add some key globals
        for name in ['led', 'led_blink_enabled']:
            if name in repl_globals:
                try:
                    user_vars[name] = repr(repl_globals[name])
                except:
                    user_vars[name] = f"<{type(repl_globals[name]).__name__}>"
        
        return Response(request, json.dumps(user_vars), content_type="application/json")
        
    except Exception as e:
        return Response(request, f"Error getting variables: {e}", content_type="text/plain")

@server.route("/get_history")
def get_history(request: Request):
    """Get command history."""
    try:
        return Response(request, json.dumps(command_history[-20:]), content_type="application/json")  # Last 20 commands
    except Exception as e:
        return Response(request, f"Error getting history: {e}", content_type="text/plain")

@server.route("/clear_console", methods=["POST"])
def clear_console(request: Request):
    """Clear the console buffer."""
    global console_buffer
    
    try:
        console_buffer = []
        add_to_console("Console cleared by user")
        print("Console buffer cleared")
        return Response(request, "Console cleared", content_type="text/plain")
        
    except Exception as e:
        error_msg = f"Error clearing console: {e}"
        print(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")

@server.route("/led_control", methods=["POST"])
def led_control(request: Request):
    """Toggle LED blinking on/off."""
    global led_blink_enabled
    
    try:
        # Get the raw request data and decode it
        raw_text = request.raw_request.decode("utf8")
        print(f"LED control raw request: {raw_text}")
        add_to_console(f"LED control request received: {len(raw_text)} bytes")
        
        if led is None:
            return Response(request, "LED not available on this device", content_type="text/plain")
        
        # Try to parse as JSON first
        action = ""
        try:
            data = json.loads(request.body)
            action = data.get("action", "").strip().lower()
            print(f"Parsed JSON action: {action}")
        except:
            # Fallback: extract action from the raw text
            if '"action":"on"' in raw_text or '"action": "on"' in raw_text or "action=on" in raw_text:
                action = "on"
            elif '"action":"off"' in raw_text or '"action": "off"' in raw_text or "action=off" in raw_text:
                action = "off"
            print(f"Extracted action from raw text: {action}")
        
        if action == "on":
            led_blink_enabled = True
            message = "LED blinking started"
            print(message)
            add_to_console(message)
            
        elif action == "off":
            led_blink_enabled = False
            # Turn LED off immediately when stopping
            if led is not None:
                led.value = False
            message = "LED blinking stopped"
            print(message)
            add_to_console(message)
        else:
            error_msg = f"Invalid action '{action}'. Use 'on' or 'off'"
            print(error_msg)
            add_to_console(error_msg)
            return Response(request, error_msg, content_type="text/plain")
        
        response_msg = f"LED blink {action}"
        print(f"Sending response: {response_msg}")
        return Response(request, response_msg, content_type="text/plain")
        
    except Exception as e:
        error_msg = f"Error toggling LED: {e}"
        print(f"ERROR: {error_msg}")
        add_to_console(f"ERROR: {error_msg}")
        return Response(request, error_msg, content_type="text/plain")

# Start server in cooperative multitasking mode
print("Starting web server with cooperative multitasking...")
server.start(HOTSPOT_IP, port=80)

print("\n" + "="*60)
print("INTERACTIVE DEVELOPMENT ENVIRONMENT READY:")
print("="*60)
print(f"1. Connect to WiFi: '{HOTSPOT_SSID}' (no password)")
print(f"2. Open browser: http://{HOTSPOT_IP}")
print("3. Use Interactive REPL console to execute Python commands")
print("4. Use LED Control button to start/stop blinking")
print("5. Use File Browser to list and select files")
print("6. All operations are non-blocking using cooperative multitasking!")
print("="*60)
print(f"\nLED Status: {'Available' if led is not None else 'Not available'}")
print("Interactive REPL Environment Ready!")
print("Execute commands → View variables → Control hardware → Browse files → No blocking!")

# Main cooperative multitasking loop
last_status_report = 0
status_report_interval = 60  # Report status every 60 seconds (reduced from 10)

while True:
    try:
        # Check for scheduled reboot
        if reboot_scheduled > 0 and time.monotonic() >= reboot_scheduled:
            import microcontroller
            print("REBOOT: Executing scheduled reboot...")
            microcontroller.reset()
        
        # Handle web requests (non-blocking)
        server.poll()
        
        # Update LED (non-blocking)
        update_led()
        
        # Periodic status reporting (much less frequent now)
        current_time = time.monotonic()
        if current_time - last_status_report >= status_report_interval:
            # Only report to print, not to console buffer
            print(f"System running: LED {'ENABLED' if led_blink_enabled else 'DISABLED'}, Free memory: {gc.mem_free()} bytes, REPL vars: {len(repl_locals)}")
            last_status_report = current_time
        
        # Small delay to prevent overwhelming the CPU
        time.sleep(0.001)  # 1ms delay for cooperative yielding
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        break
    except Exception as e:
        print(f"ERROR: Server error: {e}")
        add_to_console(f"ERROR: Server error: {e}")
        time.sleep(1)

print("Goodbye!")
