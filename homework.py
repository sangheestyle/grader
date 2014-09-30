import re

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
        self.final_score = max(self.scores)

    def set_name(self):
        names = []
        regex = r"^#{1,3} [Nn]ame$"
        rx = re.compile(regex)

        for answer_sheet in self.answer_sheets:
            for index in range(len(answer_sheet)):
                result = rx.search(answer_sheet[index]['head_contents'])
                if result is not None:
                    names.append(answer_sheet[index]['main_contents'])

        self.name = max(names)

    def set_expected_score(self):
        scores = []
        regex_score = r"^([0-9]{1,3})/[0-9]{1,3}.*"
        rx_score = re.compile(regex_score)
        regex_point_sentence = r"^#{1,3} How many points .*"
        rx_point_sentence = re.compile(regex_point_sentence)

        for answer_sheet in self.answer_sheets:
            for index in range(len(answer_sheet)):
                head_contents = answer_sheet[index]['head_contents']

                if rx_point_sentence.search(head_contents) is not None:
                    result = rx_score.search(answer_sheet[index]['main_contents'])

                    if result is not None:
                        scores.append(int(result.group(1)))

        self.expected_score = max(scores)
