import re
import urllib2

class Homework:
    def __init__(self, email, login, title, submitted_at, commits, files):
        self.name = None
        self.email = email
        self.login = login
        self.title = title
        self.submitted_at = submitted_at
        self.commits = commits
        self.files = files
        self.answer_urls = []
        self.answer_sheets = []
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

        for answer_sheet in self.answer_sheets:
            for index in range(len(answer_sheet)):
                result = rx.search(answer_sheet[index]['head_contents'])
                if result is not None:
                    names.append(answer_sheet[index]['main_contents'])

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

        for answer_sheet in self.answer_sheets:
            for index in range(len(answer_sheet)):
                head_contents = answer_sheet[index]['head_contents']
                # for debugging purpose
                # print answer_sheet[index]['head_contents']

                if rx_point_sentence.search(head_contents) is not None:
                    result = rx_score.search(answer_sheet[index]['main_contents'])

                    if result is not None:
                        scores.append(int(result.group(1)))

        self.expected_score = max(scores)

    def _extract_url(self, text):
        """
        assume one url per one line
        """
        try:
            url =re.findall(r'(https?://\S+)', text)[0]
        except:
            url = None

        return url

    def _open_url(self, url):
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req)
        except urllib2.URLError, e:
            return e.code
        else:
            return resp

    def set_urls(self):
        for idx, answer_sheet in enumerate(self.answer_sheets):
            for index in range(len(answer_sheet)):
                url = self._extract_url(answer_sheet[index]['main_contents'])
                if url is not None:
                    self.answer_sheets[idx][index].update({'url':url})
                    resp = self._open_url(url)
                    if resp == 404:
                        self.answer_sheets[idx][index].update({'valid_url':False})
                    else:
                        self.answer_sheets[idx][index].update({'valid_url':True})
                        self.answer_sheets[idx][index].update({'url_contents':
                                                                resp.read()})

