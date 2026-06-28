# https://github.com/clach04/py-posix_tz
# NOTE short names for space reasons
"""
time.time() is int on esp32 Micropython, float in CPython
time.localtime() / time.gmtime() is tuple in Micropython, struct/class/namedtuple in CPython (3.x) with different attributes
"""

from collections import namedtuple
import time
try:
    from calendar import timegm
except ImportError:
    timegm = None


global_tzd = None  # or UTC

def mktime(t):
    """Replacement / override to make MicroPython and CPython work for this TZ lib
    t is a tuple.
    """
    #print(t)  # time.gmtime(n)
    year, month, dom, h, min, sec = t[0], t[1], t[2], t[3], t[4], t[5]
    if 1 > month or month > 12:
        month = 1  # TODO review the need for this..
    #print('\t%r' % (month,))
    if timegm is not None:
        tr = timegm((year, month, dom, h, min, sec, 0, 0, 0))  # CPython: mktime treats tuple as localtime :-( use calendar.timegm() or datetime(..., tzinfo=timezone.utc).timestamp()
    else:
        tr = time.mktime((year, month, dom, h, min, sec, 0, 0, 0))  # MicroPython: mktime treats tuple as UTC, passing in unused 9th tuple for DST
    return tr

m_tuple = namedtuple('m', ('month', 'occur', 'day', 'hour', 'min', 'sec'))
def parse_mstr(s):
    if s[0] != 'M':
        raise NotImplemented('non-M %s not supported' % s[0])  # e.g. Julian
    ss = s.split('/')
    m = ss[0]
    if len(ss) == 2:
        t = ss[1]
    else:
        t = '2:00:00'
    month, occur, day = map(int, m[1:].split('.'))  # TODO catch non-int errors
    h, min, sec = map(int, t.split(':'))  # TODO catch non-int errors
    return m_tuple(month, occur, day, h, min, sec)

def _parse_name_offset(s):
    """Parse POSIX TZ name+offset portion, e.g. 'PST8PDT' or 'IST-5:30'
    Returns (name, sign, hour, min, sec, dst_name)
    """
    i = 0
    n = len(s)

    start = i
    while i < n and s[i].isalpha():
        i += 1
    name = s[start:i]

    sign = ''
    if i < n and s[i] in '+-':
        sign = s[i]
        i += 1

    start = i
    while i < n and s[i].isdigit():
        i += 1
    hour = int(s[start:i]) if i > start else 0

    min_val = 0
    sec_val = 0
    if i < n and s[i] == ':':
        i += 1
        start = i
        while i < n and s[i].isdigit():
            i += 1
        min_val = int(s[start:i]) if i > start else 0

    if i < n and s[i] == ':':
        i += 1
        start = i
        while i < n and s[i].isdigit():
            i += 1
        sec_val = int(s[start:i]) if i > start else 0

    dst_name = s[i:]

    return name, sign, hour, min_val, sec_val, dst_name

# timezone details tuple
tzd_tuple = namedtuple('tzd', ('name', 'offset', 'dst_name', 'start', 'end', 'dst_offset'))  # offsets are seconds
def parse_tz(s):
    ss = s.split(',')
    if len(ss) == 1:
        tzname, sign, d_hour, d_min, d_sec, dst_name = _parse_name_offset(s)
        offset = (d_hour * 60 + d_min) * 60 + d_sec
        timezone = offset * (1 if sign == "-" else -1)
        return tzd_tuple(tzname, timezone, dst_name, None, None, None)
    if len(ss) == 3:
        tzname, sign, d_hour, d_min, d_sec, dst_name = _parse_name_offset(ss[0])
        offset = (d_hour * 60 + d_min) * 60 + d_sec
        timezone = offset * (1 if sign == "-" else -1)
        return tzd_tuple(tzname, timezone, dst_name, parse_mstr(ss[1]), parse_mstr(ss[2]), timezone + 1 * 60 * 60)
    else:
        NotImplementedError('FIXME for %r)' % s)

def determine_change(p, year, offset):
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

    offset - offsets are seconds
    """
    if not p:
        return mktime((year, 0, 0, 0, 0, 0, 0, 0, 0))  # NOTE 9 params for CPython... 8 for MicroPython - this is the UTC / GMT0 time
    month, occur, day, h, min, sec = p
    min_offset = offset // 60
    h, min = (h - (min_offset // 60)), (min - (min_offset % 60))

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

    tr = mktime((year, month, dom, h, min, sec, 0, 0, 0))
    return tr


def set_tz(tz):
    global global_tzd
    global_tzd = parse_tz(tz)

_localtime_cache = {}  # rather than require functool lru (which is not built into MicroPython), cache manually with no clean up. Assume use case doesn't span hundreds of years
def localtime(n=None, tzd=None):
    if n is None:
        n = time.time()
    tzd = tzd or global_tzd
    tm_isdst = 0

    if tzd:
        time_tuple = time.gmtime(n)
        year = time_tuple[0]  # FIXME, assume DST never starts/ends on first/last day of a year - probably a safe thing todo
        #start_date, end_date = _localtime_cache.get((tzd.start, year), determine_change(tzd.start, year)), _localtime_cache.get((tzd.end, year), determine_change(tzd.end, year)
        try:
            start_date, end_date = _localtime_cache[(tzd.start, year)], _localtime_cache[(tzd.end, year)]
        except KeyError:
            start_date, end_date = determine_change(tzd.start, year, tzd.offset), determine_change(tzd.end, year, tzd.dst_offset)
            _localtime_cache[(tzd.start, year)], _localtime_cache[(tzd.end, year)] = start_date, end_date
        if start_date < n < end_date:
            n += tzd.dst_offset
            tm_isdst = 1
        else:
            n += tzd.offset
    # else assume UTC/GMT0
    tt = time.gmtime(n)
    # make a 9-tuple
    if len(tt) == 8:
        tt += (tm_isdst,)
    return tt

def iso_like_str(tt=None, tzd=None, include_tz_if_available=True):
    """Where tt is a localtime() time tuple
    """
    if tt is None:
        tt = localtime(n=None, tzd=tzd)
    tzd = tzd or global_tzd
    if include_tz_if_available and len(tt) >= 8:
        tm_isdst = tt[8]
        if tm_isdst:
            tz_name = tzd.dst_name
        else:
            tz_name = tzd.name
        return '%04d-%02d-%02d %02d:%02d:%02d %s' % (tt[0], tt[1], tt[2], tt[3], tt[4], tt[5], tz_name)
    else:
        return '%04d-%02d-%02d %02d:%02d:%02d' % (tt[0], tt[1], tt[2], tt[3], tt[4], tt[5])

def debug_localtime():
    t = time.time()
    print(t)
    print(parse_tz('PST8PDT,M3.2.0,M11.1.0'))
    print(parse_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00'))

    parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0')
    start_date = determine_change(parsed.start, 2025)
    end_date = determine_change(parsed.end, 2025)
    print(time.gmtime(start_date), start_date)
    print(time.gmtime(end_date), end_date)

#debug_localtime()
