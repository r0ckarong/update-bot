# Define imports and global stuff

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from github import Github
from pprint import pprint
import subprocess
import requests
import json
import telepot
import os
import schedule
import time
import logging
import errno
import gist

# import pdb

# Set up logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='updater.log', filemode='a', level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up argument parsing
parser = ArgumentParser()
parser.add_argument("-l", "--list", help="Print the list of packages to check", action="store_true")
parser.add_argument("-ll", "--long", help="Print the list of packages and their known versions", action="store_true")
parser.add_argument("-r", "--raw", help="Print raw output of packages Gist", action="store_true")
parser.add_argument("-i", "--pkginfo", type=int, help="Get the full output for a certain package")

### Not implemented yet
#parser.add_argument("-d", "--daemon", action='store_true', help="Tells the program to keep checking repeatedly in the background.")
#parser.add_argument("-t", "--token", type=str, help="GitHub access token")

# Set up global information

# Set up environment
path = os.getcwd()
gh = Github()

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

def parse_options():
    """
    Process user input of arguments
    """
    global args

    args = parser.parse_args()

    if args.list or args.long:
        print_packages()
    elif args.raw:
        print(package_list)
    elif args.pkginfo == 0:
        print_packages()
    elif args.pkginfo == None:
        args.pkginfo = 0
    elif args.pkginfo > 0:
        entries = len(json.loads(package_list)['packages'])

        if args.pkginfo > entries:
            print_packages()
            print("Choose a value between 1-" + str(entries))
        else:
            package_info(args.pkginfo-1)

    #print(args)

def GH_get_release_info():
    """
    Retrieve release information from GitHub repository
    """
    # Test with atom project for now
    user = gh.get_user('atom')
    repo = gh.get_repo('atom')
    releases = repo.get_releases()[5]
    for release in releases:
        draft = release.draft
        prerelease = release.prerelease
        title = release.title
        id = release.id
        changes = release.body
        url = release.html_url
        print(r.title, r.id, r.tarball_url, r.tag_name, r.prerelease)

def build_package_array():
    arr = []
    pack = 0
    while pack < len(pkgs):
        obj = Package()
        arr.append(obj)
        arr[pack].package = pkgs[pack]['package']
        print(pkgs[pack]['package'])
        print(arr[pack].package)
        pack += 1

    pprint(arr)
    print(arr[0].name)

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


#def test_get_gh_release():
    #print(package_list)


# class GHRelase(Package):
#
# class GHTag(Package):
#
# class Binary(Package):


def main():
    parse_options()

    get_package_gist()

    parse_package_list()

    build_package_array()

    #update_local_list(package_list)

if __name__ == "__main__":
    main()
