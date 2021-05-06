Low-level API
#############

In case the SDK does not yet support a functionality of the DSW API that you
would like to use, you can use the low-level interface. Basically it only
provides a way to communicate with the DSW API, so you don't have to implement
your own HTTP client.

Configuration described in the :doc:`config` section still applies.

The interface is available via :attr:`~sdk.DataStewardshipWizardSDK.api`
attribute defined on the :class:`~sdk.DataStewardshipWizardSDK` class.

.. code-block:: python

   dsw_sdk = DataStewardshipWizardSDK(...)
   dsw_sdk.api.get_document_download('some-doc-uuid-1')

It provides a function for every combination of endpoint and HTTP method. So
for example ``GET`` method on endpoint ``/documents/{docUuid}/download`` is
equivalent to a :meth:`~api.LowLevelAPI.get_document_download` method.

.. code-block:: python
    :caption: Example of low-level API implementation

    def post_documents(self, body: Dict[str, Any], **kwargs) -> HttpResponse:
        body = self._camelize_dict_keys(body)
        return self._http_client.post(f'/documents', body=body, **kwargs)

    def delete_document(self, doc_uuuid: str, **kwargs) -> HttpResponse:
        return self._http_client.delete(f'/documents/{doc_uuuid}', **kwargs)

    def get_document_download(self, doc_uuid: str, **kwargs) -> HttpResponse:
        return self._http_client.get(f'/documents/{doc_uuid}/download', **kwargs)

Each method on the interface has same path parameters as the endpoint itself.
If endpoint expects query parameters or a body inside the request, the method
also takes ``query_params`` or ``body`` arguments respectively.

.. code-block:: python

    # Get 10 documents with 'test' query
    docs = dsw_sdk.api.get_documents(query_params={'q': 'test', 'size': 10})

    # Create a user
    user = dsw_sdk.api.post_users(body={'firstName': 'John', ...})


Each method also accepts arbitrary keyword arguments that are passed to the
underlying implementation of the HTTP client. Therefore you can customize each
request as you will.

.. code-block:: python

    # Never timeout - waiting indefinitely (argument
    # `timeout` is passed to the Requests `get` method)
    dsw_sdk.api.get_documents(timeout=None)

Also note, that each method's name is slightly modified to reflect whether it's
dealing with one or multiple entities. E.g. ``get_documents`` for retrieving
multiple documents vs. ``get_document_download`` for downloading one document
(although both methods use the ``documents`` endpoint).

Both ``query_params`` and ``body`` arguments keys are converted to camelCase,
so you can define these in the snake_case.

.. code-block:: python

    # Both of these are equal
    dsw_sdk.api.post_users(body={'firstName': 'John', ...})
    dsw_sdk.api.post_users(body={'first_name': 'John', ...})
