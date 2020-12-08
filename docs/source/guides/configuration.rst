Configuring BentoML
===================

Many aspects of BentoML such as the YataiService, logging, and API server can easily be configured by using environment variables or updating a config file. BentoML is using a hierarchical configuration module built using the configparser module packaged in Python's standard library.
Ideally, BentoML checks for a specific configuration in the following manner:

* **Environment Variables** (first checked for, has the highest priority)
* **User config file**
* **Default config file** (last checked for, has the lowest priority)

1. Viewing configurations
=========================
To view your configurations, use the following commands:

.. code-block:: bash

    bentoml config view
    bentoml config view-effective

The :code:`bentoml config view` command checks if :code:`BENTOML_CONFIG` is defined as an environment variable.
:code:`BENTOML_CONFIG` is used to specify the path of a local config file for customizing BentoMl.
If no such env var exists, it returns the default BentoML configurations, with the base path as :code:`BENTOML_HOME`, containing the file - :code:`bentoml.cfg`.

If not specified by the user, :code:`BENTOML_HOME` has :code:`~/bentoml` as its default path. BentoML also ships with a default configuration file present at `bentoml/configuration/default_bentoml.cfg <https://github.com/bentoml/BentoML/blob/master/bentoml/configuration/default_bentoml.cfg>`_. Internally, this config file is stored in :code:`DEFAULT_CONFIG_FILE` variable, which can be accessed as -

.. code-block:: python

    import bentoml.configuration as config
    config.DEFAULT_CONFIG_FILE

The :code:`bentoml config view-effective` command can be used to view the local config overrides of the default configuration. Calling :code:`view-effective` is ideally equivalent to calling - 

.. code-block:: python

    import bentoml.configuration as config

    # Some of the default sections (as seen in DEFAULT_CONFIG_FILE path) are - 
    # core, instrument, logging, tracing, yatai_service, apiserver, etc.
    # See bentoml/configuration/default_bentoml.cfg for complete configuration
    config.config(section=None)

The above `config.config() method <https://github.com/bentoml/BentoML/blob/master/bentoml/configuration/__init__.py>`_ internally checks whether :code:`BENTOML_HOME` exists or not. If it does, then it stores the contents of :code:`DEFAULT_CONFIG_FILE`. It then checks if any local config file is present, if yes, it overwrites the default with the same. Users can specify a local config file using the above mentioned :code:`BENTOML_CONFIG` env variable.

2. Setting configurations
=========================
In BentoML, configurations can be set in different ways -

Using :code:`bentoml config set`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Example:

.. code-block:: bash

    # for "core" section:
    bentoml config set usage_tracking=false

    # for "yatai_service" section:
    bentoml config set yatai_service.url=127.0.0.1:50051

BentoML follows a :code:`section.item` format for updating any configuration using :code:`set`. In the above examples, :code:`yatai_service` is a section, whereas :code:`usage_tracking` and :code:`url` are items. While setting a config value, if no section is specified, BentoML defaults to :code:`core` section.

This command can be used for your development machines, and it will remember your settings on a local file (:code:`~/bentoml/bentoml.cfg` by default).

Using Python
^^^^^^^^^^^^
If you only need to set the config one time for a single Python session, without persisting the config to your local file, set the config via :code:`bentoml.config` in Python:

.. code-block:: python

    from bentoml import config
    config().set('core', 'usage_tracking', 'False')
    config().set('yatai_service', 'url', '127.0.0.1:50051')

In the above examples, :code:`set` can be interpreted as :code:`set(section, item, new_value)`.

Using Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can also use environment variables if you are using BentoML cli commands or don't want to change the Python code, for example:

.. code-block:: bash

     $ BENTOML__YATAI_SERVICE__URL=127.0.0.1:50051 python guides/quick-start/main.py
     $ BENTOML__YATAI_SERVICE__URL=127.0.0.1:50051 bentoml get IrisClassifier:latest

3. Additional Comments
======================

* BentoML implicitly supports expanding of nested environment variables. It does this by repeatedly expanding shell variables of form :code:`$var` and :code:`${var}` and by expanding :code:`~` and :code:`~user` constructions. For the former, unknown variables are left unchanged, whereas for the latter if :code:`user` or :code:`$HOME` is unknown, it does nothing.