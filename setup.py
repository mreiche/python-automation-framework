from pathlib import Path

from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="python-automation-framework",
    description="Automation framework for the WebDriver API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.7",
    url="https://github.com/mreiche/python-automation-framework",
    author="Mike Reiche",
    packages=["paf"],
    install_requires=["inject>=4.3.1", "selenium>=4.8.3", "is-empty>=1.0.1"],
)
