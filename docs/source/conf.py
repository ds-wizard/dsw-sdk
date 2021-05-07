# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/http_client/'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/http_client/requests_impl'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/low_level_api'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/config'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/high_level_api'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/high_level_api/models'))
sys.path.insert(0, os.path.abspath('../../src/dsw_sdk/common'))


# -- Project information -----------------------------------------------------

project = 'Data Stewardship Wizard SDK'
copyright = '2021, Jakub Drahoš'
author = 'Jakub Drahoš'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Autodoc configuration ---------------------------------------------------

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_type_aliases = {
    'HttpResponse': 'interface.HttpResponse',
    'HttpClient': 'dsw_sdk.http_client.interface.HttpClient',
    'TokenRetrievalStrategy': 'auth.TokenRetrievalStrategy',
    'RequestsHttpResponse': 'http_client.RequestsHttpResponse',
    'Model': 'model.Model',
    'State': 'model.State',
    'AppConfig': 'dsw_sdk.high_level_api.models.app_config.AppConfig',
    'Document': 'dsw_sdk.high_level_api.models.document.Document',
    'Questionnaire': 'dsw_sdk.high_level_api.models.questionnaire.Questionnaire',
    'Template': 'dsw_sdk.high_level_api.models.templates.template.Template',
    'User': 'dsw_sdk.high_level_api.models.user.User',
    'Snapshot': 'snapshot.Snapshot',
    'Type': 'common.types.Type',
}
autoclass_content = 'both'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}
autodoc_mock_imports = ['yaml', 'jwt']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
