from github import Github
import subprocess
import os
import json
from pprint import pprint
import gist
gh_token = os.environ['GH_TOKEN']
gh = Github(gh_token)
gist_id = "dac9c4de15c7b061e7851fe1105a16d3"
package_list = subprocess.check_output(['gist', 'content', gist_id, 'packages.json'], universal_newlines=True)
input_package_list = json.loads(package_list)['packages']
