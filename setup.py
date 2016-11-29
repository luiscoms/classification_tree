#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pip.req import parse_requirements
from setuptools import setup, find_packages

__version__ = '0.0.0'
__repo__ = 'http://gitlab.rbs.com.br/rbsdev/classification_tree'


install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

with open('README.md') as f:
    readme = f.read()

setup(
    name='classification_tree',
    version=__version__,
    description='Pachage to lead with classifications-api',
    long_description=readme,
    author='Luis Fernando Gomes',
    author_email='luiscoms@ateliedocodigo.com.br',
    url=__repo__,
    download_url='{}/tarball/{}'.format(__repo__, __version__),
    install_requires=reqs,
    licence='MIT',
    keywords=[],
    classifiers=[],
    packages=find_packages(exclude=('tests', 'docs'))
)
