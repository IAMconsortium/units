Development notes
*****************

Test the package build
======================

.. code-block:: shell

   $ rm -r build dist
   $ python3 setup.py bdist_wheel sdist
   $ twine check dist/

Ensure there are no warnings from twine.


Generated data files
====================
Update these files using the command::

    $ python -m iam_units.update emissions

The files contain a notice that they should not be edited manually.
