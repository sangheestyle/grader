import argparse

import getpass
from grace.grader import Grader
from grace.homework import Homework
from grace.grade_sheet import GradeSheet

"""
Specifically speaking, this grader can be grading on
CSCI-4830-002-2014

Example)
project = "challenge-week-1"
"""

parser = argparse.ArgumentParser(description='Grading CSCI-4830')
parser.add_argument('--id', help="Github ID",
                    type=str, required=True)
parser.add_argument('--user', help="Github user",
                    type=str, default='CSCI-4830-002-2014', required=False)
parser.add_argument('--project_prefix', help="Project prefix",
                    type=str, default='challenge-week-', required=False)
parser.add_argument('--begin_n', help="Start week",
                    type=int, required=True)
parser.add_argument('--end_n', help="End week",
                    type=int, required=True)
parser.add_argument('--o', help="Output file path",
                    type=str, required=True)
args = parser.parse_args()

username = args.id
password = getpass.getpass("Enter github password: ")
user = args.user
gs = GradeSheet()
for week_number in range(args.begin_n, args.end_n+1):
    project = args.project_prefix + str(week_number)
    print "===", project
    grace = Grader("Grace")
    grace.set_project(project)
    grace.login(username, password)
    grace.retrieve_correct_ans(user, project)
    grace.retrieve_homeworks(user, project)
    grace.grading()
    grace.report()
    gs.receive(int(project[-1]), grace.get_homeworks())
gs.sync_name_login()
gs.to_excel('1-9.xls')