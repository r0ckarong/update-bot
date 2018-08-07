# Define imports and global stuff

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from github import Github
from pprint import pprint
import configparser
import subprocess
import logging
import time
import errno
import os
import requests
import json
import telepot
import schedule
import gist

# import pdb

# Set up logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='updater.log',
                    filemode='a',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up configuration parsing
config = configparser.ConfigParser()

# Set up argument parsing
parser = ArgumentParser()
parser.add_argument("--latest", type=int, help="Display the latest release info from GitHub for the selected package")
parser.add_argument("-l", "--list", action="store_true", help="Print the list of packages to check")
parser.add_argument("-ll", "--long", action="store_true", help="Print the list of packages and their known versions")
parser.add_argument("-r", "--raw", action="store_true", help="Print raw output of packages Gist")
parser.add_argument("-i", "--pkginfo", type=int, help="Get the full output for a certain package")
parser.add_argument("-t", "--token", type=str, help="GitHub access token")
# Not implemented yet
parser.add_argument("-u", "--user", type=str, help="Telegram User ID of who should receive messages")
parser.add_argument("-b", "--bot", type=str, help="Telegram Bot Token")
parser.add_argument("--store", action='store_true', help="Store login credentials/tokens in config file")
parser.add_argument("-d", "--daemon", action='store_true', help="Tells the program to keep checking repeatedly in the background")

# Set up global information

# Set up environment
path = os.getcwd()

known_versions = ""
package_list = ""
packages = []

# Define package list configuration
package_listfile = "packages.json"
pkglistpath = path+"/"+package_listfile

# Make this configurable
gist_id = "dac9c4de15c7b061e7851fe1105a16d3"

def get_package_gist():
    """
    Retrieves the current package information gist from GitHub
    """

    try:
        global package_list
        logger.info("Retrieving version info from Gist")
        # This is the JSON input from the package file stored on GitHub, need to rebuild to use local fallback
        package_list = subprocess.check_output(['gist', 'content', gist_id, 'packages.json'], universal_newlines=True)
        #print(package_list)
    except CalledProcessError as error:
        logger.exception("Retrieving version info failed. Connection problem?")

def parse_package_list():
    """
    Reads the packages list and fills the array of packages to check
    """

    global pkgs
    pkgs = json.loads(package_list)['packages']

def read_local_list():
    """
    Reads the package list file in the directory
    """

    global package_list
    if os.path.exists(pkglistpath):
        with open(pkglistpath, 'r+') as pkgfile:
            package_list = pkgfile.read()
            #print(package_list)
    else:
        print("Package list file does not exist.")
        logger.critical("Package list file does not exist.")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), pkglistpath)

def update_local_list(package_list):
    """
    Write the known versions information to the data file
    """

    if os.path.exists(pkglistpath):
        with open(pkglistpath, 'r+') as verfile:
            #print(package_list)
            verfile.write(package_list)
    else:
        with open(pkglistpath, 'w+') as verfile:
            print('Known versions file does not exist. Creating a new one.')
            logging.warning('Known versions file does not exist. Creating a new one.')
            verfile.write(package_list)

def update_version_gist(package_list):
    """
    Update the version info gist on GitHub
    """

    logger.info("Updated Version info Gist." + str(gist_id))
    print("Updating Version info Gist.")

def print_packages():
    """
    Prints the configured packages and their known version numbers
    """

    count = 0
    number = len(pkgs)
    logger.info("There are [" + str(number) + "] packages to be checked.")
    print("There are [" + str(number) + "] packages to be checked.")
    while count < number:
        print(str((count+1)) + ":" + pkgs[count]['name'])
        if args.long:
            print(pkgs[count]['known_versions'])
        count += 1

def package_info(entry):
    """
    Prints information for a single entry
    """

    #print(pkgs['packages'][entry])
    print(json.dumps(pkgs[entry], indent=2, sort_keys=False))

def latest_release_info(entry):
    """
    Prints the latest release info for a given package
    """

    type = pkgs[entry]['type']
    package = pkgs[entry]['package']

    if type == "binary":
        print("This type is currently not supported.")
    else:
        user = pkgs[entry]['github'][0]['user']
        repo = pkgs[entry]['github'][1]['repo']
        github_get_release_info(package, user, repo, type)

def github_get_release_info(package, user, repo, type):
    """
    Retrieve release information from GitHub repository
    """

    gh_user = gh.get_user(user)
    gh_repo = gh_user.get_repo(repo)

    header = "Latest " + str.upper(type) + " for " + package + ":"
    print(header)
    print("=" * len(header))

    if type == "release":
        latest = []
        releases = gh_repo.get_releases()[:5]

        for release in releases:
            if release.prerelease + release.draft == 0:
                latest.append(release)

        print(latest[0].tag_name)
        print(latest[0].html_url)
        print(latest[0].body)

    elif type == "prerelease":
        releases = gh_repo.get_releases()[:1]

        for release in releases:
            print(release.tag_name)
            print(release.html_url)
            print(release.body)

    elif type == "tag":
        releases = gh_repo.get_tags()[:1]

        for release in releases:
            print(release.name)
            print("https://github.com/" + user + "/" + repo + "/releases/tag/" + release.name)

    elif type == "binary":
        print("Type is BINARY/OTHER")

    print("")

def build_package_array():
    """
    Builds the array of packages needed for operation.
    """

    arr = []
    pack = 0
    while pack < len(pkgs):
        obj = Package()
        arr.append(obj)
        arr[pack].package = pkgs[pack]['package']
        # print(pkgs[pack]['package'])
        # print(arr[pack].package)
        pack += 1

    # pprint(arr)
    # print(arr[0].name)

def send_message(package, release, url, changes):
    user_id = os.environ['USER_ID']
    bot = telepot.Bot(os.environ['BOT_TOKEN'])
    logger.info("Sending a message to " + user_id)
    message = "📣 New release for " + package + "\n* Version: " + release + "\n* D/L: " + url + "\n* Changelog: " + changes
    bot.sendMessage(user_id, message)

class Package(object):

    def __init__(self):
        """
        Basic definition of a package

        :package: The name used througout the program
        :name: The "pretty" name of the package
        :source: Source URL where the new package release is published
        :download: Calculated or hardcoded URL where the binary download file is located
        :more: Additional attributes for the package from packages.json
        :versions: List of versions for the package
        :type: Type of package release
            GitHub named release = release
            GitHub tagged release (or beta) = tag
            Non-GitHub release or other website resource = binary
        """

        self.package = ''
        self.name = ''
        self.source = ''
        self.download = ''
        self.more = []
        self.versions = []
        self.type = ''

# The [X] can't work, figure out how to iterate packages without writing a specific class for each one
    def set_source():
        self.source = package_list['packages'][X]['source']

    def set_type():
        """
        Reads the type of package release to be used in discovery and URL processing
        """

        self.type = package_list['packages'][X]['type']


    def get_package_versions(pkg_int):
        """
        Reads the known versions for a package from the package list
        """

        self.versions = package_list['packages'][X]['versions']

def main():
    #parse_options()

    global args
    global gh

    args = parser.parse_args()
    gh = Github(args.token)

    get_package_gist()

    parse_package_list()

    entries = len(json.loads(package_list)['packages'])
    if args.list or args.long:
        print_packages()

    if args.latest == None:
        pass
    elif args.latest > 0:
        if args.latest > entries:
            print("Value too high.\nChoose a value between 1-" + str(entries) + "\n")
            print_packages()
            pass
        elif args.latest <= entries:
            latest_release_info(args.latest-1)

    if args.raw:
        print(package_list)

    if args.pkginfo == None:
        pass
    elif args.pkginfo == 0:
        print_packages()
    elif args.pkginfo >= 1:
        if args.pkginfo > entries:
            print("Value too high.\nChoose a value between 1-" + str(entries) + "\n")

            print_packages()
            pass
        elif args.pkginfo <= entries:
            package_info(args.pkginfo-1)


    build_package_array()

    #github_get_release_info()

    #github_get_release_info('atom', 'atom', 'atom', 'release')
    #github_get_release_info('KeePassxc', 'keepassxreboot', 'keepassxc', 'release')
    #github_get_release_info('qBittorrent', 'qbittorrent', 'qBittorrent', 'tag')
    #github_get_release_info('AsciiDoctor-PDF', 'asciidoctor', 'asciidoctor-pdf', 'prerelease')
    #github_get_release_info('AsciiBinder', 'redhataccess', 'ascii_binder', 'tag')

    #update_local_list(package_list)
    #update_version_gist(package_list)

    #send_message("TESTPACKAGE", "1.2.3", "https://markus-napp.de/bla", "Nothing changed.")

    # Need to handle errors:
    # ConnectionResetError
    # JSONDecodeError
    # ProtocolError

    print(args)

if __name__ == "__main__":
    main()
