Development notes
*****************

Test the package build
======================

.. code-block:: shell

   $ rm -r build dist
   $ python3 setup.py bdist_wheel sdist
   $ twine check dist/

Ensure there are no warnings from twine.
