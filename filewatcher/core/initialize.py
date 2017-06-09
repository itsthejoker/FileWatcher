#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
*********************************************
 File Name: initialize.py
 Author: Joe Kaufeld
 Email: joe.kaufeld@gmail.com
 Purpose:
   Loads in the config file or generates it if necessary.
 Credits:
   Special thanks to https://github.com/sposterkil for the regex and code
   review!
*********************************************
'''

import os
import random
import sys
import textwrap

import click
from configobj import ConfigObj

from filewatcher.core import init_phrases
from filewatcher.core import init_endings
from filewatcher.core import settings


def generate_config(updated_config=False):
    config = ConfigObj()
    config.filename = 'config.ini'

    config['Info'] = {}
    config['Info'].comments.update(
        {'Info': ['# For themeing purposes!'], 'key': ['application_name']}
    )
    config['Info']['application_name'] = settings.app_name
    config['Info'].comments.update(
        {'Info': ['# Delay between filesystem checks - default is 180 '
         'seconds.'], 'key': ['delay_time']}
    )
    config['Info']['delay_time'] = settings.delay_time

    config['Directories'] = {}
    config['Directories'].comments.update(
        {'Directories': ['# Example: "C:\Things" or "/Users/[you]/Things"'],
            'key': []})
    config['Directories']['incoming_directory'] = settings.incoming_dir
    config['Directories']['movie_directory'] = settings.movie_dir
    config['Directories']['audio_directory'] = settings.audio_dir

    config['File Information'] = {}
    config['File Information'].comments.update(
        {'File Information': ['# All file sizes are in MB!',
                              '# The program assumes that all files under a'
                              '# size threshold are actually TV shows.'],
            'key': []
         }
    )
    config['File Information']['minimum_movie_size'] = settings.min_movie_size

    config['File Information'].comments.update(
        {'File Information': ['# For auto-deleting crap promo videos'],
         'key': ['minimum_episode_size']}
    )
    config['File Information']['minimum_episode_size'] = \
        settings.min_episode_size

    config['File Information'].comments.update(
        {'File Information': ['# List of file extensions worthy of being',
                              '# immediately deleted.'],
         'key': ['extensions_to_delete']}
    )
    config['File Information']['extensions_to_delete'] = settings.exts_to_delete

    config['File Information']['video_formats'] = settings.video_formats
    config['File Information']['audio_formats'] = settings.audio_formats

    config.write()

    config_nonexist_error = textwrap.fill(
        'Configuration not found, a default config.ini was created.'
        'You must edit it before using this script.\n'
        'Application exiting.',
        width=70
    )

    config_out_of_date_error = textwrap.fill(
        'Configuration found is for an older version of the software. It has '
        'been backed up and a new one has been generated; please fill in the '
        'required information in the new config.ini and run the program again.',
        width=70
    )

    #  The only reason we actually perform a check here is if you have an older
    #  version of the software and we need to update the config file - that way
    #  we can just update in place and keep rolling.
    if updated_config:
        click.echo(config_out_of_date_error)
    else:
        click.echo(config_nonexist_error)

    sys.exit()


def load_config(ctx, loaded_config):
    settings.app_name = loaded_config['Info']['application_name']

    if not ctx.obj['DELAY']:
        settings.delay_time = int(loaded_config['Info']['delay_time'])
    else:
        settings.delay_time = int(ctx.obj['DELAY'])
        click.echo(
            "Overriding delay time in config for passed in delay of {}".format(
                int(ctx.obj['DELAY'])
            )
        )

    settings.debug = ctx.obj['DEBUG']

    settings.incoming_dir = loaded_config['Directories']['incoming_directory']
    settings.movie_dir = loaded_config['Directories']['movie_directory']

    settings.min_movie_size = loaded_config['File Information']['minimum_movie_size']
    settings.min_episode_size = loaded_config['File Information']['minimum_episode_size']

    settings.exts_to_delete = [
        e.strip() for e in
        loaded_config['File Information']['extensions_to_delete'].split(',')
    ]

    settings.video_formats = [
        e.strip() for e in
        loaded_config['File Information']['video_formats'].split(',')
    ]

    settings.audio_dir = loaded_config['Directories']['audio_directory']
    settings.audio_formats = [
        e.strip() for e in loaded_config['File Information']['video_formats'].split(',')
    ]

    # check validity of config entries
    for dir_checker in (settings.incoming_dir, settings.movie_dir,
                        settings.audio_dir):
        if not os.path.isdir(dir_checker):
            click.echo("Directory \"{}\" is invalid! Please check the config!"
                       "\n".format(dir_checker))
            click.echo("Exiting application.")
            sys.exit()


def initialize(ctx, settings=settings):

    # avoid circular imports
    from filewatcher.main import __version__

    set_init_phrase = random.randrange(len(init_phrases))

    # start initialization
    click.echo("{}...".format(init_phrases[set_init_phrase]))

    if os.path.isfile("./config.ini"):
        loaded_config = ConfigObj('config.ini')
    else:
        generate_config()

    load_config(ctx, loaded_config)

    click.echo(init_endings[set_init_phrase])

    click.echo("Ready to go - starting main loop!")
    click.echo("Running {}, version {}".format(settings.app_name, __version__))
    click.echo("\nIncoming file directory: {}".format(settings.incoming_dir))
    click.echo("Movie directory: {}".format(settings.movie_dir))
    click.echo("Audio directory: {}".format(settings.audio_dir))

    intro_text = (
        "Folders identified as containing movies (along with root level "
        "files) will be moved to the movie directory. Folders identified "
        "as containing TV shows will have their parent folder renamed to "
        "have [TV] in front of it and otherwise left alone."
    )

    click.echo()  # blank line
    click.echo(textwrap.fill(intro_text, width=70))

    #  successful init!
    return True
