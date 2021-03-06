import re
import requests
from requests.exceptions import ConnectionError


def extract_url(string):
    """ Extract URL from given string

    :param string:
    :return: url
    """
    url = re.findall(r'(https?://\S+)', string)
    if not url:
        url = None
    else:
        url = url[0].replace(")", "")
    return url


def url_exists(url):
    """ Check url is exists or not

    :param url: url
    :return: response code
    """
    try:
        r = requests.head(url)
        code = r.status_code
    except ConnectionError, e:
        code = 404
    return code


class Homework:
    def __init__(self, email, login, title, submitted_at, commits, files):
        self.name = None
        self.email = email
        self.login = login
        self.title = title
        self.submitted_at = submitted_at
        self.commits = commits
        self.files = files
        self.ans_urls = []
        self.ans_sheets = []
        self.expected_score = 0
        self.scores = []
        self.ambiguity = False
        self.final_score = 0

    def set_final_scores(self):
        try:
            self.final_score = max(self.scores)
        except:
            self.final_score = 0
            self.ambiguity = True

    def set_name(self):
        # for debugging purpose
        # print "===", self.name
        names = []
        regex = r"^#{1,3} [Nn]ame$"
        rx = re.compile(regex)

        for ans_sheet in self.ans_sheets:
            for index in range(len(ans_sheet)):
                result = rx.search(ans_sheet[index]['head'])
                if result is not None:
                    names.append(ans_sheet[index]['main'])

        try:
            self.name = max(names)
        except:
            self.name = self.login

    def set_expected_score(self):
        scores = []
        #regex_score = r"^([0-9]{1,3})/[0-9]{1,3}.*"
        regex_score = r"^([0-9]{1,3})"
        rx_score = re.compile(regex_score)
        regex_point_sentence = r"^#{1,3} How many points .*"
        rx_point_sentence = re.compile(regex_point_sentence)

        for ans_sheet in self.ans_sheets:
            for index in range(len(ans_sheet)):
                head = ans_sheet[index]['head']
                # for debugging purpose
                # print ans_sheet[index]['head']

                if rx_point_sentence.search(head) is not None:
                    result = rx_score.search(ans_sheet[index]['main'])

                    if result is not None:
                        scores.append(int(result.group(1)))

        self.expected_score = max(scores)

    def set_urls(self):
        for idx1, ans_sheet in enumerate(self.ans_sheets):
            for idx2 in range(len(ans_sheet)):
                url = extract_url(ans_sheet[idx2]['main'])
                if url is not None:
                    self.ans_sheets[idx1][idx2].update({'url': url})
                    r = url_exists(url)
                    if r == 404:
                        self.ans_sheets[idx1][idx2].update(
                            {'valid_url': False})
                    else:
                        """
                        response codes:

                        403: forbidden
                        30x: server redirect
                        200: OK
                        """
                        self.ans_sheets[idx1][idx2].update(
                            {'valid_url': True})
