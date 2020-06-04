"""Install h5table."""

import setuptools
import os
import re

current_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(current_dir, 'h5table', '__init__.py'), 'r') as f:
    version = re.search(r"__version__ = '([^']+)'", f.read()).group(1)

setuptools.setup(
    name='h5table',
    version=version,
    description='Simple storage of pandas dataframes in HDF5 files.',
    license='MIT',
    author='Emerson Harkin',
    author_email='emerson.f.harkin@gmail.com',
    packages=['h5table'],
    install_requires=['h5py', 'pandas', 'numpy'],
)
