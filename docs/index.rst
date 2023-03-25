..
  Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin

.. es100-wwvb documentation master file, created by
  sphinx-quickstart on Tue Mar 14 10:46:25 2023.
  You can adapt this file completely to your liking, but it should at least
  contain the root `toctree` directive.

A time and date decoder for the ES100-MOD WWVB receiver
=======================================================

WWVB 60Khz Full funcionality receiver/parser for i2c bus based ES100-MOD.

Description
===========

A time and date decoder for the ES100-MOD WWVB receiver.
This code implements tracking (for daytime reception) and full receive decoding (for nighttime reception).
It provides Daylight Saving information and Leap Second information, if WWVB provides it.

It's written 100% in Python and tested on the Raspberry Pi4 and on the Raspberry Pi Pico W (using `micropython`) with, or without an OLED display.

The core ES100 library fully implements all the features described in ES100 Data Sheet - Ver 0.97.


.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
