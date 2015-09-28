import datetime
import re
import csv
import xlwt
try:
    from StringIO import StringIO
except:
    from io import StringIO
    
from django.db.models.query import QuerySet, ValuesQuerySet
from django.http import HttpResponse

def strip_non_ascii(string):
    if isinstance(string, basestring):
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)
    return string

class ExcelResponse(HttpResponse):

    ROW_LIMIT = 655365

    # Make sure we've got the right type of data to work with
    @property
    def cleaned_data(self):
        if isinstance(self.data, ValuesQuerySet):
            self.data = list(self.data)
        elif isinstance(self.data, QuerySet):
            self.data = list(self.data.values())
        if hasattr(self.data, '__getitem__'):
            if isinstance(self.data[0], dict):
                if self.headers is None:
                    self.headers = self.data[0].keys()
                self.data = [
                    [row[col] for col in self.headers]
                    for row in self.data
                ]
                self.data.insert(0, self.headers)
            if hasattr(self.data[0], '__getitem__'):
                return True
        return False

    @property
    def as_xls(self):
        output = StringIO()
        book = xlwt.Workbook(encoding=self.encoding,style_compression=2)
        sheet = book.add_sheet(self.sheet_name)

        styles = {
            'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
            'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
            'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
            'default': xlwt.Style.default_style,
            'currency': xlwt.easyxf(num_format_str='[$$-409]#,##0.00;-[$$-409]#,##0.00')
        }
        widths = {}
        for rowx, row in enumerate(self.data):
            for colx, value in enumerate(row):
                if value is None and self.blanks_for_none:
                    value = ''

                if self.is_user_defined_class(value):
                    value = str(value)

                cell_style = styles['default']
                if type(value).__name__ in styles:
                    cell_style = styles[type(value).__name__]

                elif isinstance(value, basestring):
                    leading_zero_number_regex = re.compile(
                        r'^-?[0]+[0-9,]*$'
                    )
                    
                    comma_separated_number_regex = re.compile(
                        r'^-?[0-9,]*\.[0-9]*$')
                    dollar_regex = re.compile(r'^\$[0-9,\.]+$')
                    
                    if leading_zero_number_regex.match(value):
                        cell_style = xlwt.easyxf(num_format_str='0'*len(value))
                    elif comma_separated_number_regex.match(value) and value != '-':
                        value = float(value.replace(',', ''))
                        if len(str(value)) > 15:
                            value = str(value)
                            cell_style = xlwt.easyxf(num_format_str='0'*len(value))
                    elif dollar_regex.match(value) and value != '-':
                        value = float(value.replace(',', '').replace('$', ''))
                        cell_style = styles['currency']

                sheet.write(rowx, colx, value, style=cell_style)
                if self.auto_adjust_width:
                    if isinstance(value, basestring):
                        width = len(value) * 256
                    else:
                        width = len(str(value)) * 256
                    if width > widths.get(colx, 0):
                        if width > self.ROW_LIMIT:
                            width = self.ROW_LIMIT
                        widths[colx] = width
                        sheet.col(colx).width = width
        book.save(output)
        return output

    @property
    def as_csv(self):
        output = StringIO()
        writer = csv.writer(output)
        for row in self.data:
            writer.writerow([strip_non_ascii(item) for item in row])
        return output

    def is_user_defined_class(self, inst):
        cls = inst.__class__
        if hasattr(cls, '__class__'):
            return ('__dict__' in dir(cls) or hasattr(cls, '__slots__'))
        return False

    def __init__(self, *args, **kwargs):

        self.data = args[0]
        try:
            self.output_name = args[1].replace('"', '\"')
        except IndexError:
            self.output_name = kwargs.pop(
                'output_name', 'excel_data').replace('"', '\"')
        self.headers = kwargs.pop('headers', None)
        self.force_csv = kwargs.pop('force_csv', False)
        self.encoding = kwargs.pop('encoding', 'utf8')
        self.sheet_name = kwargs.pop('sheet_name', 'Sheet 1')
        self.blanks_for_none = kwargs.pop('blanks_for_none', True)
        self.auto_adjust_width = kwargs.pop('auto_adjust_width', True)

        assert self.cleaned_data is True, "ExcelResponse requires a sequence of sequences"

        # Excel has a limit on number of rows; if we have more than that, make
        # a csv
        if len(self.data) <= self.ROW_LIMIT and not self.force_csv:
            output = self.as_xls
            mimetype = 'application/vnd.ms-excel'
            file_ext = 'xls'
        else:
            output = self.as_csv
            mimetype = 'text/csv'
            file_ext = 'csv'
        output.seek(0)
        super(ExcelResponse, self).__init__(
            content=output.getvalue(), content_type=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % (
            self.output_name,
            file_ext
        )
