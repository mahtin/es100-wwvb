""" maidenhead.py

Provide maidenhead conversion functions

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

#
# Quoting https://en.wikipedia.org/wiki/Maidenhead_Locator_System
#
# Character pairs encode longitude first, and then latitude.
# The first pair (a field) encodes with base 18 and the letters "A" to "R".
# The second pair (square) encodes with base 10 and the digits "0" to "9".
# The third pair (subsquare) encodes with base 24 and the letters "a" to "x".
# The fourth pair (extended square) encodes with base 10 and the digits "0" to "9".
#
# (The fifth and subsequent pairs are not formally defined, but recursing to the third and fourth pair algorithms is a possibility, e.g.: BL11bh16oo66)
#

def maidenhead(locator):
    """ maidenhead() """

    if len(locator) not in [2,4,6,8,10,12]:
        raise ValueError('Invalid Maidenhead Locator')
    locator = locator.upper()
    lon = -180.0
    lat = -90.0

    if 'A' <= locator[0] <= 'R' and 'A' <= locator[1] <= 'R':
        lon += (ord(locator[0]) - ord('A')) * 360.0/18
        lat += (ord(locator[1]) - ord('A')) * 180.0/18
    else:
        raise ValueError('Invalid Maidenhead Locator')
    if len(locator) == 2:
        lon += 360.0/18 * 0.5
        lat += 180.0/18 * 0.5
        return [float(lat), float(lon)]
    if '0' <= locator[2] <= '9' and '0' <= locator[3] <= '9':
        lon += (ord(locator[2]) - ord('0')) * 360.0/18/10
        lat += (ord(locator[3]) - ord('0')) * 180.0/18/10
    else:
        raise ValueError('Invalid Maidenhead Locator')
    if len(locator) == 4:
        lon += 360.0/18/10 * 0.5
        lat += 180.0/18/10 * 0.5
        return [float(lat), float(lon)]
    if 'A' <= locator[4] <= 'X' and 'A' <= locator[5] <= 'X':
        lon += (ord(locator[4]) - ord('A')) * 360.0/18/10/24
        lat += (ord(locator[5]) - ord('A')) * 180.0/18/10/24
    else:
        raise ValueError('Invalid Maidenhead Locator')
    if len(locator) == 6:
        lon += 360.0/18/10/24 * 0.5
        lat += 180.0/18/10/24 * 0.5
        return [float(lat), float(lon)]
    if '0' <= locator[6] <= '9' and '0' <= locator[7] <= '9':
        lon += (ord(locator[6]) - ord('0')) * 360.0/18/10/24/10
        lat += (ord(locator[7]) - ord('0')) * 180.0/18/10/24/10
    else:
        raise ValueError('Invalid Maidenhead Locator')
    if len(locator) == 8:
        lon += 360.0/18/10/24/10 * 0.5
        lat += 180.0/18/10/24/10 * 0.5
        return [float(lat), float(lon)]
    if 'A' <= locator[8] <= 'X' and 'A' <= locator[9] <= 'X':
        lon += (ord(locator[8]) - ord('A')) * 360.0/18/10/24/10/24
        lat += (ord(locator[9]) - ord('A')) * 180.0/18/10/24/10/24
    else:
        raise ValueError('Invalid Maidenhead Locator')
    if len(locator) == 10:
        lon += 360.0/18/10/24/10/24 * 0.5
        lat += 180.0/18/10/24/10/24 * 0.5
        return [float(lat), float(lon)]
    if '0' <= locator[10] <= '9' and '0' <= locator[11] <= '9':
        lon += (ord(locator[10]) - ord('0')) * 360.0/18/10/24/10/24/10
        lat += (ord(locator[11]) - ord('0')) * 180.0/18/10/24/10/24/10
    else:
        raise ValueError('Invalid Maidenhead Locator')
    lon += 360.0/18/10/24/10/24/10 * 0.5
    lat += 180.0/18/10/24/10/24/10 * 0.5
    return [float(lat), float(lon)]
