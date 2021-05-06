High-level API
##############

High-level interface provides object-oriented way to deal with the DSW data
entities. There are currently 6 of these, accessible on instances of the
:class:`~sdk.DataStewardshipWizardSDK`:

    * :attr:`~sdk.DataStewardshipWizardSDK.app_config`
    * :attr:`~sdk.DataStewardshipWizardSDK.documents`
    * :attr:`~sdk.DataStewardshipWizardSDK.packages`
    * :attr:`~sdk.DataStewardshipWizardSDK.questionnaires`
    * :attr:`~sdk.DataStewardshipWizardSDK.templates`
    * :attr:`~sdk.DataStewardshipWizardSDK.users`

See API reference of respective classes for more info and examples on usage:

    * :doc:`../reference/api/app_config_api`
    * :doc:`../reference/api/document_api`
    * :doc:`../reference/api/package_api`
    * :doc:`../reference/api/questionnaire_api`
    * :doc:`../reference/api/template_api`
    * :doc:`../reference/api/user_api`


Models
======

There is a :class:`~model.Model` class for each entity (except package) which
can be also used directly. This is useful if you already have the data of the
entity, but not the model, so have to instantiate it yourself:

.. code-block:: python

    # Somehow you got all the data of a user
    user_data = ...
    # You must pass also the `DataStewardshipWizardSDK` instance to the model;
    # argument `__update_attrs` is used to instantiate the model and to put it
    # in the right state
    user = User(dsw_sdk, __update_attrs=user_data)
    # You can also use the `_update_attrs` method, it's the same
    user = User(dsw_sdk)
    user._update_attrs(user_data)
