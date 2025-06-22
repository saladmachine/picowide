Picowide: Your Pico W's Portable Web IDE
Overview
Picowide transforms your Raspberry Pi Pico W into a self-contained, web-based Integrated Development Environment (IDE). By broadcasting its own Wi-Fi hotspot, Picowide allows you to connect directly with any modern device – be it a smartphone, tablet, or laptop – and manage your Pico W's files, edit code, and monitor its console, all through a familiar web browser interface.

Whether you're in a remote field, a cluttered lab, or simply need to update a secrets.py file without pulling out a laptop, Picowide puts a powerful development environment right where you need it: on the Pico itself. It's designed for rapid prototyping, field configuration, and on-the-go adjustments for your CircuitPython projects.

Features
Self-Hosted Web Server: Runs directly on the Pico W, serving the entire web interface.

Wi-Fi Hotspot (Access Point): Creates a "Picowide" Wi-Fi network, allowing direct connection from any device.

File Manager:

List all files on the CIRCUITPY drive.

Open and view file contents.

Edit and save changes to existing files.

Create new empty files.

Delete files (with confirmation).

Console Monitor: View real-time output from the Pico's console directly in your browser.

Onboard LED Control: Toggle the Pico W's onboard LED (for basic system testing/feedback).

Responsive Web Interface: Optimized for usability across mobile, tablet, and desktop browsers.

Getting Started
Hardware Requirements
Raspberry Pi Pico W

Micro USB cable (for initial CircuitPython flashing and power)

Software Requirements
CircuitPython: Ensure your Raspberry Pi Pico W is running a recent version of CircuitPython (e.g., 8.x or 9.x series) that includes the adafruit_httpserver library.

adafruit_httpserver library: This library is crucial for the web server functionality. It might need to be manually added to your Pico's lib folder if not included in your CircuitPython build.

Installation
Flash CircuitPython: If you haven't already, flash the latest CircuitPython firmware onto your Raspberry Pi Pico W.

Install Libraries: Copy the adafruit_httpserver library (and its dependencies) into the lib folder on your Pico W's CIRCUITPY drive.

Download Picowide Files: Download the code.py, index.html, and styles.css files from this repository.

Copy Files to Pico: Copy these three files directly into the root directory of your Pico W's CIRCUITPY drive.

Power Cycle: Safely eject your Pico W from your computer, then unplug and re-plug it to power it on.

Usage
Connect to Hotspot: On your smartphone, tablet, or computer, go to your Wi-Fi settings. You should see a new Wi-Fi network named "Picowide". Connect to this network.

Note: By default, this release of Picowide does NOT have a password on the hotspot for simplicity in the FOSS offering. For secure deployments, it's highly recommended to add a password (see code.py comments).

Open Web Interface: Once connected, open a web browser and navigate to http://192.168.4.1.

Explore the IDE: You will see the Picowide interface with various buttons:

Test Connection: Verifies communication with the Pico.

Blinky On/Off: Toggles the onboard LED.

Monitor On/Off: Starts/stops viewing console output.

List Files: Shows a list of files on the Pico.

Create File: Prompts to create a new empty file.

Click on a listed file to select it, then use Open to view/edit or Delete to remove it. Use the Close File List button to return to the main screen.

Design Philosophy & Security Considerations
Picowide prioritizes accessibility and on-device functionality for rapid development and field use. These design choices directly influence its security posture:

Hotspot-Only for IDE (Default): This version of Picowide operates exclusively as its own Wi-Fi Access Point (hotspot). This guarantees direct access in any environment without relying on external network infrastructure. While it offers unparalleled convenience for field deployment, it also means the IDE is accessible to anyone who can connect to the "Picowide" Wi-Fi network. For simple field use, adding a password to the hotspot is highly recommended (configurable in code.py).

No REPL (Read-Eval-Print Loop): While a REPL is an invaluable debugging tool, integrating a web-accessible REPL into a deployed system introduces significant security and stability risks. It allows arbitrary code execution, which could lead to file corruption, data exposure, or device instability on a resource-constrained microcontroller. For a safer and more robust tool for the community, the REPL functionality has been intentionally excluded from this release.

No Local Wi-Fi (Station Mode) for IDE: This release of the IDE does not automatically attempt to connect to local Wi-Fi networks. This simplifies the codebase and focuses on its "always-available" hotspot role. For instruments needing to connect to a local network (e.g., to send data to a Home Assistant hub), a separate, stripped-down "instrument firmware" that includes Wi-Fi client (station) mode capabilities and a secure secrets.py editor (rather than the full IDE) is recommended.

Contributing
Contributions are welcome! If you have ideas for improvements or find bugs, please open an issue or submit a pull request on this GitHub repository.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
Built with CircuitPython and adafruit_httpserver.

Inspired by the need for portable microcontroller development.