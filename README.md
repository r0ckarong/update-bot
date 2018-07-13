= Update Bot

This script checks various software packages for new release announcements in their
release streams and sends a message to the user via Telegram bot API.

Written in (currently) Python 3.6 compliant syntax

== Requires

NOTE: It's highly recommended to set up a virtual environment based on the `requirements.txt`-file

----
pip3 install requests schedule bs4 telepot python-gist
----

* Python 3.6.x (tested on 3.6.5)
* Requests 2.18.x
* link:https://docs.python.org/3.6/library/argparse.html[argparse]
* link:https://docs.python.org/3.6/library/subprocess.html[subprocess]
* link:https://docs.python.org/3.6/library/errno.html[errno]
* link:https://docs.python.org/3.6/library/json.html[json]
* link:https://www.crummy.com/software/BeautifulSoup/[BeautifulSoup4]
* link:https://github.com/nickoala/telepot[telepot]
* link:https://github.com/dbader/schedule[schedule]
* link:https://pypi.org/project/python-gist/[python-gist]
* link:https://github.com/PyGithub/PyGithub[pygithub]
* Set up a `~/.gist` file with
+
----
[gist]
token: 12350117510510urtoken131591378
editor: /usr/bin/vim
----

== Program description

What it's supposed to do:

The program starts and sends a message to the user(s) that it has started successfully and is now watching for updates

Read a package.json file that contains a number of definitions for things that need to be checked
Those include the URLs where the announcements happen and where the actual DL can be found (or base URL that can be used to calculate the final download link)
it also includes a list of versions already known to the program that should be ignored (or compared to be lower).

The program retrieves the file from a GitHub Gist
It parses the information and stores the package information and versions in variables
Then it performs requests against the separate repositories/locations to compare current versions with the known information
If the known information is outdated it retrieves the latest release name/version and appends this to the internal data
Then it calculates/retrieves the download links for the new release
Then the program prepares a message using telegram that includes the package name, version and download link
it sends this message to the specified user(s)
Finally the package information is updated in the local file and uploaded back to gist

== Package File Description

JSON Array of packages with these fields:

. `name`: Name of Package
. `description`: Description of package or file
. `source`: URL of the page to monitor for announcements
. `download`: Combined URL for file download
. `type`: tag/release GitHub type that the information needs to get parsed for
also 'binary' for non GitHub files
. `more`: Addtional stuff needed or useful for data extraction
. `comment`: Explaining the contents of more
. `versions`: List of versions known to the program

== Version File Description

JSON objects of packages with arrays of versions, ordered by highest ascending
