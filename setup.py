"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from pathlib import Path
from typing import Dict

HERE = Path(__file__).parent

version: Dict[str, str] = {}
with (HERE / "cansen" / "_version.py").open(mode="r") as version_file:
    exec(version_file.read(), version)

# Get the long description from the relevant file
long_description = (HERE / "README.md").read_text()

setup(
    name="CanSen",
    version=version["__version__"],
    description="CanSen: A script to run 0-D simulations using Cantera",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bryanwweber/CanSen",
    author="Bryan W. Weber",
    author_email="bryan.w.weber@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="experiments chemistry",
    packages=find_packages(exclude=["docs"]),
    install_requires=["cantera>=2.2,<3.0", "numpy>=1.8.1,<2.0", "tables>=3.1.1,<4.0"],
    python_requires="~=3.6",
    package_data={"cansen": ["README.md", "LICENSE.txt"]},
    entry_points={"console_scripts": ["cansen=cansen.__main__:main"]},
)
