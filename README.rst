Django ESUtils
==============

Common and easy way to manage ES backend in django based on elasticutils and
elasticsearch-py.

Hacking
-------

In order to hack on django-esutils, you'll need to set at least an Elasticsearch
instance available from your machine.

You can install it manually or more simply, use a docker container like this::

    docker run --net host dockerfile/elasticsearch

and then you can browse your ES server at: http://127.0.0.1:9200/

Configuration
~~~~~~~~~~~~~

add a :file:`local_settings.py` file in your :file:`demo/demo_esutils` directory,
with these settings:

.. code-block:: python

    ES_URLS = [
        'http://127.0.0.1:9200',
    ]

(or change it to fit your ES target configuration)

Running tests
~~~~~~~~~~~~~


Now that your ES instance is ready, and your database connection set, simply run
the tests using tox, preferrably in a virtualenv::

    mkvirtualenv TOX
    pip install tox
    tox
