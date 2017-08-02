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
