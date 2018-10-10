#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

__version__ = '1.5.0'
__repo__ = 'http://gitlab.rbs.com.br/rbsdev/classification_tree'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='classification_tree',
    version=__version__,
    description='Package to lead with classifications-api',
    long_description=read("README.rst"),
    author='Luis Fernando Gomes',
    author_email='luiscoms@ateliedocodigo.com.br',
    url=__repo__,
    download_url='{}/tarball/{}'.format(__repo__, __version__),
    packages=find_packages(exclude=('tests', 'docs')),
    zip_safe=False,
    include_package_data=True,
    licence="MIT",
    plataforms="any",
    install_requires=[
        "requests"
    ],
)
