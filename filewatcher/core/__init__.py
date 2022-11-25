import os
from typing import Optional

from filewatcher.core.console import console

#  useless, but fun!
init_phrases = (
    "Reticulating splines",
    "Murdering zombies",
    "Initializing",
    "Bringing MAXIS back",
    "Engaging warp drive",
    "Telling future",
    "Preparing fart",
    "Building pyramids",
    "Making 'fetch' happen",
)

init_endings = (
    "Splines reticulated!",
    "Zombies murdered!",
    "Initialized!",
    "I tried :'(",
    "Warp drive engaged!",
    "Future told! ...I think.",
    "...Heh.",
    "Pyramids built!",
    "That is /so/ fetch.",
)


class StatusTag:
    TV: str = "[TV]"
    DUPLICATE: str = "[DUPLICATE]"
    SKIP: str = "[SKIP]"


def get_root_directories() -> list[Optional[str]]:
    return [
        x
        for x in os.listdir(settings.incoming_dir)
        if os.path.isdir(os.path.join(settings.incoming_dir, x))
    ]


def get_root_files() -> list[Optional[str]]:
    return [
        f
        for f in os.listdir(settings.incoming_dir)
        if os.path.isfile(os.path.join(settings.incoming_dir, f))
    ]


def get_files(directory: str) -> list[Optional[str]]:
    return [
        f
        for f in os.listdir(os.path.join(settings.incoming_dir, directory))
        if os.path.isfile(os.path.join(settings.incoming_dir, directory, f))
    ]


def get_folders(directory: str) -> list[Optional[str]]:
    return [
        f
        for f in os.listdir(os.path.join(settings.incoming_dir, directory))
        if os.path.isdir(os.path.join(settings.incoming_dir, directory, f))
    ]


class base_settings:
    def __init__(self):
        self._app_name = "FileWatcher"
        self._version = 3.1
        self._delay_time = "180"
        self._debug = False

        self._incoming_dir = "C:\--INCOMING--"
        self._movie_dir = "C:\Movies"
        self._audio_dir = "C:\Audio"

        self._min_movie_size = "650"
        self._min_episode_size = "25"
        self._exts_to_delete = ".nfo, .txt, .jpg"
        self._video_formats = ".avi, .mkv, .mp4"
        self._audio_formats = ".mp3, .ogg, .flac, .aac, .wav, .m4a, .alac, .aiff"

    @property
    def app_name(self):
        return self._app_name

    @app_name.setter
    def app_name(self, new_name):
        self._app_name = new_name

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, number):
        self._version = number

    @property
    def delay_time(self):
        return self._delay_time

    @delay_time.setter
    def delay_time(self, number):
        if number > 0:
            self._delay_time = number
        else:
            console.print("Warning! You can't set the delay time to less than 0!")

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, new_value):
        self._debug = bool(new_value)

    @property
    def incoming_dir(self):
        return self._incoming_dir

    @incoming_dir.setter
    def incoming_dir(self, new_value):
        self._incoming_dir = new_value

    @property
    def movie_dir(self):
        return self._movie_dir

    @movie_dir.setter
    def movie_dir(self, new_value):
        self._movie_dir = new_value

    @property
    def audio_dir(self):
        return self._audio_dir

    @audio_dir.setter
    def audio_dir(self, new_value):
        self._audio_dir = new_value

    @property
    def min_movie_size(self):
        return self._min_movie_size

    @min_movie_size.setter
    def min_movie_size(self, value):
        if int(value) < 0:
            raise ValueError("min_movie_size: Cannot be less than 0!")
        self._min_movie_size = value

    @property
    def min_episode_size(self):
        return self._min_episode_size

    @min_episode_size.setter
    def min_episode_size(self, value):
        if int(value) < 0:
            raise ValueError("min_episode_size: Cannot be less than 0!")
        self._min_episode_size = value

    @property
    def exts_to_delete(self):
        return self._exts_to_delete

    @exts_to_delete.setter
    def exts_to_delete(self, value):
        self._exts_to_delete = value

    @property
    def video_formats(self):
        return self._video_formats

    @video_formats.setter
    def video_formats(self, value):
        self._video_formats = value

    @property
    def audio_formats(self):
        return self._audio_formats

    @audio_formats.setter
    def audio_formats(self, value):
        self._audio_formats = value

    @property
    def banned_characters(self):
        return ("/", "\\", ":", "*", "?", '"', "<", ">")

    @property
    def filenames_to_ignore(self):
        return ("Thumbs.db", ".DS_Store")


settings = base_settings()
