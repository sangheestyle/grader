import getpass
import urllib2
import re
import difflib
from github import Github
from homework import Homework


class Grader:

    def __init__(self, name):
        self.name = name
        self.github_instance = None
        self.project = None
        self.correct_ans = ''
        self.homeworks = []

        """
        You need to specify what kind of string in header is not question
        including those substring.
        """
        self.substr_not_question = [
        "Show and tell",
        "Name",
        "many points have you",
        "What is the most difficult part",
        "many hours have you spent"]

    def set_project(self, project):
        self.project = project

    def login(self, username, password):
        print ">>> Hello " + username +"! " + "I am " + self.name + "!"
        self.github_instance = Github(username, password)

    def md_to_ans_form(self, md):
        ans_form = {}
        head = None
        main = ""
        head_cnt = 0

        for index, line in enumerate(md.readlines()):
            line = line.rstrip()
            if (line.startswith('#')) and (head is None):
                # new head is started
                head = line
            elif (line.startswith('#')) and (head is not None):
                # make new dict item
                ans_form[head_cnt] = {"head": head,
                                      "main": main}
                head = line
                main = ""
                head_cnt += 1
            elif (not line.startswith('#')) and (head is None):
                continue
            else:
                main += line

        ans_form[head_cnt] = {"head": head,
                              "main": main}

        return ans_form

    def parse_ans(self, raw_ans_form, def_point=5):
        for index, item in enumerate(raw_ans_form):
            is_question = False
            point = 0
            main = raw_ans_form[item]["main"].rstrip()
            head = raw_ans_form[item]["head"].rstrip()

            project_num = re.findall("\d+", self.project)[0]
            if project_num > 4:
                substrings = self.substr_not_question[1:]
            else:
                substrings = self.substr_not_question

            if (main is not '') and not any(substring in head \
                                            for substring in substrings):
                is_question = True

            raw_ans_form[item].update({"is_question": is_question})

            if is_question:
                regex = r"\(([0-9]{1,2}) points\)"
                rx = re.compile(regex)
                result = rx.search(head)
                if (result is None):
                    point = def_point
                else:
                    point = result.group(1)
            else:
                point = 0

            raw_ans_form[item].update({"is_question": is_question,
                                       "point": point})

        return raw_ans_form

    def retrieve_correct_ans(self, user, project, filename="README.md"):
        print ">>> Retrieving correct ans"
        branch = "master"
        url = "https://raw.githubusercontent.com/" + \
              "/" + user + \
              "/" + project + \
              "/" + branch + \
              "/" + filename
        response = urllib2.urlopen(url)
        raw_ans_form = self.md_to_ans_form(response)
        self.correct_ans = self.parse_ans(raw_ans_form)

    def retrieve_homeworks(self, user, project):
        print ">>> Retrieving homeworks"
        pulls = self.github_instance.get_user(user).\
                get_repo(project).get_pulls()

        for pull in pulls:
            hw = Homework(pull.user.email,
                          pull.user.login,
                          project,
                          pull.created_at,
                          pull.get_commits(),
                          pull.get_files())
            self.homeworks.append(hw)

        regex = r".*challenge-week-[0-9]{1,2}/raw/[0-9a-z]{40}/[^/]+?.md$"
        rx = re.compile(regex)

        for homework in self.homeworks:
            for file in homework.files:
                result = rx.search(file.raw_url)

                if result is not None:
                    homework.ans_urls.append(file.raw_url)
                    response = urllib2.urlopen(file.raw_url)
                    homework.ans_sheets.append(
                            self.md_to_ans_form(response))

            homework.set_name()
            homework.set_expected_score()

    def _similar(self, text_a, text_b, trasholder=0.991):
        text_a = text_a.strip().lower()
        text_b = text_b.strip().lower()
        seq = difflib.SequenceMatcher(None, text_a, text_b)

        return seq.ratio() > trasholder

    def _check_anss(self, homework):
        score = 0
        for index, question in enumerate(self.correct_ans):
            if self.correct_ans[question]["is_question"] is True:
                # for debugging
                # print self.correct_ans[question]["head"]
                cor_ans = self.correct_ans[question]["main"]
                home_ans = homework[index]["main"]
                if self._similar(cor_ans, home_ans) is True:
                    continue
                else:
                    score += int(self.correct_ans[question]["point"])

        return score

    def grading(self):
        print ">>> Grading"
        for homework in self.homeworks:
            print "Hey ", homework.name + "!"

            for ans in homework.ans_sheets:
                try:
                    score = self._check_anss(ans)
                    homework.scores.append(score)
                except:
                    print ">>> Some problems on ", homework.name +"!"

            homework.set_final_scores()
            homework.ambiguity = self.check_ambiguity(homework)


    def check_ambiguity(self, homework):
        ambiguity = False
        if len(homework.ans_urls) > 1:
            ambiguity = True

        for ans_sheet in homework.ans_sheets:
            if len(ans_sheet) != len(self.correct_ans):
                ambiguity = True

        return ambiguity

    def check_deadline(self, deadline):
        pass

    def report(self):
        print ">>> Reporting"
        print "{0:20} {1:6} {2:6} {3:}".format(\
                "name", "score", "expect", "ambiguous")
        for homework in self.homeworks:
            print "{0:20} {1:6d} {2:6d} {3:}".format(\
                  homework.name, homework.final_score,
                  homework.expected_score, homework.ambiguity)
