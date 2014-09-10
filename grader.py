import getpass
import urllib2
import re
import difflib
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
    def __init__(self, name):
        self.name = name
        self.github_instance = None
        self.correct_answer = ''
        self.homeworks = []

    def login(self, username, password):
        print ">>> Hello " + username +"! " + "I am " + self.name + "!"
        self.github_instance = Github(username, password)

    def md_to_ans_form(self, md):
        ans_form = {}
        head_contents = None
        main_contents = ""
        head_cnt = 0
        for index, line in enumerate(md.readlines()):
            if (line.startswith('#')) and (head_contents is None):
                # new head is started
                head_contents = line
            elif (line.startswith('#')) and (head_contents is not None):
                # make new dict item
                ans_form[head_cnt] = {"head_contents": head_contents,
                                      "main_contents": main_contents}
                head_contents = line
                main_contents = ""
                head_cnt += 1
            else:
                main_contents += line
        ans_form[head_cnt] = {"head_contents": head_contents,
                              "main_contents": main_contents}
        return ans_form

    def fill_header_properties(self, raw_ans_form, def_point=5):
        for index, item in enumerate(raw_ans_form):
            is_question = False
            point = 0
            main_contents = raw_ans_form[item]["main_contents"]
            if (main_contents.strip() is not '') and (int(item) > 1):
                is_question = True
            raw_ans_form[item].update({"is_question": is_question})

            if is_question:
                head_contents = raw_ans_form[item]["head_contents"]
                regex = r"\(([0-9]{1,2}) points\)"
                rx = re.compile(regex)
                result = rx.search(head_contents)
                if (result is None):
                    point = def_point
                else:
                    point = result.group(1)
            else:
                point = 0
            raw_ans_form[item].update({"is_question": is_question,
                                       "point": point})
        return raw_ans_form

    def retrieve_correct_answer(self, user, project, filename="README.md"):
        print ">>> Retrieving correct answer"
        branch = "master"
        url = "https://raw.githubusercontent.com/" + \
              "/" + user + \
              "/" + project + \
              "/" + branch + \
              "/" + filename
        response = urllib2.urlopen(url)
        raw_ans_form = self.md_to_ans_form(response)
        self.correct_answer = self.fill_header_properties(raw_ans_form)

    def retrieve_homeworks(self, user, project):
        print ">>> Retrieving homeworks"
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
                    homework.answer_sheets.append(self.md_to_ans_form(response))

    def _similar(self, text_a, text_b, trasholder=0.991):
        text_a = text_a.strip().lower()
        text_b = text_b.strip().lower()
        seq = difflib.SequenceMatcher(None, text_a, text_b)
        return seq.ratio() > trasholder

    def _check_answers(self, homework):
        score = 0
        for index, question in enumerate(self.correct_answer):
            if self.correct_answer[question]["is_question"] is True:
                cor_ans = self.correct_answer[question]["main_contents"]
                home_ans = homework[index]["main_contents"]
                if self._similar(cor_ans, home_ans) is True:
                    continue
                else:
                    score += int(self.correct_answer[question]["point"])

        return score

    def grading(self):
        print ">>> Grading"
        for homework in self.homeworks:
            print "Hey ", homework.login + "!"
            for answer in homework.answer_sheets:
                score = self._check_answers(answer)
                homework.scores.append(score)
            homework.set_final_scores()
            homework.ambiguity = self.check_ambiguity(homework)

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

    def report(self):
        print ">>> Reporting"
        for homework in self.homeworks:
            print homework.login, homework.final_score, homework.ambiguity


if __name__ == "__main__":
    """
    Specifically speaking, this grader can be grading on
    CSCI-4830-002-2014

    Example)
    project = "challenge-week-1"
    """

    grace = Grader("Grace")

    username = raw_input("Enter github ID: ")
    password = getpass.getpass("Enter github password: ")
    user = "CSCI-4830-002-2014"
    project = raw_input("Enter github project: ")

    grace.login(username, password)
    grace.retrieve_correct_answer(user, project)
    grace.retrieve_homeworks(user, project)
    grace.grading()
    grace.report()
