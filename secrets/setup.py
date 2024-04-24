import os
cwd = os.getcwd()
from distutils.core import setup
from Cython.Build import cythonize
 
setup(ext_modules=cythonize([f"{cwd}/secrets/essential_tokens.py"]))
