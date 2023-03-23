""" sun.py

Provide sun tracking functions for CLI wwvb command

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import datetime
from math import degrees
from zoneinfo import ZoneInfo

utc_tz = ZoneInfo('UTC')

import ephem

class Sun:
    """ Sun()

    :param lat: Latitude (in decimal degrees)
    :param lon: Longitude (in decimal degrees)
    :param elev: Elevation in meters above sea level (MASL)
    :return: New instance

    Sun tracking code for sunset/sunrise math.
    Used to decide if a location is in nightime or not.

    All times are kept in UTC.

    Based on PyEphem (which is a fantastic package!)
    https://rhodesmill.org/pyephem/
    """

    def __init__(self, lat, lon, elev=0.0):
        """ :meta private: """
        self._sun = ephem.Sun()
        self._viewer = ephem.Observer()
        self._viewer.date = datetime.datetime.utcnow()
        self._viewer.lat = str(lat)
        self._viewer.lon = str(lon)
        self._viewer.elev = elev
        self._viewer.horizon = '0'

    def altitude(self, dtime=None):
        """ altitude()

        :param dtime: Optional datetime value (defaults to now)
        :return: Altitude +/-90 degrees relative to the horizon’s great circle

        Apparent position relative to horizon in degrees (negative means sun has set).
        """
        if dtime:
            self._viewer.date = dtime
        else:
            self._viewer.date = datetime.datetime.utcnow()
        # always (re)compute as time tends to march-on.
        self._sun.compute(self._viewer)
        # yes, humans prefer degrees
        return degrees(self._sun.alt)

    # look for twilight, which is 6, 12, or 18 degrees below horizon
    # see https://www.weather.gov/lmk/twilight-types

    def civil_twilight(self, dtime=None):
        """ civil_twilight()
        :param dtime: Optional datetime value (defaults to now)
        :return: True if it's civil twilight
        """
        return bool(self.altitude(dtime) <= -6.0)

    def nautical_twilight(self, dtime=None):
        """ nautical_twilight()
        :param dtime: Optional datetime value (defaults to now)
        :return: True if it's nautical twilight
        """
        return bool(self.altitude(dtime) <= -12.0)

    def astronomical_twilight(self, dtime=None):
        """ astronomical_twilight()
        :param dtime: Optional datetime value (defaults to now)
        :return: True if it's astronomical twilight
        """
        return bool(self.altitude(dtime) <= -18.0)

    def rising_setting(self, dtime=None, tz='UTC'):
        """ next_rising()
        :param dtime: Optional datetime value (defaults to now)
        :return: date/time of next rising
        """
        if dtime:
            self._viewer.date = dtime
        else:
            self._viewer.date = datetime.datetime.utcnow()
        if tz == 'UTC':
            tz = utc_tz
        else:
            tz = ZoneInfo(tz)
        # always (re)compute as time tends to march-on.
        self._sun.compute(self._viewer)
        return (
                ephem.to_timezone(self._viewer.next_rising(self._sun), tz),
                ephem.to_timezone(self._viewer.next_setting(self._sun), tz)
        )
