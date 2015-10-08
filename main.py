#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
*********************************************
 File Name: main.py
 Author: Joe Kaufeld
 Email: joe.kaufeld@gmail.com
 Purpose:
   Continuously scans a directory where new files are added automatically, make
   sure they're not currently in use, then try to identify them based on file
   type, number, and size. It uses that information to attempt placing them
   in the right final directory.
 Credits:
   Special thanks to https://github.com/sposterkil for the regex and code
   review!
*********************************************
'''

from __future__ import print_function

from initialize import initialize
from filewatcher import main_loop

__version__ = 1.2


def main():

    if initialize(version=__version__):

        # Primary
        while True:
            main_loop()

if __name__ == "__main__":
    main()
