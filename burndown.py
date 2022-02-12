import argparse
from getpass import getpass
from jira import JIRA

from jira_utils_common import seconds_to_hours_str

parser = argparse.ArgumentParser(description='Get data for burndown chart')
parser.add_argument('jira')
parser.add_argument('username')
parser.add_argument('epic')
arg = parser.parse_args()

password = getpass()

jira_options = {'server': arg.jira}
jira = JIRA(options=jira_options, basic_auth=(arg.username, password))

query = f'"Epic Link" = {arg.epic} or issueFunction in subtasksOf(\'"Epic Link" = {arg.epic}\')'
print('Getting list of issues...')
issues = jira.search_issues(query, fields='timetracking')

total_original_estimate_sec = 0

for issue in issues:
    print(issue.key)
    try:
        original_estimate_sec = issue.fields.timetracking.originalEstimateSeconds
        total_original_estimate_sec = total_original_estimate_sec + original_estimate_sec
    except (AttributeError, TypeError):
        pass

print('Original estimation = ', seconds_to_hours_str(total_original_estimate_sec), 'hours')
