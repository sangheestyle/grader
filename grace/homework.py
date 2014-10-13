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
        for idx, ans_sheet in enumerate(self.ans_sheets):
            for index in range(len(ans_sheet)):
                url = self._extract_url(ans_sheet[index]['main'])
                if url is not None:
                    self.ans_sheets[idx][index].update({'url':url})
                    resp = self._open_url(url)
                    if resp == 404:
                        self.ans_sheets[idx][index].update({'valid_url':False})
                    elif resp == 403:
                        """
                        Forbidden
                        """
                        self.ans_sheets[idx][index].update({'valid_url':True})
                        self.ans_sheets[idx][index].update({'url_contents':resp})
                    else:
                        try:
                            self.ans_sheets[idx][index].update({'valid_url':True})
                            self.ans_sheets[idx][index].update({'url_contents':
                                                                resp.read()})
                        except:
                            self.ans_sheets[idx][index].update({'valid_url':True})
                            self.ans_sheets[idx][index].update({'url_contents':
                                                                 resp})


