import os
import sys
sys.path.insert(0, os.path.abspath('..'))
print(f"DEBUG: sys.path at conf.py load: {sys.path}") # This debug line is still here for now

# Picowide Documentation Configuration
project = 'Picowide'
copyright = '2025, Joseph Wayne Pardue'
author = 'Joseph Wayne Pardue'
release = '1.0'

extensions = ['sphinx.ext.autodoc']

# Disable problematic extensions if they are implicitly loaded
# This handles the 'sphinxcontrib.applehelp' error that caused issues previously
if 'sphinxcontrib.applehelp' in extensions:
    extensions.remove('sphinxcontrib.applehelp')

# Mock out CircuitPython specific imports so Sphinx can import the code
autodoc_mock_imports = ['board', 'busio', 'digitalio', 'microcontroller', 'supervisor', 'wifi', 'socketpool', 'json', 're', 'ssl', 'os', 'ulab', 'storage', 'terminalio', 'time', 'usb_hid', 'adafruit_httpserver']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_title = 'Picowide: Your Pico W\'s Portable Web IDE'
html_short_title = 'Picowide'