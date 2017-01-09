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

import click

from core.initialize import initialize
from core.filewatcher import main_loop

__version__ = '2.0.0'


@click.group()
@click.pass_context
def cli(ctx):
    '''
    This script exists to help you organize your downloads! Run by invoking the
    `run` command: python main.py run

    You can also optionally control the time delay between checks of the
    incoming folder by running it with the --delay=(number in seconds). If
    you'd like to see what it's currently doing, you can also use the --debug
    flag. Warning -- this is *very* verbose.
    '''
    pass


@click.command()
@click.option(
    '--delay', default=None, help="Amount of time to wait between scans of the "
    "incoming file directory in seconds. Defaults to 180s (three minutes)."
)
@click.option('--debug', is_flag=True)
@click.pass_context
def run(ctx, debug, delay):
    ctx.obj['DELAY'] = delay
    ctx.obj['DEBUG'] = debug

    if initialize(ctx):

        while True:
            main_loop()

cli.add_command(run)

if __name__ == "__main__":
    cli(obj={})
