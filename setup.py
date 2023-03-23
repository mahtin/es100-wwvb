""" WWVB 60Khz Full functionality receiver/parser for i2c bus based ES100-MOD

A time and date decoder for the ES100-MOD WWVB receiver.
See README.md for detailed/further reading.

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

import re
from distutils.core import setup

with open('es100/__init__.py', 'r') as f:
    _version_re = re.compile(r"__version__\s=\s'(.*)'")
    version = _version_re.search(f.read()).group(1)

with open('README.md') as f:
    long_description = f.read()

setup(
    name = 'es100-wwvb',
    packages = ['es100', 'wwvb'],
    version = version,
    license = 'OSI Approved :: MIT License',
    description = 'WWVB 60Khz Full functionality receiver/parser for i2c bus based ES100-MOD receiver',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Martin J Levy',
    author_email = 'mahtin@mahtin.com',
    url = 'https://github.com/mahtin/es100-wwvb',
    download_url = 'https://github.com/mahtin/es100-wwvb/archive/refs/tags/%s.tar.gz' % version,
    keywords = ['WWVB', 'ES100', 'NIST', 'Time', 'Time Synchronization', 'VLW', 'Very Long Wavelength', 'NTP'],
    install_requires = ['smbus', 'ephem', 'RPi.GPIO','sysv_ipc'],
    options = {"bdist_wheel": {"universal": True}},
    include_package_data = True,
    entry_points = {'console_scripts': ['wwvb=wwvb.__main__:main']},
    python_requires=">=3.7",

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Communications :: Ham Radio',
        'Topic :: System :: Networking :: Time Synchronization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
