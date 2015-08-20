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

__version__ = 1.0

import os
import shutil
import random
import sys
import time
import re
import ConfigParser as configparser

title_parser = re.compile("""
    (?P<title>[\w,.\-!'\s]+)
    \s(?:[\(\[]?
    (?P<year>(?:(?:20)|(?:19))
    \d{2})[\)\]]?)
    """, re.MULTILINE | re.VERBOSE)


class settings:
    pass


def generate_config():

    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.ini')

    config.add_section('Info')
    config.set('Info', '; For themeing purposes!')
    config.set('Info', 'application_name', 'FileWatcher')
    config.set('Info', "; Delay between filesystem checks - default is 180 "
               "seconds.")
    config.set('Info', 'delay_time', 180)
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
    config.set('File Information', 'minimum_movie_size', 650)
    config.set('File Information', '; For auto-deleting crap promo videos')
    config.set('File Information', 'minimum_episode_size', 25)
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

    config_nonexist_error = 'Configuration not found, a default config.ini was'\
                            ' generated.\n'\
                            'You must edit it before using this script.\n\n'\
                            'Application exiting.'

    print(config_nonexist_error)
    sys.exit()


def debug_message(message):

    if settings.debug:
        print("DEBUG - {}".format(message), file=sys.stderr)


def rename_skipped(directory):

    os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
              settings.incoming_dir, ("[SKIP] " + directory)))


def folder_translator(foldername, title_parser=title_parser):
    '''Uses regex to yoink the name and year out of movie titles.'''
    debug_message("Running folder/name translation on {}".format(foldername))

    # check to see if we're operating on a file or a folder
    if get_extension(foldername) in settings.video_formats:
        extension = get_extension(foldername)
        foldername = foldername[:-len(extension)].replace(".", " ")
        foldername = foldername + extension
    else:
        foldername = foldername.replace(".", " ")

    debug_message("Now {} after replacement!".format(foldername))
    title_data = title_parser.match(foldername)

    try:
        # try and force an attribute error before it happens
        x = title_data.group("title")
        x = title_data.group("year")
    except AttributeError:
        return None

    return (
        title_data.group("title"),
        title_data.group("year")
        )


def in_use(test_file):

    # yes, possible race condition, but due to the system we're putting this
    # into race conditions will not be an issue.

    try:
        os.rename(test_file, test_file+"_")
        debug_message("Testing to see if {} is in use".format(test_file))
        os.rename(test_file+"_", test_file)
        debug_message("Not in use! Proceed!")
        return False
    except OSError:
        debug_message("File in use!")
        return True


def get_extension(filename):

    last_dot = filename.rfind('.')
    # if rfind fails, it returns -1
    if last_dot > 0:
        return filename[last_dot:]
    else:
        return None


def rename_duplicate(directory):

    os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
              settings.incoming_dir, ("[DUPLICATE] " + directory)))


def process_root_level_movie(movie):
    renamed_movie = "{} ({})".format(folder_translator(movie)[0], 
                                     folder_translator(movie)[1])

    debug_message("Moving root level file {} into new folder!".format(movie))
    if not os.path.isdir(os.path.join(settings.movie_dir, renamed_movie)):

        try:
            debug_message("Creating folder for root level file {}".format(movie))
            os.mkdir(os.path.join(settings.incoming_dir, renamed_movie))
            shutil.move(os.path.join(settings.incoming_dir, movie),
                        os.path.join(settings.incoming_dir, renamed_movie,
                                     movie))

            debug_message("Moving folder to movies folder!")
            shutil.move(os.path.join(settings.incoming_dir, renamed_movie),
                        os.path.join(settings.movie_dir, renamed_movie))
            debug_message("Move successful!")
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


def root_level_movie(files):

    debug_message("Found root level files: {}".format(files))
    if 'Thumbs.db' in files:
        # ignore the file; this does not delete it
        files.remove('Thumbs.db')
        debug_message("Ignoring Thumbs.db")

    for movie in files:
        if get_extension(movie) in settings.video_formats:
            if not in_use(os.path.join(settings.incoming_dir, movie)):
                process_root_level_movie(movie)


def is_video_folder(directory, dir_files):
    for directory_file in dir_files:
        debug_message("Testing file {} for video format!".format(directory_file))
        if get_extension(directory_file) in settings.video_formats:
            debug_message("Found video folder: {}".format(directory))
            return True

    debug_message("Folder does not contain first level video files. Skipping.")
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
        if get_extension(thing_to_delete) in settings.video_formats:
            if is_sample(directory, thing_to_delete):
                debug_message("Found sample movie {}! ENGAGE LASERS".format(
                              thing_to_delete))
                os.remove(os.path.join(settings.incoming_dir, directory,
                          thing_to_delete))
        if get_extension(thing_to_delete) in settings.exts_to_delete:
            debug_message("NUKING {}".format(thing_to_delete))
            os.remove(os.path.join(settings.incoming_dir, directory,
                      thing_to_delete))


def process_tv_show(directory):
    # for now, we're just renaming the folder so we can come back and get it
    # manually. TV shows are hard, so we'll take a look at that later.
    os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
              settings.incoming_dir, ("[TV] " + directory)))


def rename_movie_folder(directory):
    debug_message("Attempting rename of parent folder!")

    if folder_translator(directory) is None:
        print("{} has an issue I can't recover from. Skipping!")
        rename_skipped(directory)
    else:
        new_directory = "{} ({})".format(folder_translator(directory)[0],
                                         folder_translator(directory)[1])

        os.rename(os.path.join(settings.incoming_dir, directory), os.path.join(
                  settings.incoming_dir, new_directory))

        debug_message("Rename successful!")

        return new_directory


def move_movie_folder(new_directory):

    if not os.path.isdir(os.path.join(settings.movie_dir, new_directory)):

        try:
            shutil.move(os.path.join(settings.incoming_dir, new_directory),
                        os.path.join(settings.movie_dir, new_directory))
            debug_message("Move successful! Folder {} now located at {}".
                          format(new_directory, settings.movie_dir +
                                 new_directory))
        except (OSError, shutil.Error):
            print("{} is already in the destination directory! Renaming!".
                  format(new_directory))
            rename_duplicate(new_directory)
    else:
        print("{} is already in the destination directory! Renaming!".format(
              new_directory))
        rename_duplicate(new_directory)


def is_movie(directory_file):
    # return true if file is a file type we're looking for

    return (get_extension(directory_file) in settings.video_formats)


def process_movie(directory, dir_files):

    marked_tv_dir = False
    for directory_file in dir_files:
        if is_movie(directory_file):
            if is_tv_show(directory, directory_file):
                marked_tv_dir = True

    if marked_tv_dir:
        process_tv_show(directory)

    else:
        # we know we've got a movie, so it's time to rename and move the folder
        delete_samples(directory, dir_files)
        new_movie_folder = rename_movie_folder(directory)
        if type(new_movie_folder) is None:
            print("Encountered an issue with {}! Skipping!".format(directory))
        else:
            move_movie_folder(new_movie_folder)


def process_folders(dirs):
    for directory in dirs:
        debug_message("Switching to directory {}".format(directory))

        if "[TV]" in directory:
            debug_message("Found previously scanned TV folder. Skipping!")
        elif "[DUPLICATE]" in directory:
            debug_message("Found previously scanned duplicate directory. "
                          "Skipping!")
        elif "[SKIP]" in directory:
            debug_message("Found previously scanned skipped directory."
                          " Skipping again!")
        else:

            dir_files = [f for f in os.listdir(os.path.join(settings.
                         incoming_dir, directory)) if
                         os.path.isfile(os.path.join(settings.incoming_dir,
                                        directory, f))]
            if not in_use(os.path.join(settings.incoming_dir, directory,
                          dir_files[0])):
                debug_message("Folder is good to go - time to see if it's a "
                              "video folder!")

                if is_video_folder(directory, dir_files):
                    process_movie(directory, dir_files)
                else:
                    debug_message("Folder does not appear to be a movie. "
                                  "Skipping.")

            else:
                debug_message("Folder is in use! Moving to next folder.")


def main():

    # useless, but fun!
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
    global settings
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
    print("Running {}, version {}".format(settings.app_name, __version__))
    print("\nIncoming file directory: {}".format(settings.incoming_dir))
    print("Movie directory: {}".format(settings.movie_dir))
    print("\nFolders identified as containing movies (along with root level "
          "files)\nwill be moved to the movie directory. Folders identified "
          "as containing\nTV shows will have their parent folder renamed to "
          "have [TV] in front of\nit and otherwise left alone.\n")

    # Primary loop
    while True:

        # search directories and start figuring out what's what
        # returns first level folder names under dir
        dirs = [x for x in os.listdir(settings.incoming_dir) if os.path.isdir(
                os.path.join(settings.incoming_dir, x))]
        debug_message("Found directories: {}".format(dirs))

        process_folders(dirs)

        # check for files that aren't under their own folders for some
        # godforsaken reason
        files = [f for f in os.listdir(settings.incoming_dir) if os.path.
                 isfile(os.path.join(settings.incoming_dir, f))]

        if files is not []:
            root_level_movie(files)

        debug_message("Sleeping for {} seconds!".format(settings.delay_time))
        time.sleep(int(settings.delay_time))

if __name__ == "__main__":
    main()
