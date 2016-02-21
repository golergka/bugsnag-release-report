#!/usr/bin/python

import requests
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Count errors of your project on Bugsnag')
    parser.add_argument('--api-key', type=str, help='API Key for authorization', required=True, dest='api_key')
    parser.add_argument('--project-id', type=str, help='Project Id', required=True, dest='project_id')
    parser.add_argument('--severity', type=str, help='Issue severity filter', default='error')
    parser.add_argument('--release-regex', type=str, help='Regex to group version strings by', default=ur'[0-9]*\.[0-9]*\.[0-9]*', dest='release_regex')
    args = parser.parse_args()

    sys.stdout.write('Getting issues from bugsnag')
    sys.stdout.flush()

    headers = {'Authorization': 'token ' + args.api_key}
    payload = {'severity': args.severity}
    url = 'https://api.bugsnag.com/projects/' + args.project_id + '/errors'
    error_list = []

    page_limit = None

    while url != None and (page_limit == None or page_limit > 0):
	response = requests.get(url, params=payload, headers=headers)
	error_list.extend(response.json())

	if 'next' in response.links and 'url' in response.links['next']:
	    url = response.links['next']['url']
	else:
	    url = None

	if page_limit != None:
	    page_limit = page_limit - 1

	sys.stdout.write(".")
	sys.stdout.flush()

    sys.stdout.write('\n')

    print 'Total error count: ' + str(len(error_list))

    errors_by_versions = {}

    import re

    release_filter = re.compile(args.release_regex)

    for err in error_list:
	for v in err['app_versions'].keys():
	    ver = re.match(release_filter, v).group(0)
	    if ver in errors_by_versions:
		errors_by_versions[ver] += 1
	    else:
		errors_by_versions[ver] = 1

    from tabulate import tabulate

    print tabulate(sorted(errors_by_versions.items()), headers=['Release', 'Errors'])

if __name__ == "__main__":
    main()
