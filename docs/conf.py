# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'NeuroStride-VL'
copyright = '2026, NeuroStride-VL Team'
author = 'NeuroStride-VL Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'sphinx_autodoc_typehints',
    'myst_parser',
    'sphinx_copybutton',
    'sphinxcontrib.mermaid',
    'sphinx_design',
    'sphinx_togglebutton',
    'sphinx_favicon',
]

templates_path = ['_templates']
exclude_patterns = []

# Enable both .md and .rst sources
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Theme options
html_theme_options = {
    'logo_only': True,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': 'blob',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Favicon
html_favicon = '_static/favicon.ico'

# -- Extension configuration -------------------------------------------------

# Autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_rtype = True
napoleon_use_ivar = True

# Intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
    'gym': ('https://www.gymlibrary.dev/', None),
}

# Mermaid
mermaid_output_format = 'svg'
mermaid_init_js = """
    mermaid.initialize({
        startOnLoad: true,
        theme: 'neutral',
        themeVariables: {
            primaryColor: '#2980B9',
            edgeLabelBackground: '#ffffff'
        }
    });
"""

# Copybutton
copybutton_prompt_text = r'>>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '
copybutton_prompt_is_regexp = True

# -- Custom settings --------------------------------------------------------

# Project info for HTML
html_title = f"{project} {release} Documentation"
html_short_title = project
html_logo = '_static/logo.png'

# Custom CSS/JS
html_static_path = ['_static']

# Footer
html_show_copyright = True
html_show_sphinx = False
