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

def do_updates():
    find_g870a_update()
    find_qbt_update()
    find_kpxc_update()

def get_current(tp):
    global known_versions
    global known
    with open('known_versions.json','r') as verfile:
        known_versions = json.load(verfile)
        known = str(known_versions[tp][-1])
    return known

def append_known(tp, version):
    global known_versions

    if version not in known_versions[tp]:
        known_versions[tp].append(unicode(version))
        with open('known_versions.json','w') as verfile:
            verlist = json.dumps(known_versions, indent=4, sort_keys=True)
            verfile.write(verlist)
    else:
        print("Version " + version + " already known.")

def prepare_msg(tp, version, url):
    global message
    if tp == 'g870a':
        package = 'the G870A'
    elif tp == 'qbt':
        package = 'qBittorrent'
    elif tp == 'kpxc':
        package = 'KeePassXC'

    text = 'A new update for %s is released:\n%s\nDownload here: %s'

    message = text % (package, str(version), str(url))
    return message

def send_bot_msg(message):
    user_id = os.environ['USER_ID']
    bot = telepot.Bot(os.environ['BOT_TOKEN'])
    bot.sendMessage(user_id, message)

def find_g870a_update():
    tp = 'g870a'
    get_current(tp)

    headers = {'Accept': 'application/json'}

    r = requests.get('https://services.att.com/kmservices/v2/contents/KM1126238?app-id=esupport', headers=headers)

    data = r.json()

    xml = data['resultBody']['contentTypeProperties']['currentsoftdetails']
    # xml2 = data['resultBody']['contentTypeProperties']['currentsoftupd']

    # soup = BeautifulSoup(xml,'html.parser')

    # Current version
    pos = xml.find("Baseband version:",0)
    verpos = xml.find("G870A",pos+17,pos+57)
    version = xml[verpos:verpos+13]

    # Previous version
    prev = xml.rfind("Previous versions required:",0)
    prev_ver = xml.find("G870A",prev+27)
    previous_version = xml[prev_ver:prev_ver+13]

    url =  'https://xdmd.sl.attcompute.com/agents/42998/1488/SS-' + previous_version + '-to-' + version[7:] + '-UP'

    prepare_msg(tp, version, url)

    if version != known:
        send_bot_msg(message)
        print(url)
        append_known(tp, version)
    else:
        print('No new version for G870A')

def find_qbt_update():
    tp = 'qbt'
    get_current(tp)

    html = requests.get('https://www.qbittorrent.org/news.php')
    soup = BeautifulSoup(html.text,'html.parser')
    verstring = str(soup.p.string)

    endpos = verstring.find(' was',0)
    verpos = verstring.find('3', 0)
    version = str(verstring[verpos-1:endpos])
    url = 'https://sourceforge.net/projects/qbittorrent/files/qbittorrent/qbittorrent-' + version[1:] + '/qbittorrent-' + version[1:] + '.tar.gz/download'

    prepare_msg(tp, version, url)

    if version != known:
        send_bot_msg(message)
        print(url)
        append_known(tp, version)
    else:
        print('No new version for qBittorrent')

def find_kpxc_update():
    tp = 'kpxc'
    get_current(tp)

    html = requests.get('https://keepassxc.org/blog/feed.xml')
    soup = BeautifulSoup(html.text,'html.parser')
    verstring = str(soup.item.title)

    verpos = verstring.find('KeePassXC ', 0)
    endpos = verstring.find(' released',0)
    version = str(verstring[verpos+10:endpos])
    url = str(soup.item.guid.string)

    prepare_msg(tp, version, url)

    if version != known:
        send_bot_msg(message)
        print(url)
        append_known(tp, version)
    else:
        print('No new version for KeePassXC')

schedule.every().day.at("00:00").do(do_updates)
schedule.every().day.at("12:00").do(do_updates)

do_updates()

try:
    while True:
        schedule.run_pending()

        time.sleep(30)

except KeyboardInterrupt:
    print "Terminated!"
