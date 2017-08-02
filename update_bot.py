from bs4 import BeautifulSoup
import requests
import schedule
import telepot
import time
import os
import pdb
import json

import find_g870a_update
import find_qbt_update
import find_kpxc_update

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



schedule.every().day.at("00:00").do(do_updates)
schedule.every().day.at("12:00").do(do_updates)

do_updates()

try:
    while True:
        schedule.run_pending()

        time.sleep(30)

except KeyboardInterrupt:
    print "Terminated!"
