#
# Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
#

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import re
with open('../es100/__init__.py', 'r') as f:
    _version_re = re.compile(r"__version__\s=\s'(.*)'")
    version = _version_re.search(f.read()).group(1)

project = 'es100-wwvb'
copyright = '2023, Martin J Levy'
author = 'Martin J Levy'
release = str(version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
]

html_theme = "sphinx_rtd_theme"

templates_path = ['_templates']
exclude_patterns = [
    'wwvb/__init__.py', 'es100/__init__.py',
    '_build', 'Thumbs.db', '.DS_Store'
]

autoclass_content = 'both'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
