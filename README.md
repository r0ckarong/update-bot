# Update Bot

This script checks various software packages for new release announcements in their
release streams and sends a message to the user via Telegram bot.

Written (currently) in Python 3.x compliant syntax.

## Requires:

* Python 3.x
* Requests 2.18.x
* json
* BeautifulSoup4
* telepot
* schedule
* python-gist
* Set up a `~/.gist` file with
+
----
[gist]
token: 12350117510510urtoken131591378
editor: /usr/bin/vim
----


## Package File Description

JSON Array of packages with these fields:

. name: Name of Package
. description: Description of package or file
. src-url: URL of the page to monitor for announcements
. dl-url: Combined URL for file download
. type: tag/release GitHub type that the information needs to get parsed for
also 'binary' for non GitHub files
. more: Addtional stuff needed or useful for data extraction
. comment: Explaining the contents of more


JSON Structure
{
 `packages` list [
  {`package` object}
 ]
}

## Version File Description

JSON objects of packages with arrays of versions, ordered by highest ascending


<!--

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


 -->
