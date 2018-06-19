"""
Setup.py for small_small_hr
"""
from setuptools import setup, find_packages

setup(
    name='small-small-hr',
    version='0.0.2',
    description='Minimal human resource management app for Django',
    license='MIT',
    author='Kelvin Jayanoris',
    author_email='kelvin@jayanoris.com',
    url='https://github.com/moshthepitt/small-small-hr',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'Django >= 1.11',
        'voluptuous',
        'psycopg2-binary',
        'sorl-thumbnail',
        'django-private-storage',
        'django-phonenumber-field',
        'django-crispy-forms',
        'djangorestframework'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],
)
