#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
*********************************************
 File Name: main.py
 Author: Joe Kaufeld
 Email: joe.kaufeld@gmail.com
 Purpose:
   Handles identification of music folders and tries to get them to the right
   place. Known issues: cannot handle discographies or multiple albums under
   one artist.
 Credits:
   Special thanks to https://github.com/sposterkil for the regex and code
   review!
*********************************************
'''

from __future__ import print_function

from initialize import settings


def is_audio_folder(directory, dir_files):
    for directory_file in dir_files:
        settings.debug_message("Testing file {} for audio format!".format(directory_file))
        if settings.get_extension(directory_file) in settings.audio_formats:
            settings.debug_message("Found audio folder: {}".format(directory))
            return True
        else:
            settings.debug_message("Folder does not contain first level audio files. Skipping.")
            return False


def process_audio(directory):
    #  placeholder. Right now there's nothing to process because we just move
    #  stuff.
    pass
