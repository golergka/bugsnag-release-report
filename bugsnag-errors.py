#!/usr/bin/python

import requests
import sys
import argparse
import re
from tabulate import tabulate

def load_errors(api_key, project_id, severity, release_stages):
    sys.stdout.write('Getting issues from bugsnag')
    sys.stdout.flush()

    headers = {'Authorization': 'token ' + api_key}
    payload = {'severity': severity, 'release_stages': release_stages }
    url = 'https://api.bugsnag.com/projects/' + project_id + '/errors'
    errors = {}

    while url != None:
	response = requests.get(url, params=payload, headers=headers)
	for err in response.json():
	    errors[err['id']] = err

	if 'next' in response.links and 'url' in response.links['next']:
	    url = response.links['next']['url']
	else:
	    url = None

	sys.stdout.write(".")
	sys.stdout.flush()

    sys.stdout.write('\n')

    return errors

def main():
    parser = argparse.ArgumentParser(description='Count errors of your project on Bugsnag')
    parser.add_argument('--api-key', type=str, help='API Key for authorization', required=True, dest='api_key')
    parser.add_argument('--project-id', type=str, help='Project Id', required=True, dest='project_id')
    parser.add_argument('--severity', type=str, help='Issue severity filter', default='error')
    parser.add_argument('--release-regex', type=str, help='Regex to group version strings by', default=ur'[0-9]*\.[0-9]*\.[0-9]*', dest='release_regex')
    parser.add_argument('--release-stages', type=str, help='Release stages to filter on', default='Production,Test', dest='release_stages')
    args = parser.parse_args()

    errors = load_errors(args.api_key, args.project_id, args.severity, args.release_stages)

    print 'Total error count: ' + str(len(errors))

    errors_by_release = {}

    release_filter = re.compile(args.release_regex)

    for err in errors.values():
	for v in err['app_versions'].keys():
	    ver = re.match(release_filter, v).group(0)
	    if ver in errors_by_release:
		errors_by_release[ver] += 1
	    else:
		errors_by_release[ver] = 1

    print tabulate(sorted(errors_by_release.items()), headers=['Release', 'Errors'])

if __name__ == "__main__":
    main()
