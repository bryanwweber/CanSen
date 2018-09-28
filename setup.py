"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

version = {}
with open('cansen/_version.py', mode='r') as version_file:
    exec(version_file.read(), version)

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), mode='r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CanSen',
    version=version['__version__'],
    description='CanSen: A script to run 0-D simulations using Cantera',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bryanwweber/CanSen',
    author='Bryan W. Weber',
    author_email='bryan.w.weber@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='experiments chemistry',
    packages=find_packages(exclude=['docs']),
    install_requires=[
        'cantera>=2.2,<3.0',
        'numpy>=1.8.1,<2.0',
        'tables>=3.1.1,<4.0',
    ],
    python_requires='~=3.4',
    package_data={
        'cansen': ['README.md', 'LICENSE.txt'],
    },
    entry_points={
        'console_scripts': [
            'cansen=cansen.__main__:main',
        ],
    },
)
