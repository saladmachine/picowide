# **Picowide: Your Pico W's Portable Web IDE**

## **Overview**

Picowide transforms your Raspberry Pi Pico W into a self-contained, web-based Integrated Development Environment (IDE). By broadcasting its own Wi-Fi hotspot, Picowide allows you to connect directly with any modern device – be it a smartphone, tablet, or laptop – and manage your Pico W's files, edit code, and monitor its console, all through a familiar web browser interface.

Whether you're in a remote field, a cluttered lab, or simply need to update a `secrets.py` file without pulling out a laptop, Picowide puts a powerful development environment right where you need it: on the Pico itself. It's designed for rapid prototyping, field configuration, and on-the-go adjustments for your CircuitPython projects.

## **Features**

* **Self-Hosted Web Server:** Runs directly on the Pico W, serving the entire web interface.
* **Wi-Fi Hotspot (Access Point):** Creates a "Picowide" Wi-Fi network, allowing direct connection from any device.
* **Bulletproof Configuration System:**
    * Never crashes - always falls back to working defaults if config fails.
    * HTML entity decoding fixes quote corruption from web sources.
    * Individual attribute validation with graceful fallback.
    * Rapid LED blinking indicates configuration errors.
    * Self-healing: can always connect to default "Picowide"/"simpletest" to fix issues.
* **Enhanced Input Validation & Error Handling:**
    * WiFi password validation (8-64 character requirement).
    * Safe AP startup with automatic fallback to defaults.
    * IPv4 address configuration with proper timing and error recovery.
    * Comprehensive startup logging for standalone debugging.
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
* **Startup Log Viewer:** Debug standalone battery operation by viewing complete startup sequence via web interface.
* **Onboard LED Control:** Toggle the Pico W's onboard LED (for basic system testing/feedback).
* **Responsive Web Interface:** Optimized for usability across mobile, tablet, and desktop browsers.
* **Standalone Battery Operation:** Fully functional when powered by external battery without USB connection.

## **Getting Started**

### **Hardware Requirements**

* Raspberry Pi Pico W
* Micro USB cable (for initial CircuitPython flashing)
* External power source (battery pack, USB power bank, or 5V adapter) for standalone operation

### **Software Requirements**

* **CircuitPython:** Ensure your Raspberry Pi Pico W is running a recent version of CircuitPython (e.g., 8.x or 9.x series) that includes the `adafruit_httpserver` library.
* **`adafruit_httpserver` library:** This library is crucial for the web server functionality. It might need to be manually added to your Pico's `lib` folder if not included in your CircuitPython build.

### **Installation**

1.  **Flash CircuitPython:** If you haven't already, flash the latest CircuitPython firmware onto your Raspberry Pi Pico W.
2.  **Install Libraries:** Copy the `adafruit_httpserver` library (and its dependencies) into the `lib` folder on your Pico W's CIRCUITPY drive.
3.  **Download Picowide Files:** Download the `code.py`, `index.html`, `styles.css`, and `config.py` files from this repository.
4.  **Copy Files to Pico:** Copy these four files directly into the root directory of your Pico W's CIRCUITPY drive.
5.  **Configure Settings (Optional):** Edit `config.py` to adjust Wi-Fi credentials, timeout duration, and other settings.
6.  **Power Cycle:** Safely eject your Pico W from your computer, then unplug and re-plug it to power it on.

## **Usage**

### **Initial Connection**

1.  **Connect to Hotspot:** On your smartphone, tablet, or computer, go to your Wi-Fi settings. You should see a new Wi-Fi network named **"Picowide"** (or your custom SSID from config.py). Connect to this network using the password **"simpletest"** (or your custom password).
2.  **Open Web Interface:** Once connected, open a web browser and navigate to `http://192.168.4.1`.

### **Web Interface Controls**

You will see the Picowide interface with various buttons:

* **Blinky On/Off:** Toggles the onboard LED.
* **Monitor On/Off:** Starts/stops viewing real-time console output.
* **List Files:** Shows a list of files on the Pico.
* **Create File:** Prompts to create a new empty file.
* **View Startup Log/Hide Startup Log:** Shows complete startup sequence for debugging standalone operation.
* **Keep Hotspot Open/Close Hotspot:** Controls automatic timeout behavior.

### **File Management**

* Click on a listed file to select it, then use **Open** to view/edit or **Delete** to remove it.
* The built-in editor supports syntax highlighting and preserves special characters.
* Use **Save** to write changes back to the Pico's filesystem.
* Use the **Close File List** button to return to the main screen.

### **Standalone Battery Operation**

Picowide is designed to work completely independently:

1. **Power via VSYS:** Connect external power (3.7-5.5V) to VSYS pin (GPIO 39) and GND.
2. **No USB Required:** Once powered externally, the system runs without any USB connection.
3. **Startup Debugging:** Use the "View Startup Log" button to see exactly what happened during boot, including any configuration issues.

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
# Wi-Fi hotspot configuration
WIFI_SSID = "Picowide"
WIFI_PASSWORD = "simpletest"

# Wi-Fi timeout in minutes (default: 10)
WIFI_AP_TIMEOUT_MINUTES = 10

# LED blink interval in seconds (default: 0.25, rapid: 0.10 for errors)
BLINK_INTERVAL = 0.25
```

### **Error Recovery**

Picowide features a bulletproof configuration system:

* **Missing config.py:** System uses defaults and continues normally.
* **Corrupted config.py:** Individual settings fall back to defaults, system remains functional.
* **HTML entity corruption:** Automatically decodes `&quot;` and other entities from web-corrupted files.
* **Invalid passwords:** Falls back to "Picowide"/"simpletest" with error indication via rapid LED blinking.
* **Visual error indication:** Rapid LED blinking (0.10s interval) indicates configuration problems.

## **Troubleshooting**

### **Standalone Operation Issues**

If Picowide doesn't work when powered by battery:

1. **Check the Startup Log:** Connect to the hotspot and use "View Startup Log" to see what went wrong during boot.
2. **Verify Power:** Ensure 3.7-5.5V on VSYS pin with adequate current capacity.
3. **Check LED:** Rapid blinking indicates configuration errors - connect to default "Picowide"/"simpletest" to fix.
4. **Hot-swap method:** Start with USB connected, add external power to VSYS, then unplug USB.

### **Configuration Problems**

* **Rapid LED blinking:** Indicates config errors - system falls back to "Picowide"/"simpletest" credentials.
* **Can't connect:** Try default SSID "Picowide" with password "simpletest".
* **Web interface issues:** Check startup log for detailed error information.

## **Design Philosophy & Security Considerations**

Picowide prioritizes accessibility and on-device functionality for rapid development and field use. These design choices directly influence its security posture:

* **Hotspot-Only for IDE (Default):** This version of Picowide operates exclusively as its own Wi-Fi Access Point (hotspot). This guarantees direct access in any environment without relying on external network infrastructure. While it offers unparalleled convenience for field deployment, it also means the IDE is accessible to anyone who can connect to the "Picowide" Wi-Fi network.
* **Password Protection:** The hotspot requires a password (default: "simpletest", configurable in `config.py`) to prevent unauthorized access.
* **No Local Wi-Fi (Station Mode) for IDE:** This release of the IDE does not automatically attempt to connect to local Wi-Fi networks. This simplifies the codebase and focuses on its "always-available" hotspot role.
* **Power Management:** The automatic timeout feature helps prevent accidental battery drain in field deployments while maintaining security by limiting exposure time.
* **Self-Healing:** The bulletproof configuration system ensures the device remains accessible even with corrupted settings.

## **Technical Implementation**

### **Key Improvements**

* **Enhanced Error Handling:** Comprehensive validation and fallback mechanisms prevent system crashes.
* **Standalone Debugging:** Complete startup logging accessible via web interface for battery-powered debugging.
* **Input Validation:** WiFi password validation and safe AP startup procedures.
* **Configuration Robustness:** HTML entity decoding and individual setting validation.
* **Power Optimization:** Intelligent timeout management with user control.

### **System Requirements**

* CircuitPython 8.x or 9.x
* `adafruit_httpserver` library
* At least 264KB RAM (standard on RP2040)
* 2MB flash storage (standard on Pico W)

## **Contributing**

Contributions are welcome! If you have ideas for improvements or find bugs, please open an issue or submit a pull request on this GitHub repository.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## **Acknowledgments**

* Built with CircuitPython and `adafruit_httpserver`.
* Inspired by the need for portable microcontroller development.
* Enhanced through extensive testing and real-world field deployment scenarios.

---

**AI Assistance Note:** This project, including aspects of its code (e.g., structure, debugging assistance, error handling enhancements) and the drafting of this `README.md`, was significantly assisted by large language models, specifically Gemini by Google and Claude by Anthropic. This collaboration highlights the evolving landscape of modern open-source development, demonstrating how AI tools can empower makers to bring complex projects to fruition and achieve robust, production-ready implementations.