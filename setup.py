"""
Setup.py for small_small_hr
"""
from os import path

from setuptools import find_packages, setup

# read the contents of your README file
with open(
        path.join(path.abspath(path.dirname(__file__)), "README.md"),
        encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="small-small-hr",
    version=__import__("small_small_hr").__version__,
    description="Minimal human resource management app for Django",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Kelvin Jayanoris",
    author_email="kelvin@jayanoris.com",
    url="https://github.com/moshthepitt/small-small-hr",
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=[
        "Django >= 2.0.11",
        "voluptuous",
        "psycopg2-binary",
        "sorl-thumbnail",
        "django-private-storage",
        "phonenumberslite",
        "django-phonenumber-field",
        "django-crispy-forms",
        "djangorestframework",
        "sorl-thumbnail",
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
    ],
)
