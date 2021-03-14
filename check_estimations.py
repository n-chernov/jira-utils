# Check if estimations for each task in epic were correct

import argparse
from getpass import getpass
from jira import JIRA

parser = argparse.ArgumentParser(description='Check if estimations for each task in epic were correct')
parser.add_argument('jira')
parser.add_argument('username')
parser.add_argument('epic')
arg = parser.parse_args()

password = getpass()

jira_options = {'server': arg.jira}
jira = JIRA(options=jira_options, basic_auth=(arg.username, password))

query = f'"Epic Link" = {arg.epic} or issueFunction in subtasksOf(\'"Epic Link" = {arg.epic}\')'
print('Getting list of issues...')
issues = jira.search_issues(query)

estimations = dict()
time_spent = dict()
summaries = dict()
untracked_issues = []
for issue in issues:
    issue_key = issue.raw['key']
    estimation = issue.raw['fields']['timeoriginalestimate']
    spent = issue.raw['fields']['timespent']
    summaries[issue_key] = issue.raw['fields']['summary']
    if estimation is not None and spent is not None:
        estimations[issue_key] = estimation
        time_spent[issue_key] = spent
    else:
        untracked_issues.append(issue_key)


def print_issue_details(key):
    est = estimations[key]/3600
    spent = time_spent[key]/3600
    print(f'{key} - {summaries[key]}: estimation is {est:.1f} h, spent {spent:.1f} h')


print('\n--- Following tasks were finished in time:')
for key in estimations:
    if estimations[key] >= time_spent[key]:
        print_issue_details(key)

print('\n--- Following tasks were underestimated:')
for key in estimations:
    if estimations[key] < time_spent[key]:
        print_issue_details(key)

print('\n--- Issues without estimations or/and worklogs:')
for key in untracked_issues:
    print(f'{key} - {summaries[key]}')
