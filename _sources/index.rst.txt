Picowide: Your Pico W's Portable Web IDE
========================================

Transform your Raspberry Pi Pico W into a self-contained, web-based development environment. No laptop required – just connect to your Pico's Wi-Fi hotspot and code from any device with a browser.

**Quick Start**: Flash CircuitPython → Copy files → Connect to "Picowide" Wi-Fi → Browse to 192.168.4.1

Key Features
------------

* **Zero-Setup Web IDE** - Complete development environment in your browser
* **Wi-Fi Hotspot Mode** - No external network needed, works anywhere  
* **File Management** - Create, edit, delete files directly on your Pico
* **Real-time Console** - See your code output instantly
* **Mobile-Friendly** - Code from your phone or tablet
* **Secure by Design** - No REPL access, password-protected hotspot

Perfect For
-----------

* **Field Research** - Update sensor configurations in remote locations
* **Education** - Teach coding without complex setup requirements  
* **Prototyping** - Quick iterations without desktop dependency
* **IoT Projects** - Configure devices after deployment

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   first-use

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   file-management
   console-monitoring
   configuration
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Technical Reference

   architecture
   api-endpoints
   source-code
   api

What Makes Picowide Special?
----------------------------

Unlike traditional development setups that require a computer and cable connection, Picowide creates a complete wireless development environment. Your Pico W becomes both the target device AND the development server.

**Traditional Setup:**
Computer ↔ USB Cable ↔ Pico W

**Picowide Setup:**
Phone/Tablet ↔ Wi-Fi ↔ Pico W (running web IDE)

Security Philosophy
-------------------

Picowide balances convenience with safety:

- **Hotspot isolation** prevents network-based attacks
- **No REPL access** eliminates arbitrary code execution risks  
- **File-only operations** limit potential damage
- **Password protection** controls access to the IDE

Ready to Get Started?
--------------------

Jump to :doc:`installation` to set up Picowide in under 5 minutes!