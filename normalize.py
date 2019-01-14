#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Imports
import arrow
import csv
import io
import re
import sys


# In[ ]:


def to_seconds(time):
    units = [float(v) for v in time.split(':')]
    return sum((coeff * unit for coeff, unit in zip([3600, 60, 1], units)))


# In[ ]:


def to_iso8601(datetime, timezone):
    match = re.match(r'(\d\d?)/(\d\d?)/(\d\d?) (\d\d?)(.*)', datetime)
    time = arrow.get('20{2:0>2}-{0:0>2}-{1:0>2}T{3:0>2}{4} {5}'.format(*match.groups(), 'US/Pacific'), 'YYYY-MM-DDTHH:ss:mm A ZZZ')
    return time.to(timezone).format('YYYY-MM-DDTHH:mm:ssZZ')


# In[ ]:


to_zip = lambda x: '{0:0>5.5}'.format(x)


# In[ ]:


def normalize():
    raw = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    csv.register_dialect('truss', delimiter=',', escapechar=None, quoting=csv.QUOTE_MINIMAL)
    reader = csv.DictReader(raw)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        # Timestamp : to ISO-8601 format in US/Eastern timezone
        try:
            row['Timestamp'] = to_iso8601(row['Timestamp'], 'US/Eastern')
        except AttributeError:
            sys.stderr.write('WARNING: row {0}\ndropped while normalizing timestamp due to error.'.format(list(row.values())))
            continue
        # Address : no changes
        # ZIP : limit to 5 digits, prefix with 0
        row['ZIP'] = to_zip(row['ZIP'])
        # FullName : to uppercase
        row['FullName'] = row['FullName'].upper()
        # FooDuration, BarDuration : HH:MM:SS.MS format to seconds (float)
        row['FooDuration'] = to_seconds(row['FooDuration'])
        row['BarDuration'] = to_seconds(row['BarDuration'])
        # TotalDuration : replace with sum of FooDuration and BarDuration
        row['TotalDuration'] = row['FooDuration'] + row['BarDuration']
        # Notes : no changes
        writer.writerow(row)


# In[ ]:


if __name__ == "__main__":
    normalize()


# In[ ]:




