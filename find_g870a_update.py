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
