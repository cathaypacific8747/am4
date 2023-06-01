from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("helper_cy.pyx", annotate=True, language_level=3)
)