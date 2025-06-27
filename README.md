# **Picowide: Your Pico W's Portable Web IDE**

## **Overview**

Picowide transforms your Raspberry Pi Pico W into a self-contained, web-based Integrated Development Environment (IDE). By broadcasting its own Wi-Fi hotspot, Picowide allows you to connect directly with any modern device – be it a smartphone, tablet, or laptop – and manage your Pico W's files, edit code, and monitor its console, all through a familiar web browser interface.

Whether you're in a remote field, a cluttered lab, or simply need to update a `secrets.py` file without pulling out a laptop, Picowide puts a powerful development environment right where you need it: on the Pico itself. It's designed for rapid prototyping, field configuration, and on-the-go adjustments for your CircuitPython projects.

## **Features**

* **Self-Hosted Web Server:** Runs directly on the Pico W, serving the entire web interface.
* **Wi-Fi Hotspot (Access Point):** Creates a "Picowide" Wi-Fi network, allowing direct connection from any device.
* **Intelligent Power Management:** 
    * Automatic 10-minute timeout shuts down hotspot after inactivity to preserve battery life.
    * Real-time countdown display with 10-second progress updates.
    * User-controlled timeout override via "Keep Hotspot Open" button.
    * Immediate shutdown option via "Close Hotspot" button.
* **File Manager:**
    * List all files on the CIRCUITPY drive.
    * Open and view file contents.
    * Edit and save changes to existing files.
    * Create new empty files.
    * Delete files (with confirmation).
* **Console Monitor:** View real-time output from the Pico's console directly in your browser.
* **Onboard LED Control:** Toggle the Pico W's onboard LED (for basic system testing/feedback).
* **Responsive Web Interface:** Optimized for usability across mobile, tablet, and desktop browsers.

## **Getting Started**

### **Hardware Requirements**

* Raspberry Pi Pico W
* Micro USB cable (for initial CircuitPython flashing and power)

### **Software Requirements**

* **CircuitPython:** Ensure your Raspberry Pi Pico W is running a recent version of CircuitPython (e.g., 8.x or 9.x series) that includes the `adafruit_httpserver` library.
* **`adafruit_httpserver` library:** This library is crucial for the web server functionality. It might need to be manually added to your Pico's `lib` folder if not included in your CircuitPython build.

### **Installation**

1.  **Flash CircuitPython:** If you haven't already, flash the latest CircuitPython firmware onto your Raspberry Pi Pico W.
2.  **Install Libraries:** Copy the `adafruit_httpserver` library (and its dependencies) into the `lib` folder on your Pico W's CIRCUITPY drive.
3.  **Download Picowide Files:** Download the `code.py`, `index.html`, `styles.css`, and `config.py` files from this repository.
4.  **Copy Files to Pico:** Copy these four files directly into the root directory of your Pico W's CIRCUITPY drive.
5.  **Configure Timeout (Optional):** Edit `config.py` to adjust the Wi-Fi timeout duration (default: 10 minutes).
6.  **Power Cycle:** Safely eject your Pico W from your computer, then unplug and re-plug it to power it on.

## **Usage**

1.  **Connect to Hotspot:** On your smartphone, tablet, or computer, go to your Wi-Fi settings. You should see a new Wi-Fi network named **"Picowide"**. Connect to this network. **Picowide's Wi-Fi hotspot requires a password, which defaults to `simpletest`.**
2.  **Open Web Interface:** Once connected, open a web browser and navigate to `http://192.168.4.1`.
3.  **Explore the IDE:** You will see the Picowide interface with various buttons:
    * **Blinky On:** Toggles the onboard LED.
    * **Monitor On:** Starts/stops viewing console output.
    * **List Files:** Shows a list of files on the Pico.
    * **Create File:** Prompts to create a new empty file.
    * **Keep Hotspot Open:** Disables the automatic 10-minute timeout (toggles to "Close Hotspot" for immediate shutdown).
    * Click on a listed file to select it, then use **Open** to view/edit or **Delete** to remove it. Use the **Close File List** button to return to the main screen.

### **Power Management**

Picowide includes intelligent power management to extend battery life during field deployment:

* **Automatic Timeout:** By default, the Wi-Fi hotspot automatically shuts down after 10 minutes of inactivity.
* **Activity Monitoring:** The system provides real-time feedback with countdown updates every 10 seconds.
* **User Control:** 
    * Use "Keep Hotspot Open" to disable the automatic timeout entirely.
    * Use "Close Hotspot" (when timeout is disabled) for immediate shutdown.
* **Power Cycle Required:** After shutdown, a physical power cycle is required to restart the hotspot.

**Note:** The timeout countdown is NOT reset by web interface activity - only the "Keep Hotspot Open" button can control the timeout behavior.

## **Configuration**

### **config.py Settings**

The `config.py` file allows customization of key settings:

```python
# Wi-Fi timeout in minutes (default: 10)
WIFI_AP_TIMEOUT_MINUTES = 10
```

If `config.py` is missing, Picowide will use default values and continue operating normally.

## **Design Philosophy & Security Considerations**

Picowide prioritizes accessibility and on-device functionality for rapid development and field use. These design choices directly influence its security posture:

* **Hotspot-Only for IDE (Default):** This version of Picowide operates exclusively as its own Wi-Fi Access Point (hotspot). This guarantees direct access in any environment without relying on external network infrastructure. While it offers unparalleled convenience for field deployment, it also means the IDE is accessible to anyone who can connect to the "Picowide" Wi-Fi network. **For simple field use, adding a password to the hotspot is highly recommended (configurable in `config.py` along with the SSID).**
* **No Local Wi-Fi (Station Mode) for IDE:** This release of the IDE does not automatically attempt to connect to local Wi-Fi networks. This simplifies the codebase and focuses on its "always-available" hotspot role. For instruments needing to connect to a local network (e.g., to send data to a Home Assistant hub), a separate, stripped-down "instrument firmware" that includes Wi-Fi client (station) mode capabilities and a *secure* `secrets.py` editor (rather than the full IDE) is recommended.
* **Power Management:** The automatic timeout feature helps prevent accidental battery drain in field deployments while maintaining security by limiting exposure time.

## **Contributing**

Contributions are welcome! If you have ideas for improvements or find bugs, please open an issue or submit a pull request on this GitHub repository.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## **Acknowledgments**

* Built with CircuitPython and `adafruit_httpserver`.
* Inspired by the need for portable microcontroller development.

---

**AI Assistance Note:** This project, including aspects of its code (e.g., structure, debugging assistance) and the drafting of this `README.md`, was significantly assisted by large language models, specifically Gemini by Google and Claude by Anthropic. This collaboration highlights the evolving landscape of modern open-source development, demonstrating how AI tools can empower makers to bring complex projects to fruition.
