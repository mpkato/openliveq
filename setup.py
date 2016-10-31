# -*- coding:utf-8 -*-
from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

setup(
    name = "openliveq",
    packages = ["openliveq"],
    version = "0.0.1",
    description = "Package for NTCIR-13 OpenLiveQ",
    author = "Makoto P. Kato",
    author_email = "kato@dl.kuis.kyoto-u.ac.jp",
    license     = "MIT License",
    url = "https://github.com/mpkato/openliveq",
    install_requires = [
        'numpy'
    ],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest}
)
