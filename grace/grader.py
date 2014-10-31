import urllib2
import re
import difflib

import pandas as pd
from github import Github
from homework import Homework

# submission source types
SRC_TYPES = (".js", ".json")

def _correct_source_link(ans, hw):
    """
    Check the answer has source code link over than 1 line

    :param ans: homework answer
    :param hw: homework object for using files
    :return: True if the number of code line is over than 1 line
    """
    result = False
    regex = re.compile(r"\[(.*?)\](.*?)\((.*?)\)")
    source_code_path = regex.findall(ans)
    source_raw_url = set()
    paths = set(p for path_pair in source_code_path for p in path_pair)
    paths = [p for p in paths if p.endswith(SRC_TYPES)]
    for f in hw.files:
        for p in paths:
            if f.raw_url.endswith(p):
                source_raw_url.add(f.raw_url)

    if (source_code_path is not None) and (len(source_raw_url) > 0):
        for url in source_raw_url:
            response = urllib2.urlopen(url)
            res_len = response.readlines()
            if res_len > 0:
                result = True
    return result


def _similar(text_a, text_b, trasholder=0.991):
    text_a = text_a.strip().lower()
    text_b = text_b.strip().lower()
    seq = difflib.SequenceMatcher(None, text_a, text_b)
    return seq.ratio() > trasholder


def md_to_ans_form(md):
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
            ans_form[head_cnt] = {"head": head, "main": main}
            head = line
            main = ""
            head_cnt += 1
        elif (not line.startswith('#')) and (head is None):
            continue
        else:
            main += line
    ans_form[head_cnt] = {"head": head, "main": main}
    return ans_form


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
        print ">>> Hello " + username + "! " + "I am " + self.name + "!"
        self.github_instance = Github(username, password)

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
        raw_ans_form = md_to_ans_form(response)
        self.correct_ans = self.parse_ans(raw_ans_form)

    def retrieve_homeworks(self, user, project):
        print ">>> Retrieving homeworks"
        pulls = self.github_instance.get_user(user). \
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
        for hw in self.homeworks:
            for f in hw.files:
                result = rx.search(f.raw_url)
                if result is not None:
                    hw.ans_urls.append(f.raw_url)
                    response = urllib2.urlopen(f.raw_url)
                    hw.ans_sheets.append(md_to_ans_form(response))
            hw.set_name()
            hw.set_expected_score()
            hw.set_urls()

    def _check_anss(self, ans, hw):
        score = 0
        for i, q in enumerate(self.correct_ans):
            if self.correct_ans[q]["is_question"] is True:
                cor_ans = self.correct_ans[q]["main"]
                home_ans = ans[i]["main"]
                if _similar(cor_ans, home_ans) is True:
                    # Check the source link containing source code
                    if _correct_source_link(home_ans, hw):
                        score += int(self.correct_ans[q]["point"])
                    else:
                        continue
                else:
                    if "valid_url" in ans:
                        if ans["valid_url"]:
                            score += int(self.correct_ans[q]["point"])
                        else:
                            continue
                    else:
                        score += int(self.correct_ans[q]["point"])
        return score

    def grading(self):
        print ">>> Grading"
        for hw in self.homeworks:
            print "Hey ", hw.name + "!"
            for ans in hw.ans_sheets:
                print "---"
                print self.correct_ans.keys()
                print ans.keys()
                if len(ans.keys()) == 18:
                    print ans
                if self.correct_ans.keys() == ans.keys():
                    score = self._check_anss(ans, hw)
                    hw.scores.append(score)
                else:
                    print ">>> KeyError, Check the number of answer: ", hw.name + "!"

            hw.set_final_scores()
            hw.ambiguity = self.check_ambiguity(hw)

    def check_ambiguity(self, hw):
        ambiguity = False
        if len(hw.ans_urls) > 1:
            ambiguity = True

        for ans_sheet in hw.ans_sheets:
            if len(ans_sheet) != len(self.correct_ans):
                ambiguity = True

        return ambiguity

    def check_deadline(self, deadline):
        pass

    def report(self):
        print ">>> Reporting"
        print "{0:20} {1:6} {2:6} {3:}".format( \
            "name", "score", "expect", "ambiguous")
        for hw in self.homeworks:
            print "{0:20} {1:6d} {2:6d} {3:}".format( \
                hw.name, hw.final_score,
                hw.expected_score, hw.ambiguity)

    def get_homeworks(self):
        return self.homeworks