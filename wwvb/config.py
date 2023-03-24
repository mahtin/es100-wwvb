""" config.py

Provide config file functions for CLI wwvb command

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import os
import configparser

def readconfig(filename='wwvb.ini'):
    """ readconfig()
    :param filename: config file name

    Read config file (which is wwvb.ini by default.
    """
    cp = configparser.ConfigParser()
    try:
        cp.read([
            '.wwvb.ini',
            'wwvb.ini',
            os.path.expanduser('~/.wwvb.ini'),
            '/etc/wwvb.ini'
        ], 'utf-8')
    except:
        # no configuration file - this is not an error; we are just done here
        return {}

    values = {}

    our_station = None

    section = 'WWVB'
    if cp.has_section(section):
        for option in ['bus', 'address', 'irq', 'en']:
            config_value = cp.get(section, option, fallback=None)
            if isinstance(config_value, str) and len(config_value) == 0:
                config_value = None
            try:
                if config_value is not None:
                    config_value = int(config_value)
            except (ValueError, TypeError):
                pass
            values[section.lower() + '.' + option] = config_value
        for option in ['nighttime', 'tracking']:
            config_value = cp.getboolean(section, option, fallback=False)
            values[section.lower() + '.' + option] = config_value
        for option in ['station']:
            config_value = cp.get(section, option, fallback=None)
            if isinstance(config_value, str) and len(config_value) == 0:
                config_value = None
            if config_value:
                values[section.lower() + '.' + option] = config_value.lower()
                # special case for station
                our_station = config_value

    section = 'DEBUG'
    if cp.has_section(section):
        for option in ['debug', 'verbose']:
            config_value = cp.getboolean(section, option, fallback=False)
            values[section.lower() + '.' + option] = config_value

    section = 'NTPD'
    if cp.has_section(section):
        for option in ['unit']:
            config_value = cp.get(section, option, fallback=None)
            if isinstance(config_value, str) and len(config_value) == 0:
                config_value = None
            try:
                if config_value is not None:
                    config_value = int(config_value)
            except (ValueError, TypeError):
                pass
            values[section.lower() + '.' + option] = config_value

    if our_station:
        if cp.has_section(our_station):
            section = our_station
            for option in ['name', 'location', 'masl', 'antenna']:
                config_value = cp.get(section, option, fallback=None)
                if isinstance(config_value, str) and len(config_value) == 0:
                    config_value = None
                try:
                    if config_value is not None:
                        config_value = int(config_value)
                except (ValueError, TypeError):
                    pass
                if isinstance(config_value, str) and len(config_value) > 0 and config_value[0] == '[' and config_value[-1] == ']':
                    # convert to list
                    config_value = config_value[1:-1].split(',')
                    config_value = [v.strip() for v in config_value]
                    try:
                        config_value = [float(v) for v in config_value]
                    except (ValueError, TypeError):
                        pass

                values[section.lower() + '.' + option] = config_value

    return values
