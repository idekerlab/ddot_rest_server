===========
fake_cytoscapesearch
===========


.. image:: https://img.shields.io/pypi/v/fake_cytoscapesearch.svg
        :target: https://pypi.python.org/pypi/fake_cytoscapesearch

.. image:: https://img.shields.io/travis/coleslaw481/fake_cytoscapesearch.svg
        :target: https://travis-ci.org/coleslaw481/fake_cytoscapesearch




Fake Enrichment REST service

`For more information please click here to visit our wiki <https://github.com/coleslaw481/fake_cytoscapesearch/wiki>`_


Compatibility
-------------

 * Tested with Python 3.6 in Anaconda_

Dependencies to run
-------------------

 * `flask <https://pypi.org/project/flask/>`_
 * `flask-restplus <https://pypi.org/project/flast-restplus>`_

Additional dependencies to build
--------------------------------

 * GNU make
 * `wheel <https://pypi.org/project/wheel/>`_
 * `setuptools <https://pypi.org/project/setuptools/>`_
 

Installation
------------

It is highly reccommended one use `Anaconda <https://www.anaconda.com/>`_ for Python environment

.. code:: bash

  git clone https://github.com/coleslaw481/fake_cytoscapesearch.git
  cd fake_cytoscapesearch
  make install

Running service in development mode
----------------------------------


**NOTE:** Example below runs the REST service and not the task runner.

.. code:: bash

  # It is assumed the application has been installed as described above
  export FLASK_APP=fake_cytoscapesearch
  flask run # --host=0.0.0.0 can be added to allow all access from interfaces
  
  # Service will be running on http://localhost:5000



`Click here for information on launching service via Vagrant VM <https://github.com/coleslaw481/fake_cytoscapesearch/wiki/NAGA-REST-under-Vagrant-Virtual-Machine>`_


Example usage of service
------------------------

TODO

.. code:: bash
   
    TODO

Bugs
-----

Please report them `here <https://github.com/coleslaw481/fake_cytoscapesearch/issues>`_

Acknowledgements
----------------


* Initial template created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Anaconda: https://www.anaconda.com/
