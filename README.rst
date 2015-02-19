=====================
django-excel-response
=====================

This is an overhaul of https://pypi.python.org/pypi/django-excel-response which was originally http://djangosnippets.org/snippets/1151/
Author is Daniel Petrikin.

A subclass of HttpResponse which will transform a QuerySet,
or sequence of sequences, into either an Excel spreadsheet or
CSV file formatted for Excel, depending on the amount of data.
All of this is done in-memory and on-the-fly, with no disk writes,
thanks to the StringIO library.

Installation
============

::

    pip install excel_response xlwt


Usage
=====

::

    from excel_response3 import ExcelResponse

    def excelview(request):
        objs = SomeModel.objects.all()
        return ExcelResponse(objs)


or::

    from excel_response import ExcelResponse

    def excelview(request):
        data = [
            ['Column 1', 'Column 2'],
            [1,2]
            [23,67]
        ]
        return ExcelResponse(data, 'my_data')

Constructor Kwargs
======
headers - an array containing column headers

output_name - maintaining this kwarg, but tries first to 
use the 2nd arg passed when defining the class

force_csv - forcibly respond with csv, defaults to False

encoding - defaults to 'utf8'

sheet_name - defaults to 'Sheet 1'

blanks_for_none - replace None values with '', defaults to True

auto_adjust_width - adjust width of each column automatically, defaults to True
