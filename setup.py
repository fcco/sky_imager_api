try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='sky_imager_api',
    version='0.2.0',
    description='Package with useful tools to handle Vivotek fisheye cameras',
    long_description=long_description + '\n\n' + history,
    url='https://gitlab.uni-oldenburg.de/camera',
    author='Thomas Schmidt',
    author_email='t.schmidt@uni-oldenburg.de',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Sky Imager community',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='skyimager clouds camera photovoltaic forecast',
    packages=[''],
    package_dir={'':'src'},
    install_requires=['Pillow']
    )
