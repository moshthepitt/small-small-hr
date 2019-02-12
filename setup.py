"""
Setup.py for small_small_hr
"""
from setuptools import setup, find_packages

setup(
    name='small-small-hr',
    version=__import__('small_small_hr').__version__,
    description='Minimal human resource management app for Django',
    license='MIT',
    author='Kelvin Jayanoris',
    author_email='kelvin@jayanoris.com',
    url='https://github.com/moshthepitt/small-small-hr',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'Django >= 2.0.11',
        'voluptuous',
        'psycopg2-binary',
        'sorl-thumbnail',
        'django-private-storage',
        'phonenumberslite',
        'django-phonenumber-field',
        'django-crispy-forms',
        'djangorestframework',
        'sorl-thumbnail',
        'Pillow'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],
)
