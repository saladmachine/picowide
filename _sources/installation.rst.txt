Installation Guide
==================

Get Picowide running on your Raspberry Pi Pico W in under 5 minutes.

Prerequisites
-------------

**Hardware**
- Raspberry Pi Pico W (Wi-Fi enabled version)
- Micro USB cable
- Computer for initial setup (Windows/Mac/Linux)

**Software**  
- Web browser (any modern browser)
- No additional software installation required!

Step 1: Flash CircuitPython
----------------------------

1. **Download CircuitPython Firmware**
   
   Visit `circuitpython.org/board/raspberry_pi_pico_w <https://circuitpython.org/board/raspberry_pi_pico_w/>`_ and download the latest stable release (8.x or 9.x).

2. **Enter Bootloader Mode**
   
   - Hold the **BOOTSEL** button on your Pico W
   - While holding BOOTSEL, plug the USB cable into your computer
   - Release BOOTSEL button
   - Your Pico should appear as **RPI-RP2** drive

3. **Install Firmware**
   
   - Copy the downloaded ``.uf2`` file to the **RPI-RP2** drive
   - The Pico will automatically reboot
   - It should now appear as **CIRCUITPY** drive

Step 2: Install Required Libraries
-----------------------------------

1. **Download Library Bundle**
   
   Get the `Adafruit CircuitPython Bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases>`_ that matches your CircuitPython version.

2. **Extract and Copy Libraries**
   
   From the bundle, copy these to your Pico's ``lib/`` folder:
   
   .. code-block:: text
   
      CIRCUITPY/lib/
      └── adafruit_httpserver/
          ├── __init__.py
          ├── mime_types.py
          ├── request.py
          ├── response.py
          └── server.py

Step 3: Download Picowide Files
--------------------------

Get these files from the `Picowide GitHub repository <https://github.com/saladmachine/picowide>`_:

**Core Application Files:**
   * ``code.py`` - Main web server application
   * ``boot.py`` - Boot configuration  
   * ``config.py`` - Settings and parameters

**Web Interface Files:**
   * ``index.html`` - The web-based IDE interface
   * ``styles.css`` - Styling for the web interface

Step 4: Copy Files to Your Pico
----------------------------

Copy **all five files** to the **root directory** of your Pico's CIRCUITPY drive:

.. code-block:: text

   CIRCUITPY/
   ├── code.py
   ├── boot.py  
   ├── config.py
   ├── index.html
   ├── styles.css
   └── lib/
       └── adafruit_httpserver/

Step 5: First Boot
------------------

1. **Safely Eject** your Pico from your computer
2. **Unplug and reconnect** the USB cable (or use external power)
3. **Wait 15-30 seconds** for startup
4. **Look for the "Picowide" Wi-Fi network**

Your First Connection
---------------------

1. **Find the Picowide Hotspot**

   On your phone/computer, you should see:

   .. code-block:: text

      Available Networks:
      Picowide          [New network]
      YourHomeWiFi      
      Other networks...

2. **Connect with Password**

   - Select the "Picowide" network
   - Enter password: ``simpletest``
   - Wait for connection confirmation

3. **Open the Web Interface**

   - Open any web browser
   - Navigate to: ``http://192.168.4.1``
   - You should see the Picowide interface!

4. **Test Basic Functions**

   Try these to confirm everything works:
   - Click **"Blinky On"** - The Pico's LED should light up
   - Click **"List Files"** - You should see your project files
   - Click **"Monitor On"** - You should see console output

Troubleshooting Installation
----------------------------

**"Picowide" network doesn't appear**
   - Wait longer (up to 60 seconds)
   - Check USB power supply (needs stable 5V)
   - Verify all 5 files copied correctly
   - Look for error messages on CIRCUITPY drive

**Can't connect to 192.168.4.1**
   - Ensure connected to "Picowide" network (not your home Wi-Fi)
   - Try ``http://192.168.4.1`` (not ``https://``)
   - Disable mobile data on phone
   - Clear browser cache

**Interface loads but buttons don't work**
   - Check browser console for JavaScript errors
   - Verify ``styles.css`` copied correctly
   - Try different browser

Next Steps
----------

**Installation Complete!** 

Continue to :doc:`first-use` to learn the interface!