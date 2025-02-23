# test_posix_tz does **not** use unittest, as it's not included by default with MicroPython
# not a robust test suite, stops on errors (and under MicroPython, stops with very little context
 
import time

import posix_tz

def assert_equal(a, b, fatal=True):
    try:
        assert a == b, '%r != %r' % (a, b)
    except AssertionError:
        if fatal:
            raise

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
        self.parsed = posix_tz.parse_tz('UTC')

    def test_offset(self):
        assert_equal(0, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class IndiaOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('IST-5:30')

    def test_offset(self):
        assert_equal(19800, self.parsed.offset)

    def test_dstoffset(self):
        assert_is_none(self.parsed.dst_offset)  # TODO revisit this

class UsaLosAngelesOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('PST8PDT,M3.2.0,M11.1.0')

    def test_offset(self):
        assert_equal(-8 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-7 * 60 * 60, self.parsed.dst_offset)

class UsaLosAngeles(MyBaseTestCase):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('PST8PDT,M3.2.0,M11.1.0')

    def test_2025(self):
        start_date = time.localtime(posix_tz.determine_change(self.parsed.start, 2025))
        end_date = time.localtime(posix_tz.determine_change(self.parsed.end, 2025))
        canon_start_date = (2025, 3, 9, 2, 0, 0, 6, 68)
        canon_end_date = (2025, 11, 2, 2, 0, 0, 6, 306)
        assert_equal(canon_end_date, end_date)
        assert_equal(canon_start_date, start_date)

class UsaLosAngeles_2am(UsaLosAngeles):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('PST8PDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

class UsaNewYorkOffsets(MyBaseTestCase):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('EST5EDT,M3.2.0,M11.1.0')

    def test_offset(self):
        assert_equal(-5 * 60 * 60, self.parsed.offset)

    def test_dstoffset(self):
        assert_equal(-4 * 60 * 60, self.parsed.dst_offset)

class UsaNewYork(MyBaseTestCase):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('EST5EDT,M3.2.0,M11.1.0')

    def test_2025(self):
        start_date = time.localtime(posix_tz.determine_change(self.parsed.start, 2025))
        end_date = time.localtime(posix_tz.determine_change(self.parsed.end, 2025))
        canon_start_date = (2025, 3, 9, 2, 0, 0, 6, 68)
        canon_end_date = (2025, 11, 2, 2, 0, 0, 6, 306)
        assert_equal(canon_end_date, end_date)
        assert_equal(canon_start_date, start_date)

class UsaNewYork_2am(UsaLosAngeles):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('EST5EDT,M3.2.0/2:00:00,M11.1.0/2:00:00')

class UsaLosAngeles_2am_end_only(UsaLosAngeles):
    def __init__(self):
        self.parsed = posix_tz.parse_tz('PST8PDT,M3.2.0,M11.1.0/2:00:00')


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
    UsaLosAngelesOffsets,
    UsaLosAngeles,
    UsaLosAngeles_2am,
    #UsaLosAngeles_2am_end_only,  # TODO implement
    IndiaOffsets,
    UsaNewYorkOffsets,
    UsaNewYork,
    UsaNewYork_2am,
    ):
        x = test_class()
        x.run()
