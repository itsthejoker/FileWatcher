#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
*********************************************
 File Name: filewatcher.py
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
"""

from __future__ import print_function

import os
import shutil
import time
from typing import Optional

from filewatcher.core import (
    StatusTag,
    settings,
    get_files,
    get_folders,
    get_root_files,
    get_root_directories,
)
from filewatcher.movies.movies import (
    is_video_folder,
    process_movie,
    rename_duplicate,
    rename_skipped,
    folder_translator,
    process_root_level_movie,
)
from filewatcher.core.console import console

# from audio.music import is_audio_folder


def debug_message(message: str) -> None:
    if settings.debug:
        console.log(message)


settings.debug_message = debug_message


def in_use(test_file: str) -> bool:
    # yes, possible race condition, but due to the system we're putting this
    # into race conditions will not be an issue.

    try:
        settings.debug_message("Testing to see if {} is in use".format(test_file))
        os.rename(test_file, test_file + "_")
        os.rename(test_file + "_", test_file)
        settings.debug_message("Not in use! Proceed!")
        return False
    except OSError:
        settings.debug_message("File in use!")
        return True


settings.in_use = in_use


def get_extension(filename: str) -> Optional[str]:
    last_dot = filename.rfind(".")
    # if rfind fails, it returns -1
    if last_dot > 0:
        return filename[last_dot:]
    else:
        return None


settings.get_extension = get_extension


def move_folder(new_directory: str, dir_type="movie") -> None:
    if dir_type is "movie":
        settings_dir = settings.movie_dir
    elif dir_type is "audio":
        settings_dir = settings.audio_dir
    else:
        raise Exception(f"Cannot continue; unknown dir type {dir_type}!")

    if new_directory is None:
        settings.debug_message("Something went wrong! Skipping!")
    else:
        if not os.path.isdir(os.path.join(settings_dir, new_directory)):
            try:
                shutil.move(
                    os.path.join(settings.incoming_dir, new_directory),
                    os.path.join(settings_dir, new_directory),
                )
                settings.debug_message(
                    "Move successful! Folder {} now located at {}".format(
                        new_directory, os.path.join(settings_dir, new_directory)
                    )
                )
            except (OSError, shutil.Error):
                print(
                    f"{new_directory} is already in the destination directory! Renaming!"
                )
                rename_duplicate(new_directory)
        else:
            print(
                "{} is already in the destination directory! Renaming!".format(
                    new_directory
                )
            )
            rename_duplicate(new_directory)


def rename_folder(directory: str) -> Optional[str]:
    settings.debug_message("Attempting rename of parent folder!")

    translated_folder = folder_translator(directory)

    if translated_folder is None:
        print(f"{directory} has an issue I can't recover from. Skipping!")
        try:
            rename_skipped(directory)
        except OSError:
            settings.debug_message(f"{directory} is locked by the OS. Skipping!")
    else:
        title, year = translated_folder
        new_directory = f"{title} ({year})"
        try:
            os.rename(
                os.path.join(settings.incoming_dir, directory),
                os.path.join(settings.incoming_dir, new_directory),
            )
            settings.debug_message("Rename successful!")
        except OSError:
            settings.debug_message(
                f"Access denied while trying to rename {new_directory}!"
            )
            return None

        return new_directory


def rename_and_move(directory: str) -> None:
    new_folder = rename_folder(directory)
    if type(new_folder) is None:
        settings.debug_message(f"Encountered an issue with {directory}! Skipping!")
    else:
        move_folder(new_folder)


def root_level_files(files):
    settings.debug_message(f"Found root level files: {files}")

    files = [f for f in files if f not in settings.filenames_to_ignore]

    for prospect_file in files:
        if not check_for_skips(prospect_file):
            if get_extension(prospect_file) in settings.video_formats:
                if not settings.in_use(
                    os.path.join(settings.incoming_dir, prospect_file)
                ):
                    process_root_level_movie(prospect_file)

        # if get_extension(prospect_file) in settings.audio_formats:
        #     if not settings.in_use(os.path.join(settings.incoming_dir,
        #                                         prospect_file)):
        #         process_root_level_audio(prospect_file)


def check_for_skips(item: str) -> bool:
    if StatusTag.TV in item:
        settings.debug_message("Found previously scanned TV folder. Skipping!")
        return True
    elif StatusTag.DUPLICATE in item:
        settings.debug_message(
            "Found previously scanned duplicate directory. Skipping!"
        )
        return True
    elif StatusTag.SKIP in item:
        settings.debug_message(
            "Found previously scanned skipped directory. Skipping again!"
        )
        return True
    else:
        return False


def process_folders(dirs):
    for directory in dirs:
        settings.debug_message(f"Switching to directory {directory}")

        if not check_for_skips(directory):

            dir_files = get_files(directory)

            try:
                if not in_use(
                    os.path.join(settings.incoming_dir, directory, dir_files[0])
                ):
                    settings.debug_message(
                        "Folder is good to go - time to see if it's a video folder!"
                    )
                    if is_video_folder(directory, dir_files):
                        process_movie(directory, dir_files, rename_and_move)
                    else:
                        settings.debug_message(
                            "Folder does not appear to be a movie. Skipping."
                        )

                    # if is_audio_folder(directory, dir_files):
                    #     #  There will eventually be a process_audio() function
                    #     #  here, but for now we just need to move stuff.
                    #     move_folder(directory, 'audio')
                    # else:
                    #     settings.debug_message(
                    #         "Folder does not appear to be an album. Skipping."
                    #     )

            except IndexError:
                try:
                    dir_folders = get_folders(directory)

                    if "video_ts" in dir_folders:
                        rename_and_move(directory)

                except IndexError:
                    settings.debug_message(
                        "Folder appears to be empty. Will mark as skip and move on."
                    )
                    rename_skipped(directory)

            else:
                settings.debug_message("Can't use folder! Moving to next folder.")


def main_loop():
    # search directories and start figuring out what's what
    # returns first level folder names under dir

    dirs = get_root_directories()
    settings.debug_message("Found directories: {}".format(dirs))

    process_folders(dirs)

    # check for files that aren't under their own folders for some
    # godforsaken reason
    files = get_root_files()

    if files is not []:
        root_level_files(files)

    settings.debug_message("Sleeping for {} seconds!".format(settings.delay_time))

    console.print(f"Sleeping for {settings.delay_time} seconds!\r")
    time.sleep(int(settings.delay_time))
    console.print("Working...                  \r")
