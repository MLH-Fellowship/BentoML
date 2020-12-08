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

The `bentoml config view` command checks if `BENTOML_CONFIG` is defined as an environment variable.
`BENTOML_CONFIG` is used to specify the path of a local config file for customizing bentoml.
If no such env var exists, it returns the default BentoML configurations, with the base path as `BENTOML_HOME`, containing the file - `bentoml.cfg`.

If not specified by the user, `BENTOML_HOME` has `~/bentoml` as its default path. BentoML also ships with a default configuration file present at ``bentoml/configuration/default_bentoml.cfg` <https://github.com/bentoml/BentoML/blob/master/bentoml/configuration/default_bentoml.cfg>`_. Internally, this config file is stored in `DEFAULT_CONFIG_FILE` variable, which can be accessed as -
.. code-block:: python

    import bentoml.configuration as config
    config.DEFAULT_CONFIG_FILE

The `bentoml config view-effective` command can be used to view the local config overrides of the default configuration. Calling `view-effective` is ideally equivalent to calling - 
.. code-block:: python

    import bentoml.configuration as config
    config.config(section=None)

The above `config.config() method <https://github.com/bentoml/BentoML/blob/master/bentoml/configuration/__init__.py>`_ internally checks whether `BENTOML_HOME` exists or not. If it does, then it stores the contents of `DEFAULT_CONFIG_FILE`. It then checks if any local config file is present, if yes, it overwrites the default with the same. Users can specify a local config file using the above mentioned `BENTOML_CONFIG` env variable.