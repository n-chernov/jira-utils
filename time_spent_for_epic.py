"""
This script reads all worklogs for specified epic and calculates
how much time has been spent by every contributor
"""
import argparse
from jira import JIRA

parser = argparse.ArgumentParser(description='Get contribution in hours and percents for specified epic')
parser.add_argument('jira')
parser.add_argument('epic')
arg = parser.parse_args()

token = None
with open('token.txt', 'r') as file:
    token = file.read()

token = token.strip('\n') # for some reason \n appears in string after reading from file

jira_options = {'server': arg.jira}
jira = JIRA(options=jira_options, token_auth=token)

query = f'"Epic Link" = {arg.epic} or issueFunction in subtasksOf(\'"Epic Link" = {arg.epic}\')'
print('Getting list of tasks...')
tasks = jira.search_issues(query)

contribution = dict()
total_time_sec = 0

for task in tasks:
    print('Getting list of worklogs for task', task)
    worklogs = jira.worklogs(task)
    print(len(worklogs), 'worklogs found')
    for worklog in worklogs:
        name = worklog.raw['author']['displayName']
        time_sec = worklog.raw['timeSpentSeconds']
        print(name, time_sec, 'seconds')
        time_sec_prev = 0
        if name in contribution:
            time_sec_prev = contribution[name]
        contribution[name] = time_sec_prev + time_sec
        total_time_sec = total_time_sec + time_sec

print('\n--- Contribution to epic', arg.epic, '---\n')

for name, time_sec in contribution.items():
    time_h = time_sec / 3600
    share = time_sec / total_time_sec
    share_percents = int(share*100)
    print(f'{name}: {time_h:.1f} hours, {share_percents}%')
