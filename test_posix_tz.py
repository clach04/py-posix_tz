# test_posix_tz does **not** use unittest, as it's not included by default with MicroPython
# not a robust test suite, stops on errors (and under MicroPython, stops with very little context

import time

from posix_tz import determine_change, parse_tz, localtime, iso_like_str, mktime

DEFAULT_FATAL = True
DEFAULT_FATAL = False  # Debug!
is_mp = False

failure_count = 0

def assert_equal(a, b, fatal=DEFAULT_FATAL):
    try:
        assert a == b, '%r != %r' % (a, b)
    except AssertionError as info:
        global failure_count
        failure_count += 1
        if fatal:
            raise
        else:
            # TODO
            print('AssertionError! Carrying on to next test: %r' % (info,))

def assert_equal_timetuple(a, b, fatal=DEFAULT_FATAL):
    """For testing purposes make CPython struct a tuple, and restrict to 8 items (ignoreing 9th)
    TODO revisiting item throwing away
    """
    tuple_a = (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7])
    tuple_b = (b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7])
    assert_equal(tuple_a, tuple_b, fatal=fatal)

def assert_is_none(a):
    assert a is None, '%r != %r' % (a, None)

class MyBaseTestCase:
    def run(self):
        print('Running tests %r:' % self.__class__.__name__)
        tests = []
        for x in dir(self):
            if x.startswith('test'):
                tests.append(x)
        tests.sort()
        for test in tests:
            func = getattr(self, test)
            print('Running test %s.%s' % (self.__class__.__name__, test))
            func()

class MyTestCase(MyBaseTestCase):
    def test1(self):
        assert_equal(0, 0)
        assert_equal(0, 1)

class UtcOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('UTC')

    def test_name(self):
        assert_equal('UTC', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

class GmtOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT')

    def test_name(self):
        assert_equal('GMT', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

class GmtZeroOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT0')

    def test_name(self):
        assert_equal('GMT', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

class GmtMinusZeroOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT-0')

    def test_name(self):
        assert_equal('GMT', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

class GmtPlusZeroOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT+0')

    def test_name(self):
        assert_equal('GMT', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

class IndiaOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('IST-5:30')

    def test_name(self):
        assert_equal('IST', self.parsed.name)

    def test_offset(self):
        assert_equal(19800, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

class UsaLosAngeles(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0')

    def test_name(self):
        assert_equal('PST', self.parsed.name)

    def test_offset(self):
        assert_equal(-8 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-7 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('PDT', self.parsed.dst_name)

    def test_2025(self):
        start_date = time.gmtime(determine_change(self.parsed.start, 2025, self.parsed.offset))
        end_date = time.gmtime(determine_change(self.parsed.end, 2025, self.parsed.dst_offset))
        canon_start_date = (2025, 3, 9, 10, 0, 0, 6, 68)
        canon_end_date = (2025, 11, 2, 9, 0, 0, 6, 306)
        assert_equal_timetuple(canon_end_date, end_date)
        assert_equal_timetuple(canon_start_date, start_date)

class UsaLosAngeles_2am(UsaLosAngeles):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

class UsaNewYork(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('EST5EDT,M3.2.0,M11.1.0')

    def test_name(self):
        assert_equal('EST', self.parsed.name)

    def test_offset(self):
        assert_equal(-5 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-4 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('EDT', self.parsed.dst_name)

    def test_2025(self):
        start_date = time.gmtime(determine_change(self.parsed.start, 2025, self.parsed.offset))
        end_date = time.gmtime(determine_change(self.parsed.end, 2025, self.parsed.dst_offset))
        canon_start_date = (2025, 3, 9, 7, 0, 0, 6, 68)
        canon_end_date = (2025, 11, 2, 6, 0, 0, 6, 306)
        assert_equal_timetuple(canon_end_date, end_date)
        assert_equal_timetuple(canon_start_date, start_date)

class UsaNewYork_2am(UsaNewYork):
    def __init__(self):
        self.parsed = parse_tz('EST5EDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

class UsaLosAngeles_2am_end_only(UsaLosAngeles):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0/2:00:00')


GMT_TUPLE_2026_06_28__19_44_14 = (2026, 6, 28, 19, 44, 14, 6, 179, 0)
GMT_TUPLE_2025_01_01__00_00_00 = (2025, 1, 1, 0, 0, 0, 2, 1, 0)

class ChinaStandardTime(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('CST-8')

    def test_name(self):
        assert_equal('CST', self.parsed.name)

    def test_offset(self):
        assert_equal(8 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2026-06-29 03:44:14 CST', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2025-01-01 08:00:00 CST', iso_like_str(tt, self.parsed))

class IndiaStandardTime(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('IST-5:30')

    def test_name(self):
        assert_equal('IST', self.parsed.name)

    def test_offset(self):
        assert_equal(19800, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2026-06-29 01:14:14 IST', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2025-01-01 05:30:00 IST', iso_like_str(tt, self.parsed))

class GermanyBerlin(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('CET-1CEST,M3.5.0,M10.5.0/3:00:00')

    def test_name(self):
        assert_equal('CET', self.parsed.name)

    def test_offset(self):
        assert_equal(1 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(2 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('CEST', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(1, tt[8])
        assert_equal('2026-06-28 21:44:14 CEST', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2025-01-01 01:00:00 CET', iso_like_str(tt, self.parsed))

class UtcTimeZone(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('UTC')

    def test_name(self):
        assert_equal('UTC', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2026-06-28 19:44:14 UTC', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2025-01-01 00:00:00 UTC', iso_like_str(tt, self.parsed))

class UkLondon(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT0BST,M3.5.0/1:00:00,M10.5.0/1:00:00')

    def test_name(self):
        assert_equal('GMT', self.parsed.name)

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(1 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('BST', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(1, tt[8])
        assert_equal('2026-06-28 20:44:14 BST', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2025-01-01 00:00:00 GMT', iso_like_str(tt, self.parsed))

class UsaNewYork_TzList(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('EST5EDT,M3.2.0,M11.1.0')

    def test_name(self):
        assert_equal('EST', self.parsed.name)

    def test_offset(self):
        assert_equal(-5 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-4 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('EDT', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(1, tt[8])
        assert_equal('2026-06-28 15:44:14 EDT', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2024-12-31 19:00:00 EST', iso_like_str(tt, self.parsed))

class UsaTexas(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('CST6CDT,M3.2.0,M11.1.0')

    def test_name(self):
        assert_equal('CST', self.parsed.name)

    def test_offset(self):
        assert_equal(-6 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-5 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('CDT', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(1, tt[8])
        assert_equal('2026-06-28 14:44:14 CDT', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2024-12-31 18:00:00 CST', iso_like_str(tt, self.parsed))

class UsaLosAngeles_TzList(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

    def test_name(self):
        assert_equal('PST', self.parsed.name)

    def test_offset(self):
        assert_equal(-8 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-7 * 60 * 60, self.parsed.dst_offset)

    def test_dst_name(self):
        assert_equal('PDT', self.parsed.dst_name)

    def test_localtime(self):
        ts = mktime(GMT_TUPLE_2026_06_28__19_44_14)
        tt = localtime(ts, self.parsed)
        assert_equal(1, tt[8])
        assert_equal('2026-06-28 12:44:14 PDT', iso_like_str(tt, self.parsed))

    def test_localtime_jan2025(self):
        ts = mktime(GMT_TUPLE_2025_01_01__00_00_00)
        tt = localtime(ts, self.parsed)
        assert_equal(0, tt[8])
        assert_equal('2024-12-31 16:00:00 PST', iso_like_str(tt, self.parsed))

"""
for x in dir():
    if x == 'MyBaseTestCase':
        continue
    object = globals()[x]
    print(x, object)
    if issubclass(object, MyBaseTestCase):# and object is not :
        print('\t',  object)
"""
for test_class in (  # FIXME, automate this
    UtcOffsets,
    GmtOffsets,
    GmtZeroOffsets,
    GmtMinusZeroOffsets,
    GmtPlusZeroOffsets,
    UsaLosAngeles,
    UsaLosAngeles_2am,
    UsaLosAngeles_2am_end_only,
    IndiaOffsets,
    UsaNewYork,
    UsaNewYork_2am,
    ChinaStandardTime,
    IndiaStandardTime,
    GermanyBerlin,
    UtcTimeZone,
    UkLondon,
    UsaNewYork_TzList,
    UsaTexas,
    UsaLosAngeles_TzList,
    ):
        x = test_class()
        x.run()
print('Assertion failure_count (NOT test count) %d' % (failure_count,))
