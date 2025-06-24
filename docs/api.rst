API Reference
=============

Picowide - Raspberry Pi Pico 2 W Web Development Environment
=============================================================

Project Overview
----------------

Picowide is a CircuitPython application that creates a WiFi hotspot and serves a web-based file editor interface for developing directly on the Pico 2 W. It provides a complete IDE accessible from any device connected to the Pico's WiFi network.

Core Features
~~~~~~~~~~~~~

- WiFi Access Point creation
- Web-based file manager with CRUD operations  
- Real-time file editing through browser interface
- Mobile-friendly responsive design

Technical Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

- Backend: CircuitPython with adafruit_httpserver
- Frontend: Vanilla HTML/CSS/JavaScript
- Access: Connect to "Picowide" WiFi → Navigate to 192.168.4.1

Application Files
-----------------

Main Application (code.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../code.py
   :language: python
   :lines: 1-17
   :caption: Application docstring and overview

Boot Configuration (boot.py)  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../boot.py
   :language: python
   :caption: Boot setup and configuration

Project Settings (config.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../config.py
   :language: python
   :caption: Configuration parameters

