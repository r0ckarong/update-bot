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
