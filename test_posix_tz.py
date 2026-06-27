# test_posix_tz does **not** use unittest, as it's not included by default with MicroPython
# not a robust test suite, stops on errors (and under MicroPython, stops with very little context

import time

from posix_tz import determine_change, parse_tz

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

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class GmtOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT')

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class GmtZeroOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT0')

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class GmtMinusZeroOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT-0')

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class GmtPlusZeroOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('GMT+0')

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class IndiaOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('IST-5:30')

    def test_offset(self):
        assert_equal(19800, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class UsaLosAngelesOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0')

    def test_offset(self):
        assert_equal(-8 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-7 * 60 * 60, self.parsed.dst_offset)

class UsaLosAngeles(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0')

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

class UsaNewYorkOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('EST5EDT,M3.2.0,M11.1.0')

    def test_offset(self):
        assert_equal(-5 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-4 * 60 * 60, self.parsed.dst_offset)

class UsaNewYork(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('EST5EDT,M3.2.0,M11.1.0')

    def test_2025(self):
        start_date = time.gmtime(determine_change(self.parsed.start, 2025, self.parsed.offset))
        end_date = time.gmtime(determine_change(self.parsed.end, 2025, self.parsed.dst_offset))
        canon_start_date = (2025, 3, 9, 7, 0, 0, 6, 68)
        canon_end_date = (2025, 11, 2, 6, 0, 0, 6, 306)
        assert_equal_timetuple(canon_end_date, end_date)
        assert_equal_timetuple(canon_start_date, start_date)

class UsaNewYork_2am(MyBaseTestCase):
    def __init__(self):
        self.parsed = parse_tz('EST5EDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

class UsaLosAngeles_2am_end_only(UsaLosAngeles):
    def __init__(self):
        self.parsed = parse_tz('PST8PDT,M3.2.0,M11.1.0/2:00:00')


# TODO test posix_tz.localtime()

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
    UsaLosAngelesOffsets,
    UsaLosAngeles,
    UsaLosAngeles_2am,
    UsaLosAngeles_2am_end_only,
    IndiaOffsets,
    UsaNewYorkOffsets,
    UsaNewYork,
    UsaNewYork_2am,
    ):
        x = test_class()
        x.run()
print('Assertion failure_count (NOT test count) %d' % (failure_count,))
