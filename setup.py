"""Setup.py for small_small_hr."""
from os import path

from setuptools import find_packages, setup

# read the contents of your README file
with open(
    path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding="utf-8"
) as f:
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
    packages=find_packages(exclude=["docs", "*.egg-info", "build", "tests.*", "tests"]),
    install_requires=[
        "Django >= 2.2",
        "voluptuous",
        "psycopg2-binary",
        "sorl-thumbnail",
        "django-private-storage",
        "django-model-reviews",
        "phonenumberslite",
        "django-phonenumber-field",
        "django-crispy-forms",
        "djangorestframework",
        "sorl-thumbnail",
        "Pillow",
        "django-mptt",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
    ],
    include_package_data=True,
)
