chaostoolkit-wiremock
=====================

[![Build Status](https://travis-ci.com/chaostoolkit-incubator/chaostoolkit-wiremock.svg?branch=master)](https://travis-ci.com/chaostoolkit-incubator/chaostoolkit-wiremock)
[![image](https://img.shields.io/pypi/v/chaostoolkit-wiremock.svg)](https://pypi.python.org/pypi/chaostoolkit-wiremock)

[Chaos Toolkit][chaostoolkit] driver for [WireMock][wiremock]. 

[chaostoolkit]: http://chaostoolkit.org
[wiremock]: http://wiremock.org/

Package installation
--------------------

To install the package from pypi.org:

    pip install -U chaostoolkit-wiremock

Installation from source
------------------------

In order to use it, you need python 3.5+ in your environment.
Once downloaded the project, cd into it and run:

    pip install -r requirements.txt -r requirements-dev.txt
    make clean && make test && make install

Configuration
-------------

The following keys can be configured in the experiment global
configuration section, under the \"wiremock\" key:

-   **host**: the wiremock server host
-   **port**: the wiremock server port
-   **contextPath**: the contextPath for your wiremock server (optional)
-   **timeout**: accepted timeout (defaults to 1 sec)
-   **down**: the delayDistribution section used by the `down` action

Configuration example:

    {
        "configuration": {
            "wiremock": {
                "host": "localhost",
                "port": 8080,
                "contextPath": "/wiremock",
                "timeout": 10,
                "down": {
                    "type": "lognormal",
                    "median": 3000,
                    "sigma": 0.2
                }
            }
        }
    }

Exported Actions
----------------

Adding a list of mappings:

    {
      "method": [
        {
          "type": "action",
          "name": "adding a mapping",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "add_mappings",
            "arguments": {
              "mappings": [{
                "request": {
                   "method": "GET",
                   "url": "/hello"
                },
                "response": {
                   "status": 200,
                   "body": "Hello world!",
                   "headers": {
                       "Content-Type": "text/plain"
                   }
                } 
              }]
            }
          }
        }
      ]
    }

Deleting a list of mappings:

    {
      "method": [
        {
          "type": "action",
          "name": "deleting a mapping",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "delete_mappings",
            "arguments": {
              "filter": [{
                 "method": "GET",
                 "url": "/hello"
              }]
            }
          }
        }
      ]
    }

Adding a global fixed delay:

    {
      "method": [
        {
          "type": "action",
          "name": "Adding a global fixed delay",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "global_fixed_delay",
            "arguments": {
              "fixedDelay": 10
            }
          }
        }
      ]
    }

Adding a global random delay:

    {
      "method": [
        {
          "type": "action",
          "name": "Adding a global random delay",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "global_random_delay",
            "arguments": {
              "delayDistribution": {
                "type": "lognormal",
                "median": 20,
                "sigma": 0.1
              }
            }
          }
        }
      ]
    }

Adding a fixed delay to a list of mappings:

    {
      "method": [
        {
          "type": "action",
          "name": "Adding a fixed delay to a mapping",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "fixed_delay",
            "arguments": {
              "filter": [{
                "method": "GET",
                "url": "/hello1"
              }],
              "fixedDelayMilliseconds": 1000
            }
          }
        }
      ]
    }

Adding a random delay to a list of mappings:

    {
      "method": [
        {
          "type": "action",
          "name": "Adding a random delay to a mapping",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "random_delay",
            "arguments": {
              "filter": [{
                "method": "GET",
                "url": "/hello2"
              }],
              "delayDistribution": {
                "type": "lognormal",
                "median": 2000,
                "sigma": 0.5
              }
            }
          }
        }
      ]
    }

Adding a ChunkedDribbleDelay to a list of mappings:

    {
      "method": [
        {
          "type": "action",
          "name": "Adding a ChunkedDribbleDelay to a mapping",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "chunked_dribble_delay",
            "arguments": {
              "filter": [{
                "method": "GET",
                "url": "/hello"
              }],
              "chunkedDribbleDelay": {
                "numberOfChunks": 5,
                "totalDuration": 1000
              }
            }
          }
        }
      ]
    }

Taking a list of mappings down (heavy distribution delay). This action
will use the parameters specified in the \"down\" key of the
configuration section:

    {
      "method": [
        {
          "type": "action",
          "name": "Taking a mapping down",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "down",
            "arguments": {
              "filter": [{
                "method": "GET",
                "url": "/hello"
              }]
            }
          }
        }
      ]
    }

Taking a list of mappings up back again:

    {
      "method": [
        {
          "type": "action",
          "name": "Taking a mapping down",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "up",
            "arguments": {
              "filter": [{
                "method": "GET",
                "url": "/hello"
              }]
            }
          }
        }
      ]
    }

Resetting the wiremock server (deleting all mappings):

    {
      "method": [
        {
          "type": "action",
          "name": "Taking a mapping down",
          "provider": {
            "type": "python",
            "module": "chaoswm.actions",
            "func": "reset"
          }
        }
      ]
    }


### Experiments

The driver comes with an experiments directory where you can find snippets to test all APIs 
against a WireMock server listening on localhost:8080.


### Discovery

You may use the Chaos Toolkit to discover the capabilities of this
extension:

    $ chaos discover chaostoolkit-wiremock  --no-install

Credits
-------

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
