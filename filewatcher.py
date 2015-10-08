#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
*********************************************
 File Name: filewatcher.py
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

import os
import time
import shutil
import sys

from initialize import settings
from movies import (is_video_folder,
                    process_movie,
                    rename_duplicate,
                    folder_translator,
                    rename_skipped,
                    process_root_level_movie)


def debug_message(message):

    if settings.debug:
        print("DEBUG - {}".format(message), file=sys.stderr)

settings.debug_message = debug_message


def in_use(test_file):

    # yes, possible race condition, but due to the system we're putting this
    # into race conditions will not be an issue.

    try:
        os.rename(test_file, test_file+"_")
        settings.debug_message("Testing to see if {} is in use".format(test_file))
        os.rename(test_file+"_", test_file)
        settings.debug_message("Not in use! Proceed!")
        return False
    except OSError:
        settings.debug_message("File in use!")
        return True

settings.in_use = in_use


def get_extension(filename):

    last_dot = filename.rfind('.')
    # if rfind fails, it returns -1
    if last_dot > 0:
        return filename[last_dot:]
    else:
        return None

settings.get_extension = get_extension


def move_folder(new_directory):
    if new_directory is None:
        settings.debug_message("Something went wrong! Skipping!")
    else:
        if not os.path.isdir(os.path.join(settings.movie_dir, new_directory)):

            try:
                shutil.move(os.path.join(settings.incoming_dir, new_directory),
                            os.path.join(settings.movie_dir, new_directory))
                settings.debug_message("Move successful! Folder {} now located at {}".
                                       format(new_directory, settings.movie_dir +
                                              new_directory))
            except (OSError, shutil.Error):
                print("{} is already in the destination directory! Renaming!".
                      format(new_directory))
                rename_duplicate(new_directory)
        else:
            print("{} is already in the destination directory! Renaming!".
                  format(new_directory))
            rename_duplicate(new_directory)


def rename_folder(directory):
    settings.debug_message("Attempting rename of parent folder!")

    if folder_translator(directory) is None:
        print("{} has an issue I can't recover from. Skipping!".format(directory))
        try:
            rename_skipped(directory)
        except OSError:
            settings.debug_message("{} is locked by the OS. Skipping!".format(directory))
            pass
    else:
        new_directory = "{} ({})".format(folder_translator(directory)[0],
                                         folder_translator(directory)[1])
        try:
            os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
                      settings.incoming_dir, new_directory))
            settings.debug_message("Rename successful!")
        except OSError:
            settings.debug_message("Access denied while trying to rename {}!".format(
                                   new_directory))
            return None

        return new_directory


def rename_and_move(directory):
    new_folder = rename_folder(directory)
    if type(new_folder) is None:
        settings.debug_message("Encountered an issue with {}! Skipping!"
                               .format(directory))
    else:
        move_folder(new_folder)


def root_level_files(files):

    settings.debug_message("Found root level files: {}".format(files))
    if 'Thumbs.db' in files:
        # ignore the file; this does not delete it
        files.remove('Thumbs.db')
        settings.debug_message("Ignoring Thumbs.db")

    for prospect_file in files:
        if settings.get_extension(prospect_file) in settings.video_formats:
            if not settings.in_use(os.path.join(settings.incoming_dir,
                                                prospect_file)):
                process_root_level_movie(prospect_file)

        # if settings.get_extension(prospect_file) in settings.audio_formats:
        #     if not settings.in_use(os.path.join(settings.incoming_dir,
        #                                         prospect_file)):
        #         process_root_level_audio(prospect_file)


def process_folders(dirs):
    for directory in dirs:
        settings.debug_message("Switching to directory {}".format(directory))

        if "[TV]" in directory:
            settings.debug_message("Found previously scanned TV folder. Skipping!")
        elif "[DUPLICATE]" in directory:
            settings.debug_message("Found previously scanned duplicate directory. "
                                   "Skipping!")
        elif "[SKIP]" in directory:
            settings.debug_message("Found previously scanned skipped directory."
                                   " Skipping again!")
        else:

            dir_files = [f for f in os.listdir(os.path.join(settings.
                         incoming_dir, directory)) if
                         os.path.isfile(os.path.join(settings.incoming_dir,
                                        directory, f))]
            try:
                if not in_use(os.path.join(settings.incoming_dir, directory,
                              dir_files[0])):
                    settings.debug_message("Folder is good to go - time to see if "
                                           "it's a video folder!")
                    if is_video_folder(directory, dir_files):
                        process_movie(directory, dir_files, rename_and_move)
                    else:
                        settings.debug_message("Folder does not appear to be a movie."
                                               "Skipping.")
            except IndexError:
                dir_folders = [f for f in os.listdir(os.path.join(settings.
                               incoming_dir, directory)) if os.path.isdir(
                               os.path.join(settings.incoming_dir,
                                            directory, f))]

                if dir_folders[0].lower() == "video_ts":
                    rename_and_move(directory)

            else:
                settings.debug_message("Can't use folder! Moving to next folder.")


def status_update(message):
    sys.stdout.write(message)
    sys.stdout.flush()


def main_loop():
    # search directories and start figuring out what's what
    # returns first level folder names under dir

    dirs = [x for x in os.listdir(settings.incoming_dir) if os.path.isdir(
            os.path.join(settings.incoming_dir, x))]
    settings.debug_message("Found directories: {}".format(dirs))

    process_folders(dirs)

    # check for files that aren't under their own folders for some
    # godforsaken reason
    files = [f for f in os.listdir(settings.incoming_dir) if os.path.
             isfile(os.path.join(settings.incoming_dir, f))]

    if files is not []:
        root_level_files(files)

    settings.debug_message("Sleeping for {} seconds!".format(settings.delay_time))

    status_update("Sleeping for {} seconds!\r".format(settings.delay_time))
    time.sleep(int(settings.delay_time))
    status_update("Working...                  \r")
