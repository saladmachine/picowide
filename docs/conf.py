# conf.py - Minimal Sphinx configuration

import os
import sys
sys.path.insert(0, os.path.abspath('../../')) # Adjust this if your code is not in the parent directory

# Project information
project = 'picowide'
copyright = '2025, Joseph Wayne Pardue' # Replace with your name
author = 'Joseph Wayne Pardue' # Replace with your name

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc', # Enable if you plan to document Python code
    'sphinx.ext.napoleon', # Recommended for Google/NumPy style docstrings
    'sphinx.ext.todo', # Example extension for todo lists
    'sphinx.ext.viewcode', # For linking to source code
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'

# -- Extension configuration -------------------------------------------------

# Napoleon settings (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Mock imports for CircuitPython modules that can't be imported
autodoc_mock_imports = [
    "board", 
    "digitalio", 
    "analogio", 
    "busio", 
    "pwmio",
    "displayio",
    "time",
    "microcontroller",
    "supervisor"
]
