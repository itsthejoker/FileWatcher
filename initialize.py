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

if sys.version_info.major < 3:
    import ConfigParser as configparser
else:
    import configparser


class settings:
    pass

settings = settings()


def generate_config():

    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.ini')

    config.add_section('Info')
    config.set('Info', '; For themeing purposes!')
    config.set('Info', 'application_name', 'FileWatcher')
    config.set('Info', "; Delay between filesystem checks - default is 180 "
               "seconds.")
    config.set('Info', 'delay_time', '180')
    config.set('Info', '; Print the debug information? There\'s a lot, so '
               'don\'t turn')
    config.set('Info', ';     this on unless you really want to.')
    config.set('Info', 'debug', False)

    config.add_section('Directories')
    config.set('Directories', '; Example: "C:\Things"')
    config.set('Directories', 'incoming_directory', 'C:\--INCOMING--')
    config.set('Directories', 'movie_directory', 'C:\Movies')

    config.add_section('File Information')
    config.set('File Information', '; All file sizes are in MB!')
    config.set('File Information', '; The program assumes that all files under'
               ' a size threshold')
    config.set('File Information', ';     are actually TV shows.')
    config.set('File Information', 'minimum_movie_size', '650')
    config.set('File Information', '; For auto-deleting crap promo videos')
    config.set('File Information', 'minimum_episode_size', '25')
    # config.set('File Information', '; ')
    # config.set('File Information', '; Minimum number of video files to trigger '
    #            'the TV algorithm')
    # config.set('File Information', 'minimum_video_files', 2)
    config.set('File Information', '; ')
    config.set('File Information', '; List of file extensions worthy of being '
               'immediately deleted')
    config.set('File Information', ';     from a video folder.')
    config.set('File Information', 'extensions_to_delete', '.nfo, .txt, .jpg')
    config.set('File Information', 'video_formats', '.avi, .mkv, .mp4')
    # config.set('File Information', 'subtitle_formats', '.sub, .ssf, .srt, '
    #            '.ssa, .ass, .usf, .idx')

    with open('config.ini', 'w') as f:
        config.write(f)

    config_nonexist_error = 'Configuration not found, a default config.ini '\
                            'was created.\n'\
                            'You must edit it before using this script.\n\n'\
                            'Application exiting.'

    print(config_nonexist_error)
    sys.exit()


def initialize(version, settings=settings):

    #  useless, but fun!
    init_phrases = ('Reticulating splines', 'Murdering zombies',
                    'Initializing', 'Bringing MAXIS back',
                    'Engaging warp drive', 'Telling future',
                    'Preparing fart', 'Building pyramids',
                    'Making \'fetch\' happen')

    init_endings = ('Splines reticulated!', 'Zombies murdered!',
                    'Initialized!', "I tried :'(", 'Warp drive engaged!',
                    'Future told! ...I think.', '...Heh.', 'Pyramids built!',
                    'That is /so/ fetch.')

    set_init_phrase = random.randrange(len(init_phrases))

    # start initialization
    print("{}...".format(init_phrases[set_init_phrase]))

    config = configparser.ConfigParser(allow_no_value=True)

    if os.path.isfile("./config.ini"):
        config.read('config.ini')
    else:
        generate_config()

    # read configuration file
    settings.app_name = config.get('Info', 'application_name')
    settings.delay_time = int(config.get('Info', 'delay_time'))
    settings.debug = config.getboolean('Info', 'debug')

    settings.incoming_dir = config.get('Directories', 'incoming_directory')
    settings.movie_dir = config.get('Directories', 'movie_directory')

    settings.min_movie_size = config.get('File Information',
                                         'minimum_movie_size')
    settings.min_episode_size = config.get('File Information',
                                           'minimum_episode_size')
    # not implemented yet
    # settings.min_video_files = config.get('File Information',
    #                                       'minimum_video_files')

    settings.exts_to_delete = [e.strip() for e in config.get(
                               'File Information', 'extensions_to_delete').
                               split(',')]

    settings.video_formats = [e.strip() for e in config.get('File Information',
                              'video_formats').split(',')]
    # not implemented yet
    # settings.subtitle_formats = [e.strip() for e in config.get(
    #                              'File Information', 'subtitle_formats').
    #                              split(',')]

    # check validity of config entries
    for dir_checker in (settings.incoming_dir, settings.movie_dir):
        if not os.path.isdir(dir_checker):
            print("Directory \"{}\" is invalid! Please check the config!\n".
                  format(dir_checker))
            print("Exiting application.")
            sys.exit()

    print(init_endings[set_init_phrase])
    print("Ready to go - starting main loop!")
    print("Running {}, version {}".format(settings.app_name, version))
    print("\nIncoming file directory: {}".format(settings.incoming_dir))
    print("Movie directory: {}".format(settings.movie_dir))
    print("\nFolders identified as containing movies (along with root level "
          "files)\nwill be moved to the movie directory. Folders identified "
          "as containing\nTV shows will have their parent folder renamed to "
          "have [TV] in front of\nit and otherwise left alone.\n")

    #  successful init!
    return True
