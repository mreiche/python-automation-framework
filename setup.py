import os
from pathlib import Path

from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = os.environ.get("PACKAGE_VERSION", "0.0.1")

setup(
    name="python-automation-framework",
    description="Automation framework for the WebDriver API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
    url="https://github.com/mreiche/python-automation-framework",
    author="Mike Reiche",
    packages=["paf"],
    install_requires=["inject>=4.3.1", "selenium>=4.23.1", "is-empty>=1.0.1"],
    python_requires=">=3.13",
    license_files=("LICENSE.txt", )
)
