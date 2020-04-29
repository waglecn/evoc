from setuptools import setup, find_packages
import sys
import os

version = '0.1'

setup(
    name='evoc',
    version=version,
    description="A tool to study the evolution of gene clusters",
    long_description="""\
        """,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords='',
    author='Nicholas Waglechner',
    author_email='waglecn@mcmaster.ca',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_data={
        'evoc': [
            '../basic_types.tsv', '../LICENSE', '../README.md',
            'bact_core_tree_building/core_hmm/*.hmm'
        ]
    },
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'setuptools',
        'configparser',
        'nose==1.3.7',
        'coverage==4.4.2',
        'progress==1.3',
        'six==1.11.0',
        'biopython==1.70',
        'ete3==3.1.1',
        'svgwrite==1.1.2',
        'pygraphviz',
        'scipy',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            "evoc = evoc.__main__:main"
        ]
    },
)
