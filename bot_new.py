# Define imports and global stuff

from bs4 import BeautifulSoup
import subprocess
from argparse import ArgumentParser
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
parser.add_argument("-l", "--list", help="Print the list of packages to check", action="store_true", )
parser.add_argument("-a", "--all", help="Print raw packages output", action="store_true")
parser.add_argument("-f", "--full", help="Get the full output for a certain package.", action="store_true")

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

def read_local_package_list():
    """
    Reads the package list file in the directory
    """
    global package_list
    if os.path.exists(pkglistpath):
        with open(pkglistpath, 'r+') as pkgfile:
            package_list = pkgfile.read()
            #print(package_list)
    else:
        logger.critical("Package list file does not exist.")
        print('File not found.')
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), pkglistpath)

def get_package_list():
    """
    Reads the packages list and fills the array of packages to check
    """
    global package_list
    with open(pkglistpath) as pkglist:
        package_list = json.loads(pkglist.read())
        #print(package_list)
        #print(package_list[0]['qbittorrent']['versions'])


def read_package_info(count):
    """
    Read the information for a specified package
    """
    count = 0
    while count < len(package_list):
        packages = json.dumps(package_list['packages'])
        print(packages[count])
        #print(json.dumps(package_list['packages'][count], indent=2, sort_keys=True))
        #print(json.dumps(package_list['packages'][count]['name'], indent=2, sort_keys=True))


def update_local_info(package_list):
    """
    Write the known versions information to the data file
    """
    if os.path.exists(pkglistpath):
        with open(pkglistpath, 'r+') as verfile:
            #print(package_list)
            verfile.write(package_list)
    else:
        with open(pkglistpath, 'w+') as verfile:
            logging.warning('Known versions file does not exist. Creating a new one.')
            verfile.write(package_list)

# For debugging

def print_packages():
    """
    Prints the configured packages and their known version numbers
    """
    count = 0
    number = len(json.loads(package_list)['packages'])
    logger.info("There are [" + str(number) + "] packages to be checked.")
    pkgs = json.loads(package_list)
    print("There are [" + str(number) + "] packages to be checked.")
    while count < number:
        print(str((count+1)) + ":" + pkgs['packages'][count]['name'])
        #print(pkgs['packages'][count]['versions'])
        count += 1

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


    def get_package_versions():
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
    get_package_gist()

    update_local_info(package_list)

    #test_get_gh_release()

    #get_package_list()

    #read_local_package_list()

    #read_package_info(2)

    # print(len(package_list))
    # count = 0
    # while count < len(package_list):
    #     read_package_info(count)
    #     count += 1

    args = parser.parse_args()
    #print(args)

    if args.list == True:
        print_packages()

    if args.all == True:
        print(package_list)

# #Figure out how to take "package" input and use that as secondary parameter
#     if args.full == True:
#         print(package_list)

if __name__ == "__main__":
    main()
