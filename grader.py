import getpass
import urllib2
from github import Github


class Homework:
    def __init__(self, email, login, title, submitted_at, commits, files):
        self.email = email
        self.login = login
        self.title = title
        self.submitted_at = submitted_at
        self.commits = commits
        self.files = files
        self.answer_urls = []
        self.answer_sheets = []
        self.scores = []
        self.ambiguity = False
        self.final_score = 0

    def set_final_scores(self):
        self.final_score = max(self.scores)


class Grader:
    def __init__(self):
        self.github_instance = None
        self.correct_answer = ''
        self.homeworks = []

    def login(self, username, password):
        self.github_instance = Github(username, password)

    def retrieve_correct_answer(self, user, project, filename="README.md"):
        branch = "master"
        url = "https://raw.githubusercontent.com/" + \
              "/" + user + \
              "/" + project + \
              "/" + branch + \
              "/" + filename
        response = urllib2.urlopen(url)
        self.correct_answer = self.md_to_list(response)

    def md_to_list(self, md):
        raw_answer = ''
        for line in md.readlines():
            if line.startswith('#'):
                raw_answer += 'm'
            elif not line.strip():
                raw_answer += 'b'
            else:
                raw_answer += 'a'
        raw_answer = raw_answer.split("m")
        raw_answer.pop(0)
        for idx, i in enumerate(raw_answer):
            raw_answer[idx] = i.replace('b', '')
            if raw_answer[idx] is not '':
                raw_answer[idx] = 'a'

        return raw_answer

    def retrieve_homeworks(self, user, project):
        pulls = self.github_instance.get_user(user).get_repo(project).get_pulls()
        for pull in pulls:
            hw = Homework(pull.user.email, pull.user.login, project,
                          pull.created_at, pull.get_commits(), pull.get_files())
            # ISSUE: some doesn't have pull.user.email, pull.user.name
            self.homeworks.append(hw)

        for homework in self.homeworks:
            for file in homework.files:
                if file.raw_url.endswith('md'):
                    homework.answer_urls.append(file.raw_url)
                    response = urllib2.urlopen(file.raw_url)
                    homework.answer_sheets.append(self.md_to_list(response))

    def grading(self, total_scores=100, point_per_question=5):
        for homework in self.homeworks:
            for answer_sheet in homework.answer_sheets:
                mark = []
                for index in range(len(self.correct_answer)):
                    if self.correct_answer[index] == '':
                        mark.append('')
                    elif self.correct_answer[index] == answer_sheet[index]:
                        mark.append(True)
                    else:
                        mark.append(False)
                score = total_scores - mark.count(False)*point_per_question
                homework.scores.append(score)
            homework.ambiguity = self.check_ambiguity(homework)
            homework.set_final_scores()

    def check_ambiguity(self, homework):
        ambiguity = False
        if len(homework.answer_urls) > 1:
            ambiguity = True

        for answer_sheet in homework.answer_sheets:
            if len(answer_sheet) != len(self.correct_answer):
                ambiguity = True

        return ambiguity

    def check_deadline(self, deadline):
        pass

    def check_answer(self):
        pass

    def report(self):
        for homework in self.homeworks:
            print homework.login, homework.final_score, homework.ambiguity


if __name__ == "__main__":
    """
    Specifically speaking, this grader can be grading on
    CSCI-4830-002-2014
    """

    g = Grader()
    username = raw_input("Enter github ID: ")
    password = getpass.getpass("Enter github password: ")
    g.login(username, password)
    user = raw_input("Enter github user: ")
    project = raw_input("Enter github project: ")
    g.retrieve_correct_answer(user, project)
    g.retrieve_homeworks(user, project)
    g.grading()
    g.report()
