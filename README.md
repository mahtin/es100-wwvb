# es100-wwvb
**WWVB** 60Khz Full functionality receiver/parser for i2c bus based **ES100-MOD**

## Description
A time and date decoder for the **ES100-MOD** **WWVB** receiver.
This code implements tracking (for daytime reception) and full receive decoding (for nighttime reception).
It provides Daylight Saving information and Leap Second information, if WWVB provides it.

It's written 100% in Python and tested on the **Raspberry Pi4** and on the **Raspberry Pi Pico W** (using `micropython`) with, or without an OLED display.

The core ES100 library fully implements all the features described in **ES100 Data Sheet - Ver 0.97**.

## Install

Use PyPi (see [package](https://pypi.python.org/pypi/es100-wwvb) for details) or GitHub (see [package](https://github.com/mahtin/es100-wwvb) for details).

### Via PyPI

```bash
    $ pip install es100-wwvb
    $
```

The sudo version of that command may be needed in some cases. YMMV

### Setting boot options and permissions on Raspberry Pi (or other similar O/S's)

The program requires access to the GPIO and I2C subsystems. The following provides that access.

```bash
$ sudo adduser pi gpio ; sudo adduser pi i2c
Adding user `pi' to group `gpio' ...
Adding user pi to group gpio
Done.
Adding user `pi' to group `i2c' ...
Adding user pi to group i2c
Done.
$

$ id
uid=1000(pi) gid=1000(pi) groups=...,997(gpio),998(i2c),...
$
```
Additionally, like all uses of the `adduser` command, the user should logout and log back in for this to take effect; however, the following step will force that action.

For GPIO on a Raspberry Pi, adding this package does everything required.
```bash
$ sudo apt-get install rpi.gpio
...
$
```

On the Raspberry Pi, the `raspi-config` command should be used to enable the I2C subsystem.
Click on `Interface Options` and then `Advanced Options`.
There you will see an `I2C` option.
Enable it.
Exit.
```bash
$ sudo raspi-config
...
$
```
A reboot is required via the `sudo reboot now` command for this to take effect..

## NTP support

The `wwvb` command line tool provides support for setting the system time via `ntpd`'s shared memory driver.
The short instructions are:

Add a shared memory server to `/etc/ntp.conf` file.
```
server 127.127.28.2
fudge 127.127.28.2 time1 0.0 time2 0.0 stratum 0 refid WWVB flag4 1
```

The `.2` at the end of the address tells `ntpd` pick a shared memory segment that's `2` above the base value of `0x4E545030`.
If you use `0` or `1` for the unit number; then the shared memory area is only readable as `root`.
This is not recommended in any way; hence the reason to recommend `2` (or above) as those are read/write by any user.
See https://www.ntp.org/documentation/drivers/driver28/ for the full details.

Then add `--ntpd=2` to the running version of `wwvb`.
```bash
$ wwvb -v -n --ntpd=2
```
See the section on setting location, as latency from WWVB is important to calculate correctly.

See the section of `wwvb.ini` configuration file.

## Hardware
This code requires a [UNIVERSAL-SOLDER® Everset® ES100-MOD WWVB-BPSK Receiver Module V1.1](https://universal-solder.ca/downloads/EverSet_ES100-MOD_V1.1.pdf) board/chipset and antenna(s).

> ES100-MOD is a receiver module for the phase-modulated time signal broadcasted by the NIST radio
> station WWVB near Fort Collins, Colorado, and is based on Everset® Technology’s fully
> self-contained receiver-demodulator-decoder Chip ES100.

![](https://github.com/mahtin/es100-wwvb/raw/main/images/universal-solder-everset-es100-wwvb-starter-kit.png)

Ordering from [UNIVERSAL-SOLDER](https://universal-solder.ca/product-category/atomic-clock-radio-receiver/), along with more information, can me found here:

* The chipset: [EverSet ES100-MOD WWVB BPSK Phase Modulation Receiver Module](https://universal-solder.ca/product/everset-es100-mod-wwvb-bpsk-phase-modulation-receiver-module/) presently at C$22.90
* The starter kit: [EverSet ES100 WWVB BPSK Atomic Clock Starter Kit](https://universal-solder.ca/product/everset-es100-wwvb-starter-kit/) presently at C$34.90
* The full Arduino-based board: [Application Development Kit for EverSet ES100-MOD Atomic Clock Receiver](https://universal-solder.ca/product/canaduino-application-development-kit-with-everset-es100-mod-wwvb-bpsk-atomic-clock-receiver-module/) presently at C$59.90

The starter kit is the easiest way to get up-n-running with this software.

Information about the chip's reception process and operational configuration can be found via [Everset Technologies](https://everset.tech/receivers/):

* Everset [ES100 Data Sheet – Ver 0.97](https://everset.tech/wp-content/uploads/2014/11/ES100DataSheetver0p97.pdf)
* Everset [Antenna Considerations](https://everset.tech/wp-content/uploads/2014/11/AN-005_Everset_Antenna_Considerations_rev_1p1.pdf)
* EverSet [ES100 Energy Consumption Minimization](https://everset.tech/wp-content/uploads/2014/11/AN-002_ES100_Energy_Consumption_Minimization_rev_2p1.pdf)

EverSet is a fabless IC company (based in Richardson, Texas).
UNIVERSAL-SOLDER (based in Yorkton Saskatchewan Canada) is the exclusive maker of receiver kits.

[1] Image and PDF's are Copyright UNIVERSAL-SOLDER Electronics Ltd. 2016-2022. All Rights Reserved.

## Wiring

The ES100 connections are:

* ES100 Pin 1 == VCC 3.6V (2.0-3.6V recommended)
* ES100 Pin 2 == IRQ Interrupt Request
* ES100 Pin 3 == SCL
* ES100 Pin 4 == SDA
* ES100 Pin 5 == EN Enable
* ES100 Pin 6 == GND

![](https://github.com/mahtin/es100-wwvb/raw/main/images/raspberry-pi-es100-wiring-diagram.png)

It's recommended that IRQ goes to GPIO-17 (pin 11) and EN goes to GPIO-4 (pin 7). This can be changed via command line arguments.

## Radio Station WWVB

[WWVB](https://www.nist.gov/pml/time-and-frequency-division/time-distribution/radio-station-wwvb) is located in Ft Collins Colorado USA and is operated by [NIST](https://www.nist.gob/).
To quote the website:
> WWVB continuously broadcasts digital time codes on a 60 kHz carrier that may serve as a stable frequency
> reference traceable to the national standard at NIST. The time codes are synchronized with the 60 kHz
> carrier and are broadcast continuously in two different formats at a rate of 1 bit per second using pulse
> width modulation (PWM) as well as phase modulation (PM).

### Further reading

* https://www.nist.gov/pml/time-and-frequency-division/time-distribution/radio-station-wwvb
* https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=914904

### Location
To use the service; you will need to be within receiving distance (see below) of WWVB in [WWVB, 5701 CO-1, Fort Collins, Colorado 80524](https://goo.gl/maps/KgRn1jDmJ3zSUfxx7).

It's geographic coordinates are: `40.678062N, 105.046688W`; however, to be be more accurate; there are two antennas as follows:

* North antenna coordinates: `40° 40' 51.3" N, 105° 03' 00.0" W` == `40.680917 N, 105.050000 W`
* South antenna coordinates: `40° 40' 28.3" N, 105° 02' 39.5" W` == `40.674528 N, 105.044306 W`

## Speed of radio waves ...
Light (or radio waves) travel at the speed of light (or close to the speed of light).
In order to know your own accurate time; you need to know the speed of the signal and the distance from the transmitter.
Speed of ground level radio waves was explained in the 1950 paper [The Speed of Radio Waves and Its Importance in Some Applications](https://ieeexplore.ieee.org/document/1701081) by R.L. Smith-Rose Department of Scientific and Industrial Research, Radio Research Station, DSIR, Slough, UK.

The key number from the paper are:

* `299,775 km/s` in a vacuum
* `299,250 km/s` for 100 Khz at ground level
* `299,690 km/s` for cm waves
* `299,750 km/s` for aircraft at 30,000 feet (9,800 meters)

I choose `299,250 km/s` as that matches the WWVB configuration as close as needed.

## Best propagation is during nighttime
This code calculates if the transmitter and receiver are at nighttime or not.
This could help decide if the receiver can produce a result. Very Long Wavelength signals propagate better at night.

The 2014 paper [WWVB Time Signal Broadcast: A New Enhanced Broadcast Format and Multi-Mode Receiver](https://www.nist.gov/publications/wwvb-time-signal-broadcast-new-enhanced-broadcast-format-and-multi-mode-receiver) [1] provides a diagram of the potential propagation of the WWVB signal.
It's calculated for 2am (i.e. middle of night).

![](https://github.com/mahtin/es100-wwvb/raw/main/images/figure1-simulated-coverage-area-for-the-legacy-WWVB-broadcast.png)

> **Figure 1.** Simulated coverage area for the legacy WWVB broadcast at 0800
> UTC (Coordinated Universal Time) in October, where the shaded area is
> the day-night boundary. The simulated coverage assumes the use of a
> properly oriented antenna and the absence of interference and shielding
> losses. These three assumptions are often invalid in indoor applications.

[1] Lowe, J. , Liang, Y. , Eliezer, O. and Rajan, D. (2014), WWVB Time Signal Broadcast: A New Enhanced Broadcast Format and Multi-Mode Receiver, IEEE Communications Magazine, [online], https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=915289 (Accessed March 5, 2023)

Antenna placement and orientation is vital in order to receive a signal. Indoors with a noisy RF environment will limit reception. Have either one antenna perfectly oriented with the WWVB transmitter site; however, that means the other antenna will not receive anything. A better plan is to have the two antennas splitting the direction - that way, both antennas can work.

This is my reception in California during daytime/nighttime.

![](https://github.com/mahtin/es100-wwvb/raw/main/images/antenna-1-vs-2-vs-local-time-of-day.png)

Clearly, my antenna placement is biased towards antenna 1. Local interference could also affect how each antenna performs.

The program calculates and prints the direction to point (in degrees clockwise from North) for optimum reception.

## Time transmission times

**NIST**'s **WWVB** 60 Khz signal broadcasts 24/7. However, during the hour cycle, the PM (Phase Modulation) signal changes as follows [1]:

> Every half-hour, for a duration of six minutes, the normal WWVB-PM 1-minute frames are replaced by the WWVBPM
> extended-mode time code sequences. The ES100 is not capable of receiving during these six-minute intervals that
> occur from HH:10 to HH:16 and HH:40 to HH:46 each hour (i.e. HH= 00, 01,…, 23).

This means you should not expect to see full reception or time for 5 minutes plus 5 minutes per hour.
Presently the code does not take this into account; it just keeps trying to receive.
As power consumption isn't a prime factor for a Raspberry Pi based systems, this is not a large issue.

[1] EverSet [ES100 Energy Consumption Minimization](https://everset.tech/wp-content/uploads/2014/11/AN-002_ES100_Energy_Consumption_Minimization_rev_2p1.pdf)

## System time vs WWVB receive time

It is assumed that any modern-day Linux environment has a stable clock and also runs some form of NTP (Network Time Protocol) such that the system time is pretty close to the real time.
The code uses that fact to manage the tracking mode reception.

## Getting Started

The package comes with a command line tool called **wwvb**.
This provides a way to run the ES100 hardware in continuous mode while printing the received date and time upon a successful decode by the hardware.
There are various command options. This example shows how a location (as in Lat/Long) can be passed on the command line.
```bash
    $ wwvb -l 39.861667N,104.673056W
    The great circle distance to WWVB: 1501.6 Km and direction is 70.6 degrees; hence latency 5.018 Milliseconds
    ...
    WWVB: 2023-03-04 12:58:22.005018+00:00
    WWVB: 2023-03-04 13:00:36.005018+00:00
    WWVB: 2023-03-04 13:05:04.005018+00:00
    WWVB: 2023-03-04 13:07:18.005018+00:00
    ...
    ^C
    $
```
Full usage of the command line tool can be found with the `--help` option:
```bash
    $ wwvb --help
    usage: wwvb [-V|--version] [-h|--help] [-v|--verbose] [-d|--debug] [-b|--bus={0-1}] [-a|--address={8-127}] [-i|--irq={1-40}] [-e|--en={1-40}] [-l|--location=lat,long] [-m|--masl={0-99999}] [-n|--nighttime] [-t|--tracking] [-A|--antenna={0-1}] [-N|--ntpd={0-255}]

    $
```

The `--bus` and `--address` options refer to the **i2c** bus position for the ES100 module. These rarely change and in fact are presently unused.
The `--irq` and `--en` options are needed if you connect the ES100 module differently than shown above. Any available GPIO port can be used.
Note that if the lines are wired incorrectly the program will simply hang.
The `--location` and `--masl` provide locations and MASL (Meters Above Sea Level) information.

The `--location` is required as the program needs to know its accurate location in order to calculate latency. If you don't provide it, your time could be off by many milliseconds. Available formats so far are:
```bash
  --location 37.4,-121.9
  --location 37.363056,-121.928611
  --location 37.363056N,121.928611W
```
If a location is not provided; then it defaults to my local airport: **SJC** (San José Mineta International Airport). This is possibly incorrect.

The `--nighttime` option enables the tracking vs reception mode logic for daytime/nighttime reception.
If the flag is not used, then full reception is operating 24/7.
This flag is normally only needed in power-saving situations.

The `--tracking` flag forces tracking reception 24/7. This will only provide second-resolution responses.

The `--antenna` flag can force the antenna to be locked into `1` or `2`.
Without this flag, the antenna swap between each reception.

The `--ntp` flag enables the setting of system time via NTP. See the NTP section above.

## Config file

The `wwvb` command will read a `wwvb.ini` configuration file, either from the current directory, your home directory or `/etc/wwvb.ini`.
This allow setting to be stored without using command line options.
If you provide a command line option, it will override the configuration file.

Here's a sample configuration file.
```bash
$ cat wwvb.ini
[WWVB]
    # I2C values
    bus = 1
    address = 50
    # GPIO pins
    irq = 11
    en = 7
    # flags,, as needed
    nighttime = False
    tracking = False
    # select where the receiver is. Add a section below to match your choice
    # SJC & Denver are simply examples
    station = SJC
    #station = Denver

[DEBUG]
    # should you want to debug anything
    debug = False
    verbose = False

[NTPD]
    # remove comment to connect to NTPD via shared memory on unit 2
    # unit = 2

[SJC]
    # Where's our receiver?
    name = San José Mineta International Airport
    location = [37.363056, -121.928611]
    masl = 18.9
    antenna =

[Denver]
    # If we had a receiver in Colorado, this is its information
    name = Colorado State Capitol Building
    location = [39.7393N, 104.9848W]
    masl = 1609
    antenna =
$
```

A mimimal `wwvb.ini` file could be:
```bash
$ cat wwvb.ini
[WWVB]
    station = SJC
[SJC]
    location = [37.363056, -121.928611]
    masl = 18.9
$
```

If you are runing `wwvb` as a daemon, then the `/etc/wwvb.ini` file would be a better choice.

## Raspberry Pi Pico W

The Pico support runs without features like **NTP**, it does set the RTC (Real Time Clock) on the **Pico** based on the **WWVB** time.
At the present time, there's minimal instruction for this. See below.

![](https://github.com/mahtin/es100-wwvb/raw/main/images/raspberry-pi-pico-w-es100-mod.jpg)

To run the code on a **Raspberry Pi Pico W** using `micropython`, first clone the github repo.
```bash
$ git clone https://github.com/mahtin/es100-wwvb.git
...
$
```

Copy the `es100` and `pico` folder and it's content to `/flash` on the Pico. Producing this file layout:
```bash
$ rshell
Connecting to /dev/cu.usbmodem1101 (buffer-size 512)...
Trying to connect to REPL  connected
Retrieving sysname ... rp2
...
/Users/martin> cp -r es100 /flash/
/Users/martin> cp -r pico /flash/
/Users/martin> ls -l /flash/es100 /flash/pico
/flash/es100:
   198 Mar 22 09:49 __init__.py
 28509 Mar 22 09:50 es100.py
  4808 Mar 22 09:49 gpio_control.py
  4479 Mar 22 09:50 i2c_control.py

/flash/pico:
   259 Mar 22 09:50 board_led.py
  6418 Mar 22 09:50 datetime.py
   977 Mar 22 09:50 irq_wait_for_edge.py
  2764 Mar 22 09:50 logging.py
   254 Mar 22 09:50 main.py
  2028 Mar 22 09:50 wwvb_lite.py
/Users/martin> repl
Entering REPL. Use Control-X to exit.
>
MicroPython v1.19.1-966-g05bb26010 on 2023-03-13; Raspberry Pi Pico W with RP2040
Type "help()" for more information.
>>>
>>> import flash.pico.main
WWVB: 2023-03-22 14:20:29.000+00:00 2023-03-22 14:20:29.033+00:00 Antenna2 -0.033
WWVB: 2023-03-22 14:24:55.000+00:00 2023-03-22 14:24:55.001+00:00 Antenna2 -0.001
...
```

## Adding an OLED display to the Pico

The code includes basic code to drive an OLED I2C display.
Presently tested with an **I2C 0.96 Inch OLED I2C 128x64 Pixel Display Module** purchased from Amazon at [https://www.amazon.com/dp/B09C5K91H7](https://www.amazon.com/dp/B09C5K91H7).
This code will operate silently without that display attached.
The code expects to be wired to I2C `bus0` using pins `GP8` & `GP9` (this can be changed in code).
Refer to the `oled_display.py` file for more information.

![](https://github.com/mahtin/es100-wwvb/raw/main/images/raspberry-pi-pico-w-es100-mod-with-oled.jpg)

The display will update the screen once a WWVB signal has been received.

This software port will be expanded upon over time.

## Other ES100 projects found

Additional software is out there; here are some of what I found.
I believe my code is presently the most complete code.

UNIVERSAL-SOLDER
* https://universal-solder.ca/downloads/wwvb_bpsk_es100.zip (use `curl -O` to grab)

Fio Cattaneo Nov 2019 - es100-wwvb-refclock
* https://github.com/fiorenzo1963/es100-wwvb-refclock

Keith Greiner April 2019 - How to Receive 60 KHz Time Signals with Arduino Due and ES100 Module
* https://sites.google.com/site/wwvbreceiverwitharduino/home?authuser=0
* https://sites.google.com/site/wwvbreceiverwitharduino/home/es100_starter_code_with_amendments?authuser=0

## Author & Copyright
Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin

