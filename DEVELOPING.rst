Development notes
*****************

The repository and package aim to be ruthlessly simple, and thus as easy as possible to maintain.
Thus:

- No built documentation; like `pycountry <https://pypi.org/project/pycountry/>`_, the README *is* the documentation.
- Actual code (in \_\_init\_\_.py) kept to a minimum.
- `setuptools-scm <https://pypi.org/project/setuptools-scm/>`_ and git tags used for all versioning.
- Minimal CI configuration: one service/OS/Python version.
- Versioning: similar to pycountry: ``<YYYY>.<M>.<D>``.
- AUTHORS: anyone adding a commit to the repo should also add their name to AUTHORS.


Test the package build
======================

.. code-block:: shell

   $ rm -r build dist
   $ python3 setup.py bdist_wheel sdist
   $ twine check dist/

Ensure there are no warnings from twine.


Generated data files for GWP contexts
=====================================

iam_units/data/emissions/emissions.txt defines the base units for Pint, and imports the files iam_units/data/emissions/gwp\_\*.txt.
These files each define one context, and contain a notice that they should not be edited manually.

Update these files using the command::

    $ python -m iam_units.update emissions

The update submodule parses metric_conversions.csv and writes the context files.
When adding a new context file, make sure to ``@import`` it in emissions.txt and write a unit test.
