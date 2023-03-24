"""

datetime and timezone for micropython - just the bare minimum

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

from machine import RTC
import utime

# The RTC() does not provide millseconds/microseconds - however, there is a way to fake it using
# the ticks_ms()'s call.
# https://github.com/charlee/rp2_led_matrix/blob/master/src/lib/rtc_clock.py

class datetime:
    """ datetime()

    :param year: Year
    :param month: Month
    :param day: Day
    :param hour: Hour
    :param minute: Minute
    :param second: Second
    :param microsecond: Microsecond
    :param tzinfo: TZ
    :return: datetime() instance

    Replacement for normal Python datetime(). Minimal implementation.
    """

    # needs to be caculated at some point - see end of file
    initial_ticks_ms = 0

    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        """ :meta private: """
        self._d = (year, month, day)
        self._t = (hour, minute, second, microsecond)
        self._tz = tzinfo

    # Via  https://github.com/charlee/rp2_led_matrix/blob/master/src/lib/rtc_clock.py
    # Thank you @charlee
    @classmethod
    def calibrate(cls):
        """ calibrate()
        Adjust the sub-second counter accoring to the RTC.
        """
        start_second = RTC().datetime()[6]
        while RTC().datetime()[6] == start_second:
            utime.sleep_ms(1)
        # It's a new seccond - record the millisecond point
        cls.initial_ticks_ms = utime.ticks_ms() % 1000  # we only need the 1000's part

    def replace(self, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=True):
        """ replace()
        :param year: Year
        :param month: Month
        :param day: Day
        :param hour: Hour
        :param minute: Minute
        :param second: Second
        :param microsecond: Microsecond
        :param tzinfo: TZ
        :return: datetime() instance

        Replacement for normal Python datetime.replace(). Minimal implementation.
        """
        if year is None:
            year = self._d[0]
        if month is None:
            month = self._d[1]
        if day is None:
            day = self._d[2]
        if hour is None:
            hour = self._t[0]
        if minute is None:
            minute = self._t[1]
        if second is None:
            second = self._t[2]
        if microsecond is None:
            microsecond = self._t[3]
        if tzinfo is True:
            tzinfo = self._tz
        return datetime(year, month, day, hour, minute, second, microsecond, tzinfo)

    def total_seconds(self):
        """ total_seconds()
        return: The total number of seconds (for hour, minute, second) values
        Replacement for normal Python datetime.replace(). Minimal implementation.
        """
        return self._t[0] * 60 * 60 + self._t[1] * 60 + self._t[2] + self._t[3]/1000000.0

    @classmethod
    def utcnow(cls):
        """ utcnow()
        :return: Now as a datetime() option
        Replacement for normal Python datetime.replace(). Minimal implementation.
        """
        # RTC return weekday (which is useless) and microsecond which is inaccurate or zero
        (year, month, day, _, hour, minute, second, _) = RTC().datetime()
        subseconds_ms = int((utime.ticks_ms() - datetime.initial_ticks_ms) % 1000)
        return datetime(year, month, day, hour, minute, second, subseconds_ms * 1000)

    @classmethod
    def setrtc(cls, dt):
        """ setrtc()
        :param dt: datetime of new "now"

        set RTC
        """
        # setting microseconds does nothing
        now = (dt.year, dt.month, dt.day, 0, dt.hour, dt.minute, dt.second, 0)
        # we should adjust calibrate so it's still correct
        # XXX todo
        RTC().datetime(now)

    @property
    def year(self):
        """ :return: year value """
        return self._d[0]

    @property
    def month(self):
        """ :return: month value """
        return self._d[1]

    @property
    def day(self):
        """ :return: day value """
        return self._d[2]

    @property
    def hour(self):
        """ :return: hour value """
        return self._t[0]

    @property
    def minute(self):
        """ :return: minute value """
        return self._t[1]

    @property
    def second(self):
        """ :return: second value """
        return self._t[2]

    @property
    def microsecond(self):
        """ :return: microsecond value """
        return self._t[3]

    def __sub__(self, other):
        """ :meta private: """
        return datetime(
                    self._d[0] - other._d[0], self._d[1] - other._d[1], self._d[2] - other._d[2],
                    self._t[0] - other._t[0], self._t[1] - other._t[1], self._t[2] - other._t[2],
                    self._t[3] - other._t[3],
                    self._tz)

    def __str__(self):
        """ :meta private: """
        if self._tz:
            # return with timezone
            return '%04d-%02d-%02d %02d:%02d:%02d.%03d%s' % (
                    self._d[0], self._d[1], self._d[2],
                    self._t[0], self._t[1], self._t[2], self._t[3]/1000,
                    self._tz
                )
        # return with no timezone
        return '%04d-%02d-%02d %02d:%02d:%02d.%03d' % (
                self._d[0], self._d[1], self._d[2],
                self._t[0], self._t[1], self._t[2], self._t[3]/1000,
            )

    def __repr__(self):
        """ :meta private: """
        return self.__str__()

# Lets calibrate the millseconds - could take from 0 to 999 milliseconds
datetime.calibrate()

# timezone only implements UTC
class timezone:
    """ timezone() """
    def __init__(self, offset):
        """ :meta private: """
        self._offset = offset

    def __str__(self):
        """ :meta private: """
        return '+00:00'

timezone.utc = timezone(0)
