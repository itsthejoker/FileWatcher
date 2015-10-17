#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
*********************************************
 File Name: movies.py
 Author: Joe Kaufeld
 Email: joe.kaufeld@gmail.com
 Purpose:
   Handles pretty much all the recognizing, renaming, and moving of movie
   files and folders.
 Credits:
   Special thanks to https://github.com/sposterkil for the regex and code
   review!
*********************************************
'''

from __future__ import print_function

import re
import os
import shutil

from initialize import settings

try:  # settings.imdb hasn't loaded yet - need to figure out why.
    import imdb
    imdb_access = imdb.IMDb()
except ImportError:
    pass

title_parser = re.compile("""
    (?P<title>[\w,.\-!'\s]+)
    \s(?:[\(\[]?
    (?P<year>(?:(?:20)|(?:19))
    \d{2})[\)\]]?)
    """, re.MULTILINE | re.VERBOSE)


def rename_skipped(directory):

    os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
              settings.incoming_dir, ("[SKIP] " + directory)))


def folder_translator(foldername, title_parser=title_parser):
    '''Uses regex to yoink the name and year out of movie titles.'''
    settings.debug_message("Running folder/name translation on {}".format(
                           foldername))

    # check to see if we're operating on a file or a folder
    if settings.get_extension(foldername) in settings.video_formats:
        extension = settings.get_extension(foldername)
        foldername = foldername[:-len(extension)].replace(".", " ")
        foldername_less_extension = foldername.replace("_", " ")
        foldername = foldername_less_extension + extension
    else:
        foldername = foldername.replace(".", " ")
        foldername = foldername.replace("_", " ")

    foldername = foldername.title()

    settings.debug_message("Now {} after replacement!".format(foldername))
    title_data = title_parser.match(foldername)

    try:
        # try and force an attribute error before it happens
        x = title_data.group("title")
        x = title_data.group("year")
    except AttributeError:
        settings.debug_message("folder_translator - AttributeError!")

        # if it's a folder, foldername_less_extension will not have been
        # created; we catch the unbound error and just use the normal folder
        # name here for that reason
        try:
            title = foldername_less_extension
        except UnboundLocalError:
            title = foldername

        if settings.imdb:
            settings.debug_message("Attempting lookup through IMDbPy!")
            settings.debug_message("IMDbPy - Searching for year of {}".format(
                                   title))
            try:
                maybe_title = imdb_access.search_movie(
                    "{}".format(title))[0]['title']
                settings.debug_message("IMDbPy - I think I found it! It's {}!".
                                       format(maybe_title))
                maybe_year = imdb_access.search_movie(
                    "{}".format(title))[0]['year']
                settings.debug_message("IMDbPy - I think I found it! It's {}!".
                                       format(maybe_year))
                settings.debug_message("IMDbPy - returning ({}, {})".format(
                    maybe_title, maybe_year))
                return(maybe_title, maybe_year)
            except (AttributeError, IndexError):
                # it can't find a title or year! Oh no! Give up for now.
                return None
        else:
            # guess it's not installed. Crap.
            return None

    return (
        title_data.group("title"),
        title_data.group("year")
        )


def rename_duplicate(directory):

    os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
              settings.incoming_dir, ("[DUPLICATE] " + directory)))


def process_root_level_movie(movie):

    translated_folder = folder_translator(movie)
    if translated_folder is not None:
        renamed_movie = "{} ({})".format(translated_folder[0],
                                         translated_folder[1])
    else:
        rename_skipped(movie)
        return

    settings.debug_message("Moving root level file {} into new folder!".format(
                           movie))
    if not os.path.isdir(os.path.join(settings.movie_dir, renamed_movie)):

        try:

            for banned_ch in settings.banned_characters:
                if banned_ch in renamed_movie:
                    renamed_movie = renamed_movie.replace(banned_ch, "")

            settings.debug_message("Creating folder for root level file {}"
                                   .format(movie))
            os.mkdir(os.path.join(settings.incoming_dir, renamed_movie))
            shutil.move(os.path.join(settings.incoming_dir, movie),
                        os.path.join(settings.incoming_dir, renamed_movie,
                                     movie))

            settings.debug_message("Moving folder to movies folder!")
            shutil.move(os.path.join(settings.incoming_dir, renamed_movie),
                        os.path.join(settings.movie_dir, renamed_movie))
            settings.debug_message("Move successful!")
        except (OSError, shutil.Error):

            print("{} is already in the destination directory! Renaming!".
                  format(renamed_movie))
            rename_duplicate(renamed_movie)
    else:

        if not os.path.isfile(os.path.join(settings.movie_dir, renamed_movie,
                                           movie)):
            try:
                shutil.move(os.path.join(settings.incoming_dir, movie),
                            os.path.join(settings.movie_dir, renamed_movie,
                                         movie))
            except shutil.Error:
                print("Something went wrong with moving {}! Skipping!".format(
                      movie))
        else:
            print("{} is already in the destination directory! Renaming!".
                  format(renamed_movie))
            if not os.path.isdir(os.path.join(settings.incoming_dir,
                                              renamed_movie)):
                os.mkdir(os.path.join(settings.incoming_dir, renamed_movie))
                shutil.move(os.path.join(settings.incoming_dir, movie),
                            os.path.join(settings.incoming_dir, renamed_movie,
                                         movie))
                rename_duplicate(renamed_movie)


def is_video_folder(directory, dir_files):
    for directory_file in dir_files:
        settings.debug_message("Testing file {} for video format!".format(directory_file))
        if settings.get_extension(directory_file) in settings.video_formats:
            settings.debug_message("Found video folder: {}".format(directory))
            return True

    settings.debug_message("Folder does not contain first level video files. Skipping.")
    return False


def is_tv_show(directory, directory_file):
    # we don't have to check the extension here because is_movie() did that
    # for us

    if (int(os.path.getsize(os.path.join(settings.incoming_dir, directory,
                                         directory_file)))/1000000) < int(
            settings.min_movie_size):
        # check to see if it's a "sample" video. I hate those.
        if is_sample(directory, directory_file):

            # this only works because I've never seen a TV directory with a
            # sample video file. If I ever find one, I'll rework this.
            return False  # not a TV directory, false alarm
        else:
            return True


def is_sample(directory, directory_file):
    if (int(os.path.getsize(os.path.join(settings.incoming_dir, directory,
                            directory_file)))/1000000) < int(
            settings.min_episode_size):
        return True
    else:
        return False


def delete_samples(directory, dir_files):
    # nuke any sample files and anything in the extensions to delete string
    # like txt files, nfo files, and jpg files
    for thing_to_delete in dir_files:
        if settings.get_extension(thing_to_delete) in settings.video_formats:
            if is_sample(directory, thing_to_delete):
                settings.debug_message("Found sample movie {}! ENGAGE LASERS"
                                       .format(thing_to_delete))
                os.remove(os.path.join(settings.incoming_dir, directory,
                          thing_to_delete))
        if settings.get_extension(thing_to_delete) in settings.exts_to_delete:
            settings.debug_message("NUKING {}".format(thing_to_delete))
            os.remove(os.path.join(settings.incoming_dir, directory,
                      thing_to_delete))


def process_tv_show(directory):
    # for now, we're just renaming the folder so we can come back and get it
    # manually. TV shows are hard, so we'll take a look at that later.
    os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
              settings.incoming_dir, ("[TV] " + directory)))


def is_movie(directory_file):
    # return true if file is a file type we're looking for

    return (settings.get_extension(directory_file) in settings.video_formats)


def process_movie(directory, dir_files, rename_and_move):

    marked_tv_dir = False
    for directory_file in dir_files:
        if is_movie(directory_file):
            if is_tv_show(directory, directory_file):
                marked_tv_dir = True

    if marked_tv_dir:
        try:
            process_tv_show(directory)
        except OSError:
            print("Encountered an issue with {}! Skipping!".format(directory))

    else:
        # we know we've got a movie, so it's time to rename and move the folder
        delete_samples(directory, dir_files)
        rename_and_move(directory)
