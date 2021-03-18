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
print(f'\nGetting list of issues in epic {arg.epic}...')
issues = jira.search_issues(query)

estimations = dict()
time_spent = dict()
summaries = dict()
untracked_issues = set()  # issues which doesn't have either estimation or worklogs
total_time_estimated = 0
total_time_spent = 0
spent_in_estimated_tasks = 0
for issue in issues:
    issue_key = issue.raw['key']
    estimation = issue.raw['fields']['timeoriginalestimate']
    spent = issue.raw['fields']['timespent']
    summaries[issue_key] = issue.raw['fields']['summary']
    if estimation is not None:
        estimations[issue_key] = estimation
        total_time_estimated = total_time_estimated + estimation
    else:
        untracked_issues.add(issue_key)
    if spent is not None:
        time_spent[issue_key] = spent
        total_time_spent = total_time_spent + spent
    else:
        untracked_issues.add(issue_key)
    if estimation is not None and spent is not None:
        spent_in_estimated_tasks = spent_in_estimated_tasks + spent


def print_issue_details(key):
    est = 0.0
    sp = 0.0
    if key in estimations:
        est = estimations[key]/3600
    if key in time_spent:
        sp = time_spent[key]/3600
    print(f'{key} - {summaries[key]}: estimation is {est:.1f} h, logged {sp:.1f} h')


total_time_estimated_h = total_time_estimated / 3600
total_time_spent_h = total_time_spent / 3600
spent_in_estimated_tasks_h = spent_in_estimated_tasks / 3600
print('\n--- Total:')
print(f'Estimate:                  {total_time_estimated_h:.1f} h')
print(f'Logged:                    {total_time_spent_h:.1f} h')
print(f'Logged in estimated tasks: {spent_in_estimated_tasks_h:.1f} h')


print('\n--- Following tasks were finished in time:')
for key in estimations:
    if key in estimations and key in time_spent:
        if estimations[key] >= time_spent[key]:
            print_issue_details(key)

print('\n--- Following tasks were underestimated:')
for key in estimations:
    if key in estimations and key in time_spent:
        if estimations[key] < time_spent[key]:
            print_issue_details(key)

print('\n--- Issues without estimations or/and worklogs:')
for key in untracked_issues:
    print_issue_details(key)
