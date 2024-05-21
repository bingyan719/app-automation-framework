import sys
from setuptools import setup, find_packages


def parse_requirements(filename):
    """ load requirements from a pip requirements file. (replacing from pip.req import parse_requirements)"""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


reqs = parse_requirements('requirements.txt')


setup(
    name='ui.automation',
    version='1.0.0',
    author='Viking Den',
    author_email='icyiy123889@ABCD.com.cn',
    description='UI Test Automation Framework for Apps on Android/iOS',
    long_description='UI Test Automation Framework for Apps on Android/iOS',
    url='',
    license='Apache License 2.0',
    keywords=['automation', 'automated-test', 'app', 'android', 'ios'],
    packages=find_packages(exclude=['cover', 'playground', 'tests', 'dist']),
    install_requires=reqs,
    entry_points="""
                [console_scripts]
                ui.test = ui.cli.__main__:main
                """,
    classifiers=[
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)