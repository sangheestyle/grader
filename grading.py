import getpass
from grace.grader import Grader
from grace.homework import Homework

"""
Specifically speaking, this grader can be grading on
CSCI-4830-002-2014

Example)
project = "challenge-week-1"
"""

username = raw_input("Enter github ID: ")
password = getpass.getpass("Enter github password: ")
user = "CSCI-4830-002-2014"
project = raw_input("Enter github project: ")

grace = Grader("Grace")
grace.set_project(project)
grace.login(username, password)
grace.retrieve_correct_ans(user, project)
grace.retrieve_homeworks(user, project)
grace.grading()
grace.report()
