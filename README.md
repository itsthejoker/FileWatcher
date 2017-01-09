# FileWatcher
When downloading movies, the organization is often what gets you. Thankfully, now you have a little helper!

With FileWatcher, simply use the config file to point it at a downloads directory. In this case, we'll say C:\\--INCOMING-- or /home/itsthejoker/Downloads/ (FileWatcher is OS agnostic!). FileWatcher keeps an eye on all the folders and files in the downloads folder on a settable schedule, once every `x` seconds. If it identifies a folder containing a movie, it will attempt to see if it's in use, then try and rename the parent folder according to the schema of "Movie! (Year)" and move the folder to a settable movies directory. It can also be set to automatically delete any kind of file type found in a movie directory. FileWatcher 2.0 is built for Python 3.5, but any version of Python 3 should work.

The newly finished version 2.0.0 is incompatible with previous versions. If you're using a previous version of FileWatcher, you'll need to back up your config and make a new one -- FileWatcher tries to make this as painless as possible, but it's not automatic (yet)!

## Usage
* Save the program anywhere you like, then run it once. It will generate the config file that you'll have to edit.
* Change the downloads directory and the movie directory to wherever they are on your HDD. Copying across HDDs is supported.
* By default, the program refreshes your downloads directory every 180 seconds, or three minutes. This is changeable in the config file.
* Sit back and download away!

If a folder contains video files, it will tag the directory if it cannot process it correctly. Possible tags:
* [TV] - If a folder contains video files that are between the minimum episode size and the minimum movie size, FileWatcher will mark the directory as containing TV episodes. Eventually I would like to have FileWatcher be able to handle these, but because they're so varied and much more complex, this is far from realization.
* [DUPLICATE] - If you already have the movie in your movies folder, the program will mark the one in the downloads folder as a duplicate and leave it alone. What you choose to do with it is up to you.
* [SKIP] - This is saved for strange cases where it has detected a movie folder but cannot finish the processing for some reason or another. Once marked, it will ignore this directory until you either manually remove the tag or fix whatever it has complained about.

### IMDbPy!
~~Starting a few versions ago, FileWatcher now has support for IMDbPy! If a) IMDbPy is installed and b) the following criteria are met:

* root level movie
* filename contains title, but no year (example: aladdin.mp4)

...then FileWatcher will attempt to query IMDb and try to pull the year for you. If the query succeeds and FileWatcher is confident enough that it's the right file, it will rename the file (Aladdin (1992).mp4), create a folder for it, place the newly-renamed file into the folder, and treat it like a normal movie object for sorting. It's very cool.~~

IMDbPy does not work in Python3! I'll try to recreate the behavior that we need inside the actual application, but that's not done yet. For now, this functionality is deprecated.

### A Note About Renaming
When the program renames a folder, it will parse the title of the folder and attempt to extract the title and year from it. Examples:
* Season 10 --> [TV] Season 10
* Transporter 2 (2005) [1080p] --> Transporter 2 (2005)
* Daddy.Long.Legs.1955.720p.BluRay.x264 --> Daddy Long Legs (1955)
* Sweeney Todd in Concert 2001.mp4 --> Sweeney Todd in Concert (2001)\Sweeney Todd in Concert 2001.mp4

The program will barf if it cannot find a title or a year, but that's why the [SKIP] tag exists.

### A Note About Deleting
You can set the program to automatically delete certain types of files from identified movie directories. When you generate the config, it will already have three file types filled in: .txt, .nfo, and .jpg. This is to get rid of a lot of the fluff that commonly finds its way into the media. It will also delete all video files smaller than the minimum episode size that is set, assuming that anything smaller than a TV episode is going to be some kind of "sample.avi" file. We don't need those either, so it's gone. If you want to disable the sample file deletion, just set the minimum episode size to 0.

## Music
FileWatcher also now does very basic music handling - it looks for audio files in a folder and then moves them to another folder of your choosing. At this point, it does not do any renaming or attempt to sort; it will only move to another directory, where you can presumably run through another program to sort. (I'm using MusicBrainz Picard, and it's working pretty well!)
