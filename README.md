[![Static analysis](https://github.com/ds-wizard/dsw-sdk/actions/workflows/static_analysis.yml/badge.svg?branch=master)](https://github.com/ds-wizard/dsw-sdk/actions/workflows/static_analysis.yml)
[![Tests](https://github.com/ds-wizard/dsw-sdk/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/ds-wizard/dsw-sdk/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/dsw-sdk/badge/?version=latest)](https://dsw-sdk.readthedocs.io/en/latest/?badge=latest)

# DSW SDK


## Introduction

This projects aims at providing unified and easy-to-use Python library for
communicating with the Data Stewardship Wizard API. For more info about
the DSW project itself, see [official webpage](https://ds-wizard.org/) or the 
[API documentation](https://api.demo.ds-wizard.org/swagger-ui/).


## Installation

You can install this library via PyPI:

```commandline
pip install dsw-sdk
```


## Quickstart

The only mandatory step need in order to get going is to initialize the whole
SDK and tell it, where is the DSW API located and how to connect to it:

```python
from dsw_sdk import DataStewardshipWizardSDK


dsw_sdk = DataStewardshipWizardSDK(
    api_url='http://localhost:3000',
    email='albert.einstein@example.com',
    password='password',
)
```

Now you are ready to go.

> Note that this is only *illustrative example* and we
encourage you **not** to store secrets like passwords in the source code.
There are better mechanisms (env variables) introduced in the docs.


## Basic usage

Most actions should be done via the high-level interfaces provided on an 
instance of the `DataStewardshipWizardSDK` class. These interfaces operate with 
subclasses of `Model` class (e.g. `user.User`) -- these are the DSW data 
entities. Basically they are just data classes with bunch of attributes and 
methods for saving the entity (`save()`) on the server and deleting it
(`delete()`).

```python
import os


user = dsw_sdk.users.create_user(
   first_name='John',
   last_name='Doe',
   email='john.doe@example.com',
)
user.password = os.getenv('SECRET_PASSWORD')
user.save()

...

user.delete()
```

For more advanced usage, see the [docs](https://dsw-sdk.readthedocs.io/en/latest/).
