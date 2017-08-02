from bs4 import BeautifulSoup
import requests
import schedule
import telepot
import time
import os
import pdb
import json

known = ''
known_versions = {}
message = ''
version = ''
data = ''

class Update(object):

    def __init__(self, package, version, known, known_versions, data, message):
        self.package = package
        self.version = version
        self.known = known
        self.known_versions = known_versions
        self.data = data
        self.message = message

    def get_current(self, package):
        with open('known_versions.json','r') as verfile:
            known_versions = json.load(verfile)
            known = str(known_versions[package][-1])
        return known
        return known_versions

    def strain_version(self, verstring, verpos, endpos):
        start = verstring.find(verpos, 0)
        end = verstring.find(endpos, 0)
        sievelen = len(verpos)
        version = str(verstring[start+sievelen:end])
        return version

    def append_known(self, package, version, known_versions):
        if version not in known_versions[package]:
            known_versions[package].append(unicode(version))
            with open('known_versions.json','w') as verfile:
                verlist = json.dumps(known_versions, indent=4, sort_keys=True)
                verfile.write(verlist)
        else:
            print(package + 'version ' + version + ' already known.')

class G870A(Update):
    package = 'G870A'

    data = requests.get('https://services.att.com/kmservices/v2/contents/KM1126238?app-id=esupport', headers={'Accept': 'application/json'}).json()

    url =  'https://xdmd.sl.attcompute.com/agents/42998/1488/SS-' + previous_version + '-to-' + version[7:] + '-UP'

class qBittorrent(Update):
    package = 'qBittorrent'
    url = 'https://sourceforge.net/projects/qbittorrent/files/qbittorrent/qbittorrent-' + version[0:] + '/qbittorrent-' + version[0:] + '.tar.gz/download'

class KeePassXC(Update):
    package = 'KeePassXC'
    url = str(data.item.guid.string)

def get_current(package):
    global known_versions
    global known
    with open('known_versions.json','r') as verfile:
        known_versions = json.load(verfile)
        known = str(known_versions[package][-1])
    return known

def strain_version(verstring, verpos, endpos):
    global version
    start = verstring.find(verpos, 0)
    end = verstring.find(endpos, 0)
    sievelen = len(verpos)
    version = str(verstring[start+sievelen:end])
    return version

def append_known(package, version):
    global known_versions

    if version not in known_versions[package]:
        known_versions[package].append(unicode(version))
        with open('known_versions.json','w') as verfile:
            verlist = json.dumps(known_versions, indent=4, sort_keys=True)
            verfile.write(verlist)
    else:
        print(package + 'version ' + version + ' already known.')

def liquidize(html):
    global data
    data = BeautifulSoup(html.text,'html.parser')
    return data

def prepare_msg(package, version, url):
    global message

    text = 'A new update for %s is released:\n%s\nDownload here: %s'

    message = text % (package, str(version), str(url))
    return message

def send_bot_msg(message):
    user_id = os.environ['USER_ID']
    bot = telepot.Bot(os.environ['BOT_TOKEN'])
    bot.sendMessage(user_id, message)

def notify(package, version, url):
    if version != known:
        prepare_msg(package, version, url)
        send_bot_msg(message)
        print(url)
        append_known(package, version)
    else:
        print('No new version for ' + package)

def find_g870a_update():
    package = 'G870A'
    get_current(package)

    data = requests.get('https://services.att.com/kmservices/v2/contents/KM1126238?app-id=esupport', headers={'Accept': 'application/json'}).json()

    xml = data['resultBody']['contentTypeProperties']['currentsoftdetails']
    # xml2 = data['resultBody']['contentTypeProperties']['currentsoftupd']

    # data = BeautifulSoup(xml,'html.parser')

    # Current version
    pos = xml.find("Baseband version:",0)
    verpos = xml.find("G870A",pos+17,pos+57)
    version = xml[verpos:verpos+13]

    # Previous version
    prev = xml.rfind("Previous versions required:",0)
    prev_ver = xml.find("G870A",prev+27)
    previous_version = xml[prev_ver:prev_ver+13]

    url =  'https://xdmd.sl.attcompute.com/agents/42998/1488/SS-' + previous_version + '-to-' + version[7:] + '-UP'

    notify(package, version, url)

def find_qbt_update():
    package = 'qBittorrent'
    get_current(package)

    html = requests.get('https://www.qbittorrent.org/news.php')
    liquidize(html)
    verstring = str(data.p.string)

    strain_version(verstring, 'qBittorrent ', ' was')

    url = 'https://sourceforge.net/projects/qbittorrent/files/qbittorrent/qbittorrent-' + version[0:] + '/qbittorrent-' + version[0:] + '.tar.gz/download'

    notify(package, version, url)

def find_kpxc_update():
    package = 'KeePassXC'
    get_current(package)

    html = requests.get('https://keepassxc.org/blog/feed.xml')
    liquidize(html)
    verstring = str(data.item.title)

    strain_version(verstring, 'KeePassXC ', ' released')

    url = str(data.item.guid.string)

    notify(package, version, url)

def do_updates():
    find_g870a_update()
    find_qbt_update()
    find_kpxc_update()

schedule.every().day.at("00:00").do(do_updates)
schedule.every().day.at("12:00").do(do_updates)

do_updates()

try:
    while True:
        schedule.run_pending()

        time.sleep(30)

except KeyboardInterrupt:
    print "Terminated!"
