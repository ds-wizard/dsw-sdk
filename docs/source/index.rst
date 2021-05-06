.. Data Stewardship Wizard SDK documentation master file, created by
   sphinx-quickstart on Sun Mar 21 15:11:03 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
############

This projects aims at providing unified and easy-to-use Python library for
communicating with the Data Stewardship Wizard API. For more info about
the DSW project itself, see `official webpage`_ or the `API documentation`_.

.. _official webpage: https://ds-wizard.org/
.. _API documentation: https://api.demo.ds-wizard.org/swagger-ui/


Installation
************

You can install this library via PyPI:

.. code-block::

   pip install dsw-sdk


Quickstart
**********

The only mandatory step need in order to get going is to initialize the whole
SDK and tell it, where is the DSW API located and how to connect to it:

.. code-block:: python

   dsw_sdk = DataStewardshipWizardSDK(
      api_url='http://localhost:3000',
      email='albert.einstein@example.com',
      password='password',
   )

Now you are ready to go.

.. note::

   Note that this is only *illustrative example* and we
   encourage you **not** to store secrets like passwords in the source code.
   There are better mechanisms (env variables) introduced later in this
   documentation.


Basic usage
***********

Most actions should be done via the high-level interfaces provided on an
instance of the :class:`~sdk.DataStewardshipWizardSDK` class. These interfaces
operate with subclasses of :class:`~model.Model` class (e.g.
:class:`~user.User`) -- these are the DSW data entities. Basically they are
just data classes with bunch of attributes and methods for saving the entity
(:meth:`~model.Model.save`) on the server and deleting it
(:meth:`~model.Model.delete`).

.. code-block:: python

   user = dsw_sdk.users.create_user(
      first_name='John',
      last_name='Doe',
      email='john.doe@example.com',
   )
   user.password = os.getenv('SECRET_PASSWORD')
   user.save()

   ...

   user.delete()

For more advanced usage, see the next sections.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   advanced_usage/index
   reference/index

Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
