Configuration
#############

There are 3 ways to configure the SDK, taking precedence in the following
order:

    * arguments passed to the :class:`~sdk.DataStewardshipWizardSDK` class
      when creating it's instance
    * each config value can be set as an environment variable prefixed with
      ``DSW_SDK_`` (e.g. ``DSW_SDK_EMAIL`` or ``DSW_SDK_API_URL`` is the same
      as passing ``email`` or ``api_url`` to the SDK constructor)
    * config loaded from a YAML file (it's path is passed as ``conf_file``
      keyword argument to :meth:`~sdk.DataStewardshipWizardSDK.__init__`
      method)

You can combine these to achieve whatever configuration you need. Consider
following scenario: You are administrator of multiple DSW instances and you
need to manage them in an effective way. You write a script using this SDK
that leverage all of the above mentioned configuration possibilities:

    * Storing the general configuration that is common for all instances in
      the ``dsw_conf.yml`` file.
    * Password for each admin user is saved in ``DSW_SDK_PASSWORD`` environment
      variable. That way you can include all of the source codes and even the
      configuration files in your version control system without compromising
      some secrets.
    * Each instance can have it's specific configuration passed when
      initializing the library (e.g. some values that are computed only at
      runtime).

Example of a file config

.. code-block:: yaml
   :caption: dsw_conf.yml

    dsw_sdk:  # This section is mandatory
        enable_ssl: false
        headers:
            'User-Agent': 'DSW SDK'
        default_timeout:
            - 6
            - 120

Taking from the example introduced in the quickstart section:

.. code-block:: python

   # Make sure that we have the password set in an env variable
   assert os.getenv('DSW_SDK_PASSWORD')

   dsw_sdk = DataStewardshipWizardSDK(
      api_url='http://localhost:3000',
      email='albert.einstein@example.com',
      file_conf='dsw_conf.yml',
   )

Dependency injection
====================

You can also pass pre-configured instances of HTTP client, session used with
HTTP client and logger to the SDK constructor in order to achieve even more
customizations.

.. code-block:: python

    from dsw_sdk.http_client.interface import HttpClient, HttpResponse
    from somewhere.inside.your.code import already_setup_logger


    class CustomHttpClient(HttpClient):
        # Implementing all abstract methods of
        # the `HttpClient` interface
        def get(self, path: str, **kwargs) -> HttpResponse:
            ...


    # Initializing the HTTP client in your own way
    http_client = CustomHttpClient(...)

    dsw_sdk = DataStewardshipWizardSDK(
        http_client=http_client,
        logger=already_setup_logger,
    )

In the case of HTTP client, you can also pass only the class of your custom
client. It will then get instantiated with all the other config values as it
normally would. This is useful if you don't want to perform the initialization
yourself or in cases, when you want to override just one aspect of the default
HTTP client shipped with this library.

.. code-block:: python

    from dsw_sdk.http_client.requests_impl.http_client import SessionHttpClient

    class CustomHttpClient(SessionHttpClient):
        def after_request(self, response):
            ...  # Some custom logic here


    dsw_sdk = DataStewardshipWizardSDK(
        api_url='http://localhost:3000',
        email='albert.einstein@example.com',
        http_client=CustomHttpClient,
    )

For a complete list of all possible configuration values, see
:ref:`configuration values <config_values>`.
