""" main()

Copyright (C) 2023 Martin J Levy - W6LHI/G8LHI - @mahtin - https://github.com/mahtin
"""

# This is key - once done, all the imports work
import os
os.chdir('/flash')

from pico.wwvb_lite import wwvb_lite

def main():
    wwvb_lite()

main()
