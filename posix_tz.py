# https://github.com/clach04/py-posix_tz
# NOTE short names for space reasons
"""
time.time() is int on esp32 Micropython, float in CPython
time.localtime() is tuple in Micropython, struct/class/namedtuple in CPython (3.x) with different attributes
"""

from collections import namedtuple
import re
import time


m_tuple = namedtuple('m', ('month', 'occur', 'day', 'hour', 'min', 'sec'))
def parse_mstr(s):
    if s[0] != 'M':
        raise NotImplemented('non-M %s not supported' % s[0])  # e.g. Julian
    ss = s.split('/')
    m = ss[0]
    if len(ss) == 2:
        t = s[1]
    else:
        t = '2:00:00'
    month, occur, day = map(int, m[1:].split('.'))  # TODO catch non-int errors
    h, min, sec = map(int, t.split(':'))  # TODO catch non-int errors
    return m_tuple(month, occur, day, h, min, sec)

name_offset_re = re.compile(r"^([A-Z]+)([+-]?)(\d+)(?::(\d+))?(?::(\d+))?")  # TODO revisit this
# timezone details tuple
tzd_tuple = namedtuple('tzd', ('name', 'offset', 'dst_name', 'start', 'end', 'dst_offset'))  # offsets are seconds
def parse_tz(s):
    #import pdb; pdb.set_trace()
    if s.upper() in ('UTC', 'GMT', 'GMT0', 'GMT-0', 'GMT+0'):
        return tzd_tuple('UTC', 0, None, None, None, None)
    elif s in ('PST8PDT,M3.2.0,M11.1.0', 'PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00'):
        return tzd_tuple('PST8PDT', 8 * 60 * 60, 'PDT', parse_mstr('M3.2.0'), parse_mstr('M11.1.0'), 9 * 60 * 60)
    else:
        ss = s.split(',')
        if len(ss) == 1:
            # no DST
            #import pdb; pdb.set_trace()
            x = re.match(name_offset_re, s)
            #tzname, sign, d_hour, d_min, d_sec = re.match(name_offset_re, s).groups(default=0)  # Cpython
            tzname, sign, d_hour, d_min, d_sec = x.group(1), x.group(2), x.group(3) or 0, x.group(4) or 0, x.group(5) or 0  # micropython
            offset = (int(d_hour) * 60 + int(d_min)) * 60 + int(d_sec)
            timezone = offset * (1 if sign == "-" else -1)
            return tzd_tuple(tzname, timezone, None, None, None, None)
        else:
            NotImplementedError('FIXME for %r)' %s)
    raise NotImplementedError('for %r (or potentially a bad value...)' %s)

def determine_change(p, year):
    """
    Mm.n.d format, where:

        Mm (1-12) for 12 months
        n (1-5) 1 for the first week and 5 for the last week in the month
        d (0-6) 0 for Sunday and 6 for Saturday

    For example:
        PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00
    
      * PST8PDT
      * M3.2.0/2:00:00
          * 3 - March
          * 2 - 2nd week
          * 0 - Sunday
          * 2:00:00 - 2am
      * M11.1.0/2:00:00
    """
    month, occur, day, h, min, sec = p

    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if ((((year % 4) == 0) and ((year % 100) != 0)) or (year % 400) == 0):
        month_days[1] = 29

    # Gauss date algo, determine day of week for first day of the month
    d = 1
    x = year - ((14 - month) // 12)
    y = (x + (x // 4)) - ((x // 100)) + ((x // 400))
    z = month + 12 * ((((14 - month)) // 12)) - 2;
    first_dom = (d + y + ((31 * z) // 12)) % 7
    #print('Gauss first of the %r month %r' % (month, first_dom))

    # determine the day of the month
    dom = 1 + (occur - 1) * 7 + (day - first_dom) % 7

    if dom > month_days[month - 1]:
        dom -= 7
    
    tr = time.mktime((year, month, dom, h, min, sec, 0, 0, 0))  # NOTE 9 params for CPython... 8 for MicroPython
    return tr  # NOTE for CPython, DST start time could be off an hour... Fine in Micropython

def debug_localtime():
    t = time.time()
    print(t)
    print(parse_tz('PST8PDT,M3.2.0,M11.1.0'))
    print(parse_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00'))

    parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0')
    start_date = determine_change(parsed.start, 2025)
    end_date = determine_change(parsed.end, 2025)
    print(time.localtime(start_date), start_date)
    print(time.localtime(end_date), end_date)

#debug_localtime()
