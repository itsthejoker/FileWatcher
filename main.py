#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
*********************************************
 File Name: main.py
 Author: Joe Kaufeld
 Email: opensource@joekaufeld.com
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
import sys

from filewatcher.core.initialize import initialize
from filewatcher.core.filewatcher import main_loop
from filewatcher.core.console import console

console.rule("[white]FileWatcher")

if __name__ == "__main__":
    initialize()
    while True:
        try:
            main_loop()
        except KeyboardInterrupt:
            console.print()
            console.rule("[bold red]Exiting!")
            sys.exit(0)
