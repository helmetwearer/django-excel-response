#!/usr/bin/env python
from distutils.core import setup

version='1.0'

setup(
    name='django-excel-response3',
    version=version,
    author='Dan Petrikin',
    author_email='dan@pydojo.com',
    packages=['excel_response3'],

    url='http://github.com/danpetrikin/django-excel-response/',
    download_url = 'https://github.com/danpetrikin/django-excel-response/tarball/1.0',
    description = """A subclass of HttpResponse which will transform a QuerySet,
or sequence of sequences, into either an Excel spreadsheet or
CSV file formatted for Excel, depending on the amount of data.

http://github.com/danpetrikin/django-excel-response/
""",

    long_description = open('README.rst').read(),

    requires = ['xlwt'],
    keywords = ['excel','django'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',

    ],
)
