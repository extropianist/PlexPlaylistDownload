"""This script downloads a Plex Playlists into physical files in your filesystem.
import os
import argparse
import requests
import plexapi
import logging
import yaml
from plexapi.server import PlexServer
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

class DownloadOptions():
    def __init__(self, args, config=None):
        self.host = args.host or config.get('host')
        self.token = args.token or config.get('token')
        self.playlist = args.playlist or config.get('playlist')
        self.saveto = args.save_to or config.get('save_to')
        self.orderby = args.order_by
        self.keep_original_filename = args.original_filenames
        self.user = args.switch_user
        self.max_threads = args.max_threads or config.get('max_threads', 4)

def download_file(item, saveto, filename):
    try:
        files = item.download(saveto, keep_original_name=False)
        file = files[0]
        newfile = os.path.join(saveto, filename)
        os.rename(file, newfile)
        return True
    except Exception as e:
        logging.error(f"Failed to download {item.title}: {e}")
        return False

def download_playlist(options: DownloadOptions):
    """ Downloads a given playlist from the specified Plex server and stores the files locally. """

    # Setup logging
    logging.basicConfig(filename='plex_downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print('Connecting to plex...', end='')
    try:
        plex = PlexServer(options.host, options.token)
    except (plexapi.exceptions.Unauthorized, requests.exceptions.ConnectionError):
        print(' failed')
        logging.error('Failed to connect to Plex server')
        return
    print(' done')

    if options.user != None:
        print('Switching to managed account %s...' % options.user, end='')
        try:
            plex = plex.switchUser(options.user)
        except (plexapi.exceptions.Unauthorized, requests.exceptions.ConnectionError):
            print(' failed')
            logging.error(f'Failed to switch to managed account {options.user}')
            return
        print(' done')

    print('Getting playlist...', end='')
    try:
        playlist = plex.playlist(options.playlist)
    except (plexapi.exceptions.NotFound):
        print(' failed')
        logging.error(f'Playlist {options.playlist} not found')
        return
    print(' done')

    saveto = './%s/' % (playlist.title if options.saveto == None else options.saveto)
    if not os.path.exists(saveto):
        os.makedirs(saveto)

    print('Iterating playlist...', end='')
    items = playlist.items()
    print(' %s items found' % playlist.leafCount)

    if options.orderby != None:
        items.sort(key=lambda x: getattr(x, options.orderby))

    # Print file names and prompt user to continue
    print('\nFiles to be downloaded:')
    filenames = []
    for i, item in enumerate(items, start=1):
        filename = f"{item.title}.{item.media[0].container}"
        filenames.append(filename)
        print(f'{i}. {filename}')
    input('\nPress Enter to continue with downloading...')

    # Progress bar setup
    print('Downloading files...')
    with ThreadPoolExecutor(max_workers=options.max_threads) as executor:
        futures = []
        for i, item in enumerate(items, start=1):
            # Skip existing files if option is enabled
            filename = filenames[i - 1]
            filepath = os.path.join(saveto, filename)
            futures.append(executor.submit(download_file, item, saveto, filename))

        # Track progress
        for future in as_completed(futures):
            future.result()

    print(' done')

    # Ask the user if they want to review the log file
    review_log = input('Would you like to review the log file? (yes/no): ').strip().lower()
    if review_log in ['yes', 'y']:
        subprocess.run(['cat', 'plex_downloader.log'])

def main():
    # Load configuration from file
    config = {}
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file).get('plex', {})
    except FileNotFoundError:
        print("Config file not found, proceeding with command-line arguments only.")

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '-p', '--playlist',
        type=str,
        help="The name of the Playlist in Plex for which to create the M3U playlist"
    )
    mode.add_argument('-l', '--list',
                      action='store_true',
                      help="Use this option to get a list of all available playlists")
    parser.add_argument(
        '--host',
        type=str,
        help="The URL to the Plex Server, i.e.: http://192.168.0.100:32400"
    )
    parser.add_argument(
        '--token',
        type=str,
        help="The Token used to authenticate with the Plex Server"
    )
    parser.add_argument(
        '--order-by',
        type=str,
        help="Supply a property by which to sort the list. By default the list is exported in the same order as saved in Plex"
    )
    parser.add_argument(
        '--save-to',
        type=str,
        help="Supply a directory where to save the downloaded files to"
    )
    parser.add_argument(
        '--original-filenames',
        action='store_true',
        help="Use this option to download the files using their original filename"
    )
    parser.add_argument(
        '-u', '--switch-user',
        type=str,
        help="Optional: The Managed User Account you want to switch to upon connect."
    )
    parser.add_argument(
        '--max-threads',
        type=int,
        help="Maximum number of threads to use for downloading files"
    )

    args = parser.parse_args()
    options = DownloadOptions(args=args, config=config)

    if args.list:
        list_playlists(options)
    else:
        download_playlist(options)

if __name__ == "__main__":
    main()
