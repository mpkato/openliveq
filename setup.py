# -*- coding:utf-8 -*-
from setuptools import setup

setup(
    name = "openliveq",
    packages = ["openliveq", "openliveq.nlp", "openliveq.features"],
    version = "0.0.1",
    description = "Package for NTCIR-13 OpenLiveQ",
    author = "Makoto P. Kato",
    author_email = "kato@dl.kuis.kyoto-u.ac.jp",
    license     = "MIT License",
    url = "https://github.com/mpkato/openliveq",
    install_requires = [
        "click",
    ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'openliveq=openliveq.__main__:main'
        ]
    },
)
