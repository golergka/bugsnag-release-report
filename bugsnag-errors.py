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
    parser.add_argument('--release-stages', type=str, help='Release stages to filter on', default='Production,Test', dest='release_stages')
    args = parser.parse_args()

    sys.stdout.write('Getting issues from bugsnag')
    sys.stdout.flush()

    headers = {'Authorization': 'token ' + args.api_key}
    payload = {'severity': args.severity, 'release_stages': args.release_stages }
    url = 'https://api.bugsnag.com/projects/' + args.project_id + '/errors'
    errors = {}

    page_limit = None

    while url != None and (page_limit == None or page_limit > 0):
	response = requests.get(url, params=payload, headers=headers)
	for err in response.json():
	    errors[err['id']] = err

	if 'next' in response.links and 'url' in response.links['next']:
	    url = response.links['next']['url']
	else:
	    url = None

	if page_limit != None:
	    page_limit = page_limit - 1

	sys.stdout.write(".")
	sys.stdout.flush()

    sys.stdout.write('\n')

    print 'Total error count: ' + str(len(errors))

    import re

    errors_by_versions = {}

    release_filter = re.compile(args.release_regex)

    for err in errors.values():
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
