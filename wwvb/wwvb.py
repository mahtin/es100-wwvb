#!/usr/bin/env python3
""" WWVB 60Khz Full funcionality receiver/parser for i2c bus based ES100-MOD

A time and date decoder for the ES100-MOD WWVB receiver.
See README.md for detailed/further reading.

wwvb - full function command line command to provide control and receiption from ES100-MOD WWVB receiver.

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import sys
import time
import logging
import signal
import getopt
from datetime import timedelta

from es100 import ES100, ES100Error, __version__
from .misc import convert_location, caculate_latency, is_it_nighttime
from .config import readconfig

from .ntpdriver28 import NTPDriver28, NTPDriver28Error

# ES100's pins as connected to Raspberry Pi GPIO pins

                                        # ES100 Pin 1 == VCC 3.6V (2.0-3.6V recommended)
RPI_DEFAULT_GPIO_IRQ  = 11 # GPIO-17    # ES100 Pin 2 == IRQ Interrupt Request
                                        # ES100 Pin 3 == SCL
                                        # ES100 Pin 4 == SDA
RPI_DEFAULT_GPIO_EN   = 7  # GPIO-4     # ES100 Pin 5 == EN Enable
                                        # ES100 Pin 6 == GND

MY_LOCATION = [37.363056, -121.928611, 18.9]  # SJC Airport

def doit(program_name, args):
    """ doit

    :param program_name: $0 in shell terms
    :param args: $* in shell terms
    :return: nothing

    This code will loop forever until an error occurs, or is interrupt is reached
    """

    i2c_bus = None
    i2c_address = None
    flag_debug = False
    flag_verbose = False
    es100_irq = RPI_DEFAULT_GPIO_IRQ
    es100_en = RPI_DEFAULT_GPIO_EN
    our_location_name = ''
    our_location = MY_LOCATION[:2]
    our_masl = MY_LOCATION[2]
    flag_enable_nighttime = False
    flag_force_tracking = False
    antenna_choice = None
    ntpd_unit_number = None

    # needed within this and other modules
    required_format = '%(asctime)s %(name)s %(levelname)s %(message)s'
    logging.basicConfig(format=required_format)

    usage = program_name + ' ' + ' '.join([
                                '[-V|--version]',
                                '[-h|--help]',
                                '[-v|--verbose]',
                                '[-d|--debug]',
                                '[-b|--bus={0-1}]',
                                '[-a|--address={8-127}]',
                                '[-i|--irq={1-40}]',
                                '[-e|--en={1-40}]',
                                '[-l|--location=lat,long]',
                                '[-m|--masl={0-99999}]',
                                '[-n|--nighttime]',
                                '[-t|--tracking]',
                                '[-A|--antenna={0-1}]',
                                '[-N|--ntpd={0-255}]',
                            ])

    # we set defaults from config file - so that command line can override
    config = readconfig()

    if 'wwvb.station' in config:
        station = config['wwvb.station']
        our_location_name = config[station + '.' + 'name']
        our_location = config[station + '.' + 'location']
        our_location = convert_location(our_location)
        our_masl = config[station + '.' + 'masl']
        antenna_choice = config[station + '.' + 'antenna']

    if 'wwvb.bus' in config:
        i2c_bus = config['wwvb.bus']
    if 'wwvb.address' in config:
        i2c_address = config['wwvb.address']
    if 'wwvb.irq' in config:
        es100_irq = config['wwvb.irq']
    if 'wwvb.en' in config:
        es100_en = config['wwvb.en']
    if 'wwvb.nighttime' in config:
        flag_enable_nighttime = config['wwvb.nighttime']
    if 'wwvb.tracking' in config:
        flag_enable_nighttime = config['wwvb.tracking']
    if 'debug.debug' in config:
        flag_debug = config['debug.debug']
    if 'debug.verbose' in config:
        flag_verbose = config['debug.verbose']
    if 'ntpd.unit' in config:
        ntpd_unit_number = config['ntpd.unit']

    try:
        opts, args = getopt.getopt(args,
                                    'Vhvdb:a:i:e:l:m:ntAN:',
                                    [
                                        'version',
                                        'help',
                                        'verbose',
                                        'debug',
                                        'bus=',
                                        'address=',
                                        'size=',
                                        'irq=',
                                        'en=',
                                        'location=',
                                        'masl=',
                                        'nighttime',
                                        'tracking',
                                        'antenna',
                                        'ntpd=',
                                    ])
    except getopt.GetoptError:
        sys.exit('usage: ' + usage)

    for opt, arg in opts:
        if opt in ('-V', '--version'):
            print("%s %s" % (program_name, __version__), file=sys.stderr)
            sys.exit(0)
        if opt in ('-h', '--help'):
            print("%s %s" % ('usage:', usage), file=sys.stderr)
            sys.exit(0)
        if opt in ('-v', '--verbose'):
            logging.basicConfig(level=logging.INFO)
            flag_verbose = True
            continue
        if opt in ('-d', '--debug'):
            logging.basicConfig(level=logging.DEBUG)
            flag_debug = True
            continue
        if opt in ('-b', '--bus'):
            try:
                i2c_bus = int(arg)
            except ValueError:
                print("%s %s" % (program_name, 'invalid bus'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-a', '--address'):
            try:
                i2c_address = int(arg, 16)
            except ValueError:
                print("%s %s" % (program_name, 'invalid address'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-i', '--irq'):
            try:
                es100_irq = int(arg)
            except ValueError:
                print("%s %s" % (program_name, 'invalid irq'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-e', '--en'):
            try:
                es100_irq = int(arg)
            except ValueError:
                print("%s %s" % (program_name, 'invalid en'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-l', '--location'):
            try:
                our_location = convert_location(arg)
            except ValueError:
                print("%s %s" % (program_name, 'invalid location'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-m', '--masl'):
            try:
                our_masl = int(arg)
            except ValueError:
                print("%s %s" % (program_name, 'invalid masl'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-n', '--nighttime'):
            flag_enable_nighttime = True
            continue
        if opt in ('-t', '--tracking'):
            flag_force_tracking = True
            continue
        if opt in ('-A', '--antenna'):
            try:
                antenna_choice = int(arg)
                if antenna_choice not in [1, 2]:
                    raise ValueError
            except ValueError:
                print("%s %s" % (program_name, 'invalid antenna number'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue
        if opt in ('-N', '--ntpd'):
            try:
                ntpd_unit_number = int(arg)
                if not 0 <= ntpd_unit_number < 256:
                    raise ValueError
            except ValueError:
                print("%s %s" % (program_name, 'invalid ntpd unit number'), file=sys.stderr)
                sys.exit('usage: ' + usage)
            continue

    log = logging.getLogger(program_name)
    if flag_debug:
        log.setLevel(logging.DEBUG)
    if flag_verbose:
        log.setLevel(logging.INFO)

    (distance_km, bearing, latency_secs) = caculate_latency(our_location[0], our_location[1])

    log.info('The great circle distance to WWVB: %.1f Km and ' +
                    'direction is %.1f degrees; ' +
                    'hence latency %.3f Milliseconds',
                distance_km,
                bearing,
                latency_secs * 1000.0
            )

    our_latency = timedelta(microseconds=latency_secs*1000000.0)

    try:
        es100 = ES100(antenna=antenna_choice, irq=es100_irq, en=es100_en, bus=i2c_bus, address=i2c_address, debug=flag_debug, verbose=flag_verbose)
    except ES100Error as err:
        sys.exit(err)

    # If we are talking to NTPD, now's the time to set that up.
    if ntpd_unit_number is not None:
        try:
            driver28 = NTPDriver28(unit=ntpd_unit_number, debug=flag_debug, verbose=flag_verbose)
            log.info('ntpd connected via: %s' % (driver28))
        except NTPDriver28Error as err:
            log.warning('failed to connect to ntpd, continuing anyway')
            ntpd_unit_number = None
            driver28 = None
    else:
        driver28 = None

    # All set. Let's start receiving till the end of time

    while True:
        received_dt = receive(es100, log, flag_force_tracking, flag_enable_nighttime, our_location, our_masl)
        if not received_dt:
            continue

        # by default WWVB has microsecond == 0 (as it's not in the receive frames)

        # Remember that our_latency we caculated based on our location?
        # We now add it into the time received time to correct for our location
        received_dt += our_latency

        sys_received_dt = es100.system_time()
        if received_dt.year == 1 and received_dt.month == 1 and received_dt.day == 1:
            # tracking result with only seconnd and microsecond being accurate
            log.info('Time received (seconds only): %02d.%03d at %s',
                        received_dt.second,
                        int(received_dt.microsecond / 1000),
                        sys_received_dt
                    )
            print('WWVB: (tracking) %02d.%03d at %s' % (
                        received_dt.second,
                        int(received_dt.microsecond / 1000),
                        sys_received_dt
                    ))
            sys.stdout.flush()
            continue

        delta_seconds = es100.delta_seconds()
        rx_antenna = es100.rx_antenna()

        if driver28:
            leap_second = es100.leap_second()
            update_ntpd(driver28, log, received_dt, sys_received_dt, leap_second)

        log.info('Reception of %s at system time %s with difference %.3f via %s',
                                received_dt,
                                sys_received_dt,
                                delta_seconds,
                                rx_antenna
                        )

        print('WWVB: %s at %s' % (received_dt, sys_received_dt))
        sys.stdout.flush()

    # not reached

previous_nighttime = None

def receive(es100, log, flag_force_tracking, flag_enable_nighttime, our_location, our_masl):
    """ receive()

    :param es100: The previously opened instance used to talk with the ES100-MOD
    :param log: Standard Python logging instance
    :param flag_force_tracking: A flag used to run the ES100-MODE in trackmode all the time (Default is False)
    :param flag_enable_nighttime: A flag used to produce compluted nighttime/daytime.  Such that the  ES100-MODE can swap between daytime tracking and nighttime reception.  (Default is False)
    :param our_location [lat, lon]: Receivers location. Negative lat and lon is South and West.
    :param our_masl: Receivers MASL (Meters Above Sea Level)

    :return: The received date and time as datetime.datetime

    Setup everything to receive the date and time.
    """

    global previous_nighttime

    if flag_force_tracking:
        # Always do tracking (ignore nighttime flag)
        new_tracking_flag = True
        log.info('Reception starting (tracking forced on)')
    else:
        if flag_enable_nighttime:
            if  is_it_nighttime(our_location[0], our_location[1], our_masl):
                # nighttime
                new_tracking_flag = False
                if previous_nighttime is not True:
                    log.info('Nighttime in-progress (Reception starting)')
                previous_nighttime = True
            else:
                # daytime
                new_tracking_flag = True
                if previous_nighttime is not False:
                    log.info('Daytime in-progress (Tracking starting)')
                previous_nighttime = False
        else:
            # Don't care about nighttime/daytime; always receive
            new_tracking_flag = False
            log.info('Reception starting')

    try:
        received_dt = es100.time(tracking=new_tracking_flag)
    except (ES100Error, OSError):
        return None

    return received_dt

def update_ntpd(driver28, log, received_dt, sys_received_dt, leap_second):
    """ update_ntpd()

    :param driver28: shared memory instance
    :param log: logging instance
    :param received_dt: date and time just received from WWVB
    :param sys_received_dt: date and time of system when date and time was received
    :param leap_second: leap second indication

    Try to update NTPD via SHM
    """
    log.info('NTPD being updated: %s', received_dt)
    driver28.update(received_dt, sys_received_dt, leap_second)

def signal_handler(signalnum, current_stack_frame):
    """ signal_handler()
    :param signalnum: Signal number (i.e. 15 == SIGTERM)
    :param current_stack_frame: Current stack frame or None

    """
    # cleanup of ES100 and the like will be done by exit
    if signalnum == signal.SIGINT:
        sys.exit('^C')
    sys.exit('Signal received: %s' % (signalnum))

def wwvb(args=None):
    """ wwvb()

    :param args: list The command line paramaters (shell's $0 $*) (Default is None)
    :return: nothing

    WWVB command line entry point
    """

    if args is None:
        args = sys.argv[1:]

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    #program_name = sys.argv[0]
    program_name = 'wwvb'
    doit(program_name, args)

    sys.exit(0)
