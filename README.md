# PlexPlaylistDownload

----------------------------------------------------------------------------------------------------------------------------

Here is a summary of the changes made to the script from the original version to the current version:

Configuration File Support:

Added the ability to load settings from a configuration file (config.yaml).
Added configuration options for host, token, playlist, save_to, and max_threads.
Progress Bar and Logging:

Added tqdm for progress tracking during downloads, although this feature was later removed due to issues.
Introduced a logging mechanism using the logging module to log activities and errors into plex_downloader.log.
Multithreaded Downloads:

Integrated ThreadPoolExecutor to allow parallel downloading of playlist items using multiple threads, controlled by the --max-threads argument.
Enhanced User Prompts:

Added a feature that lists the files to be downloaded and prompts the user to confirm before proceeding with the downloads.
After the download, the script now asks the user if they want to review the log file. If the user agrees, it opens the log file using cat.
Removed skip-existing Feature:

Initially, a --skip-existing feature was added, allowing users to skip files that already exist in the target directory. This was later removed upon user request.
Code Improvements:

Fixed various indentation issues and syntax errors to ensure smooth operation.
Improved error handling when connecting to the Plex server, switching user accounts, and downloading files.
The final script provides better flexibility for users through configuration files, multithreaded downloads, enhanced logging, and improved user interactions while ensuring a smooth and error-free experience.

----------------------------------------------------------------------------------------------------------------------------

A small python script to download playlists created on a [Plex](https://www.plex.tv/) media server to physical files
on your filesystem.

If this means nothing to you, you can probably stop reading right now.
Otherwise, go ahead, you might have a similar use-case as me.

## Prerequisites

### High-Level

- [Plex Media Server](https://www.plex.tv/):
  Plex is my go-to media frontend I use on Smart TVs, Phones, Tablets, PCs, Laptops, you name it. Well
  everything except for my car. All my media, movies, TV shows, music and photos are stored on my own private
  media server with ability to stream anytime, anywhere in the world.

### Low-Level

1. Python 3
2. The plexapi library (use `pip install plexapi` to install)

## My workflow

If you like to know a bit more about my use-case, read on, otherwise you can skip this section.

> Since years I have been an avid user of Plex. I love having all my media in one place available on many different devices.
> I've also recently started using Plex for organizing, categorizing, tagging all the photos I've made over the years and
> recently, with the birth of my daughter, this feature has become more and more important. Now, everytime I want to develop
> a physical photo album I usually start by creating a playlist in Plex. Once that is done, I download all photos to my PC
> transfer the photos to a thumbdrive so I can get them developed/printed.
> This script is helps me with this process.

## How does it work?

So we have established you need a Plex library with local media assets from which you create playlists in Plex.

If this holds true for you then you might be able to use this script with your Plex server.
So what else do you need to get started:

1. Your Plex server base URL (in your local network, i.e., `http://192.168.0.10:32400`), which you provide to script
   via the `--host <url>` argument
2. A token to access your Plex server with, which you provide using `--token <thetoken>` argument.
   You can find out how to get such a token [here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

### Querying the available playlists

Using the above mentioned arguments `--host` and `--token` we are now ready to start communicating with the Plex server.
You may want to start by querying all available playlists that can be used for download. We're limiting everything to `music`
playlists.

To query your playlists run the script with:

```bash
python3 PlexPlaylistDownload.py --host <baseurl> --token <yourtoken> --list
```

This will output all available playlists for download.

### Downloading your files

To download a specific playlist you need to supply it's name to the script.

```bash
python3 PlexPlaylistDownload.py --host <baseurl> --token <yourtoken> --playlist <yourplaylist>
```

Executing this command will create a folder named `./<yourplaylist>` in the working directory where you executed the command.
Inside this folder all the downloaded files will be placed, where the filenames have been renamed with numbers that represent
the order you have defined, which is either the order as defined in the playlist, or an artificial order which you can specify
with `--order-by <field>` (see below for more details).

### Optional arguments

The following optional arguments can be supplied when combined with the `--playlist` argument:

- `--original-filenames`: Use this switch to download the files using their original filenames. This will omit renaming the files.
  Also note that it does not make sense to combine this argument with `--order-by <field>`.
- `--save-to <path>`: Specify a path where you want your files to be saved. If the path does not exist it will be created.
- `--order-by <field>`: Reorders your files from the playlist in the order given by the supplied field. A valid value
  would be for instance `originallyAvailableAt` which outputs photos in the order of the date they were taken. If you're
  interested in different fields you will have to play around with the [python plexapi](https://python-plexapi.readthedocs.io/en/master/index.html)
  and find the fields yourself.
