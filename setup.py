# -*- coding: utf-8 -*-
"""
@author:        Andreas Kaeberlein
@copyright:     Copyright 2021
@credits:       AKAE

@license:       GPLv3
@maintainer:    Andreas Kaeberlein
@email:         andreas.kaeberlein@web.de

@file:          setup.py
@date:          2021-01-02

@note           setup pip installer
"""



#------------------------------------------------------------------------------
# Python Libs
#
import setuptools
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='ATWG',
    version='0.1.3',
    scripts=['atwg-cli'],
    install_requires = ["pyserial", "pyyaml"],
    author='Andreas Kaeberlein',
    author_email="andreas.kaeberlein@web.de",
    license="GPLv3",
    platforms="Any",
    description="Various Temperature Waveform Generator for Climate Chambers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akaeba/ATWG",
    download_url = "https://pypi.org/project/ATWG/",
    packages=setuptools.find_packages("ATWG"),          # include all packages under ATWG
    package_dir={"": "ATWG"},                           # tell distutils packages are under src
    package_data={"ATWG": ["driver/espec/*.yml"],},     # adds .yml config files to package
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
#------------------------------------------------------------------------------
