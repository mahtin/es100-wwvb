""" misc.py

Provide misc functions for CLI wwvb command

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

from math import degrees, radians, sin, cos, acos, atan2

from .sun import Sun

WWVB_FT_COLLINS = [40.6777225, -105.047153, 1585]  # latitude, longitude, and MASL

RADIOWAVE_SPEED = 299250.0              # km / sec

def convert_location(lat_lon):
    """ convert_location """

    if isinstance(lat_lon, list):
        lat = lat_lon[0]
        lon = lat_lon[1]
    else:
        # try to split a string
        try:
            if ',' in lat_lon:
                (lat, lon) = lat_lon.split(',',2)
            elif ' ' in lat_lon:
                (lat, lon) = lat_lon.split(' ',2)
            else:
                raise ValueError('invalid lat lon format')
        except ValueError as err:
            raise ValueError from err

    if isinstance(lat, float) and isinstance(lon, float):
        # done!
        return [lat, lon]

    lat = lat.strip()
    lon = lon.strip()
    if lat[-1] == 'N':
        lat = '+' + lat[:-1]
    elif lat[-1] == 'S':
        lat = '-' + lat[:-1]
    if lon[-1] == 'E':
        lon = '+' + lon[:-1]
    elif lon[-1] == 'W':
        lon = '-' + lon[:-1]

    # both these cases are bogus and should not happen
    if lat[0:2] in ['--', '-+', '+-', '++']:
        lat = lat[1:]
    if lon[0:2] in ['--', '-+', '+-', '++']:
        lon = lon[1:]

    try:
        return [float(lat), float(lon)]
    except ValueError as err:
        raise ValueError from err

def caculate_latency(my_lat, my_lon):
    """ caculate_latency """

    distance_km = great_circle_km(
                    my_lat, my_lon,
                    WWVB_FT_COLLINS[0], WWVB_FT_COLLINS[1])

    bearing = bearing_degrees(
                    my_lat, my_lon,
                    WWVB_FT_COLLINS[0], WWVB_FT_COLLINS[1])

    latency_secs = distance_km / RADIOWAVE_SPEED

    return (distance_km, bearing, latency_secs)

sun_at_wwvb_ft_collins = None
sun_at_my_receiver = None

def is_it_nighttime(my_lat, my_lon, my_masl, dtime=None):
    """ is_it_nighttime """
    global sun_at_wwvb_ft_collins, sun_at_my_receiver

    if not sun_at_wwvb_ft_collins:
        sun_at_wwvb_ft_collins = Sun(WWVB_FT_COLLINS[0], WWVB_FT_COLLINS[1], WWVB_FT_COLLINS[2])
    if not sun_at_my_receiver:
        sun_at_my_receiver = Sun(my_lat, my_lon, my_masl)

    # VLW Reception is better at night (you learned that when becoming a ham radio operator)
    # if both location are dark presently, then radio waves should flow
    return bool(sun_at_wwvb_ft_collins.civil_twilight(dtime) and sun_at_my_receiver.civil_twilight(dtime))

# You can double check this caculation via GCMAP website.
# http://www.gcmap.com/mapui?P=WWVB%3D40.678062N105.046688W%3B%0D%0ASJC-WWVB&R=1505Km%40WWVB&PM=b%3Adisc7%2B%22%25U%25+%28N%22&MS=wls2&DU=km

def great_circle_km(lat1, lon1, lat2, lon2):
    """ great_circle """
    # https://medium.com/@petehouston/calculate-distance-of-two-locations-on-earth-using-python-1501b1944d97
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    return 6371 * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))

def bearing_degrees(lat1, lon1, lat2, lon2):
    """ bearing_degrees """
    # https://stackoverflow.com/questions/54873868/python-calculate-bearing-between-two-lat-long
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    x = cos(lat2) * sin(lon2 - lon1)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1)
    bearing = degrees(atan2(x, y))
    if bearing < 0.0:
        return bearing + 360.0
    return bearing
