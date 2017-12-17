from bs4 import BeautifulSoup
from subprocess import call
import requests
import json
import telepot
import os
import sys
import schedule
import time
import logging
# import pdb

# Set up logging
def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('update-bot.log', mode='a')
    handler.setFormatter(formatter)
    #screen_handler = logging.StreamHandler(stream=sys.stdout)
    #screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    #logger.addHandler(screen_handler)
    return logger

logger = setup_custom_logger('update-bot')

gist_id = str(os.environ['VERSION_GIST'])
version_file = 'known_versions.json'

def get_version_file():
    with open(version_file,'w') as verfile:
        call(['gist', '-r', gist_id], stdout=verfile)

def get_known_versions():
    global known_versions
    with open(version_file,'r') as verfile:
        known_versions = json.load(verfile)
    return known_versions

def update_known_versions(package, version):
    with open(os.devnull, 'w') as FNULL:
        call(['gist', '-u', gist_id, version_file], stdout=FNULL)
    print('Updated gist file with version "' + version + '" for ' + package)

def do_update():
    get_version_file()
    # get_known_versions()

    updates = [
    # G870A(),
    qBittorrent(),
    libtorrent(),
    KeePassXC(),
    Atom(),
    AsciidoctorPDF(),
    AsciiBinder()
    ]

    for update in updates:
        # print(update.known_versions)
        # print(update.known)
        # print(update.version)
        # print(update.url)

        if update.version not in update.known_versions:
            notify(update.package,update.version,update.url,update.known)
            update.append_known(update.package,update.version)
        else:
            logger.info(update.package + ' version "' + update.version + '" is already known.')
            print(update.package + ' version "' + update.version + '" is already known.')

def liquidize(input):
    data = BeautifulSoup(input.text,'html.parser')
    return data

def prepare_msg(package, version, url):
    text = 'A new update for %s is released:\n%s\nDownload here: %s'

    message = text % (package, str(version), str(url))
    return message

def send_bot_msg(message):
    bot = telepot.Bot(os.environ['BOT_TOKEN'])
    user_id = os.environ['USER_ID']
    bot.sendMessage(user_id, message)

def notify(package, version, url, known):

    message = prepare_msg(package, version, url)
    send_bot_msg(message)
    # print(message)

class Update(object):

    def __init__(self):
        self.package = package
        self.version = version
        self.known_versions = get_known_versions()[package]
        self.known = self.get_current()

    def get_current(self, package):
        self.known = str(known_versions[package][-1])
        return self.known

    # def get_github_release(self, package, srcstring):

    def get_version(self):
        if self.package == 'qBittorrent':
            verstring = str(self.data[0]['name'])
            version = 'v' + self.strain_version(verstring, 'release-')
        elif self.package == 'libtorrent':
            verstring = str(self.data[0]['name'])
            version = 'v' + self.strain_version(verstring, 'libtorrent-')
        elif self.package == 'KeePassXC':
            version = str(self.data[0]['tag_name'])
        elif self.package == 'Atom':
            version = str(self.data['name'])
        elif self.package == 'Asciidoctor-PDF':
            version = str(self.data[0]['name'])
        elif self.package == 'AsciiBinder':
            version = str(self.data[0]['name'])
        return version

    def strain_version(self, verstring, verpos, endpos=''):
        start = verstring.find(verpos, 0)
        if endpos == '':
            end = len(verstring)
        else:
            end = verstring.find(endpos, 0)

        sievelen = len(verpos)
        self.version = str(verstring[start+sievelen:end])
        return self.version

    def append_known(self, package, version):
        self.known_versions.append(unicode(version))
        known_versions[package] = self.known_versions
        print ('Added ' + package + ' version ' + version + ' to list.')
        with open('known_versions.json','w') as verfile:
            verlist = json.dumps(known_versions, indent=4, sort_keys=True)
            verfile.write(verlist)
        update_known_versions(package, version)

    def get_data(self, srcstring, headers=''):
        data = requests.get(srcstring, headers)
        if data.status_code == 200:
            return data
        else:
            return None

    def print_version(self, version):
        print(self.version)

class G870A(Update):

    def __init__(self):
        self.package = 'G870A'
        self.srcstring = 'https://services.att.com/kmservices/v2/contents/KM1126238?app-id=esupport'
        self.xml = self.get_data(self.srcstring, {'Accept': 'application/json'}).json()['resultBody']['contentTypeProperties']['currentsoftdetails']
        self.version = self.get_version(self.data)
        self.previous_version = self.get_previous()
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
    #     pos = self.xml.find("Baseband version:",0)
    #     verpos = self.xml.find("G870A",pos+17,pos+57)
    #     version = self.xml[verpos:verpos+13]
    #     return version

    def get_previous(self):
        prev = self.xml.rfind("Previous versions required:",0)
        prev_ver = self.xml.find("G870A",prev+27)
        previous_version = self.xml[prev_ver:prev_ver+13]
        return previous_version

    def build_url(self):
        url = 'https://xdmd.sl.attcompute.com/agents/42998/1488/SS-' + self.get_previous() + '-to-' + self.get_version()[7:] + '-UP'
        return url

class qBittorrent(Update):

    def __init__(self):
        self.package = 'qBittorrent'
        self.srcstring = 'https://api.github.com/repos/qbittorrent/qBittorrent/tags'
        self.data = json.loads(self.get_data(self.srcstring).text)
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.version = self.get_version(data)
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
        # verstring = str(self.data[0]['name'])
        # version = 'v' + self.strain_version(verstring, 'release-')
        # return version

    def build_url(self):
        url = 'https://github.com/qbittorrent/qBittorrent/archive/release-' + self.get_version()[1:] + '.tar.gz'
        return url

class libtorrent(Update):

    def __init__(self):
        self.package = 'libtorrent'
        self.srcstring = 'https://api.github.com/repos/arvidn/libtorrent/releases'
        self.data = json.loads(self.get_data(self.srcstring).text)
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.version = self.get_version()
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
    #     verstring = str(self.data[0]['name'])
    #     version = 'v' + self.strain_version(verstring, 'libtorrent-')
    #     return version

    def build_url(self):
        url = 'https://github.com/arvidn/libtorrent/archive/libtorrent-' + self.get_version()[1:] + '.tar.gz'
        return url

class KeePassXC(Update):

    def __init__(self):
        self.package = 'KeePassXC'
        self.srcstring = 'https://api.github.com/repos/keepassxreboot/keepassxc/releases'
        self.data = json.loads(self.get_data(self.srcstring).text)
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.version = self.get_version()
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
    #     version = str(self.data[0]['tag_name'])
    #     return version

    def build_url(self):
        url = 'https://github.com/keepassxreboot/keepassxc/releases/tag/' + self.version
        return url

class Atom(Update):

    def __init__(self):
        self.package = 'Atom'
        self.srcstring = 'https://api.github.com/repos/atom/atom/releases/latest'
        self.data = json.loads(self.get_data(self.srcstring).text)
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.version = self.get_version()
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
    #     version = str(self.data['name'])
    #     return version

    def build_url(self):
        url = 'https://github.com/atom/atom/releases/tag/' + 'v' + self.get_version()
        return url

class AsciidoctorPDF(Update):

    def __init__(self):
        self.package = 'Asciidoctor-PDF'
        self.srcstring = 'https://api.github.com/repos/asciidoctor/asciidoctor-pdf/releases'
        self.data = json.loads(self.get_data(self.srcstring).text)
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.version = self.get_version()
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
    #     version = str(self.data[0]['name'])
    #     return version

    def build_url(self):
        url = str(self.data[0]['html_url'])
        return url

class AsciiBinder(Update):

    def __init__(self):
        self.package = 'AsciiBinder'
        self.srcstring = 'https://api.github.com/repos/redhataccess/ascii_binder/tags'
        self.data = json.loads(self.get_data(self.srcstring).text)
        self.known = self.get_current(self.package)
        self.known_versions = get_known_versions()[self.package]
        self.version = self.get_version()
        self.url = self.build_url()
        logger.debug('Performing update for ' + self.package)

    # def get_version(self):
    #     version = str(self.data[0]['name'])
    #     return version

    def build_url(self):
        url = str(self.data[0]['tarball_url'])
        return url


def main():

    do_update()

    schedule.every(2).hours.do(do_update)

    try:
        while True:
            schedule.run_pending()

            time.sleep(30)

    except requests.exceptions.ConnectionError:
        logger.error('ConnectionError occurred', exc_info=True)
        send_bot_msg('I could not retrieve something. Will try again later.')
        pass

    except KeyboardInterrupt:
        print "Terminated!"

    except:
        logger.error('Something has broken.', exc_info=True)
        send_bot_msg('Update bot has crashed!')

if __name__ == "__main__":
    main()
