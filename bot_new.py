from bs4 import BeautifulSoup
import subprocess
import requests
import json
import telepot
import os
import schedule
import time
import logging
import gist
import pprint
# import pdb

pp = pprint.PrettyPrinter(indent=4)

# Set up logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='updater.log', filemode='a', level=logging.INFO)
logger = logging.getLogger(__name__)

### Make this configurable
gist_id = "dac9c4de15c7b061e7851fe1105a16d3"

### Set up global information

# Set up environment
path = os.getcwd()

known_versions = ""
package_list = ""
packages = []

# Define version file
version_file = 'known_versions.json'
verfilepath = path+"/"+version_file

# Define package list configuration
package_listfile = "packages.json"
pkglistpath = path+"/"+package_listfile

"""
Retrieves the current version gist
"""
def get_version_gist():
    try:
        global known_versions
        logger.info("Retrieving version info from Gist")
        known_versions = subprocess.check_output(['gist', 'content', gist_id, 'known_versions.json'], universal_newlines=True)
        #print(known_versions)
    except CalledProcessError as error:
        logger.exception("Retrieving version info failed. Connection problem?")

"""
Reads the package list in the directory
"""
def get_package_list():
    global package_list
    if os.path.exists(pkglistpath):
        with open(pkglistpath, 'r+') as pkgfile:
            package_list = pkgfile.read()
            #print(package_list)
    else:
        logger.critical("Package list file does not exist.")
        print('File not found.')

"""
Reads the packages list and fills the array of packages to check
"""
def read_package_list():
    global package_list
    with open(pkglistpath) as pkglist:
        package_list = json.loads(pkglist.read())
        #print(package_list)
        #print(package_list[0]['qbittorrent']['versions'])

"""
Read the information for a specified package
"""
def read_package_info(count):
    print(json.dumps(package_list['packages'][count], indent=2, sort_keys=True))
    print(json.dumps(package_list['packages'][count]['name'], indent=2, sort_keys=True))

"""
Write the known versions information to the data file
"""
def update_version_file(known_versions):
    if os.path.exists(verfilepath):
        with open(verfilepath, 'r+') as verfile:
            #print(known_versions)
            verfile.write(known_versions)
    else:
        with open(verfilepath, 'w+') as verfile:
            logging.warning('Known versions file does not exist. Creating a new one.')
            verfile.write(known_versions)

### For debugging
"""
Prints the configured packages and their known version numbers
"""
def print_packages():
    count = 0
    numba = len(package_list['packages'])
    print(numba)
    while count < numba:
        print(package_list['packages'][count]['name'])
        print(package_list['packages'][count]['versions'])
        count += 1

class Update(object):
    """
    Reads the known versions for a package from the package list
    """
    def get_package_versions():
        print("Nope")




def main():
    get_version_gist()

    #update_version_file(known_versions)

    get_package_list()

    read_package_list()

    read_package_info(2)

    print_packages()

    # print(len(package_list))
    # count = 0
    # while count < len(package_list):
    #     read_package_info(count)
    #     count += 1

if __name__ == "__main__":
    main()
