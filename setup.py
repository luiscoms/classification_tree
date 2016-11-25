#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = '0.0.0'
__repo__ = 'http://gitlab.rbs.com.br/rbsdev/classification_tree'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='classification_tree',
    version=__version__,
    description='Pachage to lead with classifications-api',
    long_description=readme,
    author='Luis Fernando Gomes',
    author_email='luiscoms@ateliedocodigo.com.br',
    url=__repo__,
    download_url='{}/tarball/{}'.format(__repo__, __version__),
    locence=license,
    keywords=[],
    classifiers=[],
    packages=find_packages(exclude=('tests', 'docs'))
)
