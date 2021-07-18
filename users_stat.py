import argparse
from getpass import getpass
from jira import JIRA


def get_number_of_issues(query):
    issues = jira.search_issues(query, maxResults=1)
    return issues.total


def reported_issues(name, thisYear = False):
    query = f'reporter = {name}'
    if thisYear:
        query += ' and created  >= startOfYear()'
    return get_number_of_issues(query)


def resolved_issues(name, thisYear = False):
    query = f'"resolved by" = {name}'
    if thisYear:
        query += ' and resolved >= startOfYear()'
    return get_number_of_issues(query)


def closed_issues(name, thisYear = False):
    query = f'status changed to closed by {name}'
    if thisYear:
        query += ' and closed >= startOfYear()'
    return get_number_of_issues(query)


def write_row(file, list_of_values):
    str = ''
    for entry in list_of_values:
        str += f'{entry};'
    file.write(str + '\n')


parser = argparse.ArgumentParser(description='Get some statistics for specified group')
parser.add_argument('jira')
parser.add_argument('username')
parser.add_argument('users_filename')
parser.add_argument('result_filename')
arg = parser.parse_args()

users_file = open(arg.users_filename, 'r')
user_names = users_file.readlines()

password = getpass()
jira_options = {'server': arg.jira}
jira = JIRA(options=jira_options, basic_auth=(arg.username, password))

users_stat = dict()

for user_name in user_names:
    user_name = user_name.strip()
    if len(user_name) == 0:
        continue
    print(f'Getting data for {user_name}...')
    try:
        users_stat[user_name] = dict()
        users_stat[user_name]['reported'] = reported_issues(user_name)
        users_stat[user_name]['resolved'] = resolved_issues(user_name)
        users_stat[user_name]['closed'] = closed_issues(user_name)
        users_stat[user_name]['reported_this_year'] = reported_issues(user_name, thisYear=True)
        users_stat[user_name]['resolved_this_year'] = resolved_issues(user_name, thisYear=True)
        users_stat[user_name]['closed_this_year'] = closed_issues(user_name, thisYear=True)
    except:
        print(f'Failed to get data for user {user_name}')

separator = ';'
result_file = open(arg.result_filename, 'w')
write_row(result_file, ['Name', 'Reported', 'Resolved', 'Closed',
                        'Reported this year', 'Resolved  this year', 'Closed  this year'])

for user_name in user_names:
    user_name = user_name.strip()
    if len(user_name) == 0:
        continue
    us = users_stat[user_name]
    write_row(result_file, [user_name, us['reported'], us['resolved'], us['closed']
                            , us['reported_this_year'], us['resolved_this_year'], us['closed_this_year']])

# print(users_stat)
