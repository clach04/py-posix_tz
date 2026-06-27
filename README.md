# py-posix_tz

Python / MicroPython package for processing POSIX TZ names/rules for localtime() lookup/derivation that's timezone and DST aware

https://github.com/clach04/py-posix_tz

Primarily focused on MicroPython where memory/storage is restricted. If you have a full Python implementation (like CPython, etc.) use an IANA timezone API instead.

The timezone support that POSIX TZ offers (in general, not specifically about this package) is limited to now and the future. It has no idea about previous rules, there is only one rule. If new rules for a timezone are created, a new TZ will need to be created and deployed.

## MicroPython Usage

Assuming already installed, and device on network:

```python
import ntptime  # https://github.com/micropython/micropython-lib/blob/master/micropython/net/ntptime/ntptime.py

from posix_tz import global_tzd, localtime, set_tz

ntptime.settime()  # standard micropython sets clock to UTC (GMT0)

print('time.time() %r' % (time.time(),))
print('time.localtime() %r' % (time.localtime(),))
print('time.gmtime() %r' % (time.gmtime(),))
print('')

print('global_tzd %r' % (global_tzd,))
print('set TZ')
set_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00')  # Los Angeles rule, valid as of 2025 (and previous few years)
print('global_tzd %r' % (global_tzd,))
print('localtime() %r' % (localtime(),))
```

Show two timezones

```python
import time

from posix_tz import global_tzd, iso_like_str, localtime, parse_tz, set_tz, tzd_tuple
# assume clock already set

tt = time.mktime((2026, 6, 7, 16, 46, 0, -1, -1, -1))  # NOTE 9-tuple
utc = parse_tz('UTC')
los_angeles = parse_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

print('localtime() %r' % (localtime(n=None, tzd=los_angeles),))
print('localtime() %r' % (localtime(n=tt, tzd=los_angeles),))
print('iso_like_str() %r' % (iso_like_str(localtime(n=tt, tzd=los_angeles), tzd=los_angeles),))
print('iso_like_str() %r' % (iso_like_str(localtime(n=tt, tzd=utc), tzd=utc),))
print('time.localtime() %r' % (time.localtime(tt),))
print('time.gmtime() %r' % (time.gmtime(tt),))
```

Simple world clock.

```python
import time

from posix_tz import localtime, mktime  # NOTE overrides compared with CPython
from posix_tz import global_tzd, iso_like_str, parse_tz, set_tz, tzd_tuple
# assume clock already set

tz_list = [
    'CST-8',  # China Standard Time
    'IST-5:30',  # India Standard Time
    #'CET-1CEST,M3.5.0,M10.5.0/3',  # Germany, Berlin  # FIXME
    'CET-1CEST,M3.5.0,M10.5.0/3:00:00',  # Germany, Berlin
    'UTC',  # Coordinated Universal Time (UTC) / GMT0
    #'GMT0BST,M3.5.0/1,M10.5.0', # UK, London  # FIXME
    'GMT0BST,M3.5.0/1:00:00,M10.5.0/1:00:00', # UK, London  # FIXME
    'EST5EDT,M3.2.0,M11.1.0',  # USA/New York - 'EST5EDT,M3.2.0/2:00:00,M11.1.0/2:00:00'
    'CST6CDT,M3.2.0,M11.1.0',  # USA/Texas
    'PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00',  # USA/Los Angeles
]
tzs = []
for tz_name in tz_list:
    print(tz_name)
    tzs.append(parse_tz(tz_name))

t_list = [
    (2025, 1, 1, 0, 0, 0, -1, -1, -1),
    (2026, 6, 7, 16, 46, 0, -1, -1, -1),
    None  # determine current time
]
for t in t_list:
    if t:
        tt = mktime(t)
    else:
        tt = mktime(time.gmtime())
    print(t)
    print(tt)
    for tz in tzs:
        print(iso_like_str(localtime(n=tt, tzd=tz), tzd=tz))
    print('')

```

## MicroPython WASM Usage

Combine module and tests into one file suitable for running in MicroPython WASM,
either https://tools.simonwillison.net/micropython or command line

    cp posix_tz.py concat.py  # copy /Y posix_tz.py concat.py
    rg -v -N import test_posix_tz.py >> concat.py
    micropython-wasm --memory 33554432 --fuel 200000000 concat.py


## Resources

### Time refresher for MicroPython and Python

from https://docs.micropython.org/en/latest/library/time.html#time.localtime

> Convert the time secs expressed in seconds since the Epoch (see above) into an
> 8-tuple which contains: (year, month, mday, hour, minute, second, weekday, yearday)
> If secs is not provided or None, then the current time from the RTC is used.

**NOTE** tuple with eight elements.

The format of the entries in the 8-tuple are:

> 1. year includes the century (for example 2014).
> 2. month is 1-12
> 3. mday is 1-31
> 4. hour is 0-23
> 5. minute is 0-59
> 6. second is 0-59
> 7. weekday is 0-6 for Mon-Sun
> 8. yearday is 1-366


Compare with:

  * https://docs.python.org/3/library/time.html#time.localtime
  * https://docs.python.org/3/library/time.html#time.mktime

> (mktime) This is the inverse function of localtime().
> Its argument is the struct_time or full 9-tuple (since the dst flag is needed; use -1 as the dst flag if it is unknown)
> which expresses the time in local time, not UTC. It returns a floating-point number, for compatibility with time().

Highlights:

  * time.time() is int on esp32 Micropython, float in CPython
  * time.localtime() is an 8-tuple in Micropython, versus 9-tuple struct/class/namedtuple in CPython (3.x) with **different** attributes


### Documentation on rules

  * https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
  * https://www.netburner.com/learn/time-zones-and-daylight-savings-with-olson-and-posix/
  * Posix specification for time zone names: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap08.html#tag_08_03
  * https://developer.ibm.com/articles/au-aix-posix/#posix-format-specification1


### Sample mappings IANA names to posix strings

  * https://github.com/clach04/Esp8266_Wifi_Matrix_Clock/blob/patch-1/posix.md#sample-iana-to-posix-strings (from https://github.com/yuan910715/Esp8266_Wifi_Matrix_Clock/blob/master/posix.md)
  * https://support.cyberdata.net/portal/en/kb/articles/010d63c0cfce3676151e1f2d5442e311
