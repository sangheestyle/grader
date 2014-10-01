import unittest
from grace.homework import Homework

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        email = "homework@homework.com"
        login = "homework"
        title = "challenge-week-1"
        submitted_at = ""
        commits = None
        files = None

        self.hw = Homework(email, login, title, submitted_at, commits, files)
        self.hw.answer_sheets = [{0:{'main_contents': 'First Last',
                                     'head_contents': '# Name'},
                                  1:{'main_contents': "90/100(Make your",
                                     'head_contents': '# How many points have'},
                                  2:{'main_contents': 'http://imgur.com/mC2uo',
                                     'head_contents': '## Checkpoint 1 (10 points)'}}
                                ]

    def test_set_name(self):
        self.hw.set_name()
        self.assertEqual(self.hw.name, 'First Last')

    def test_set_expected_score(self):
        self.hw.set_expected_score()
        self.assertEqual(self.hw.expected_score, 90)

    def test_extract_url(self):
        url = "http://abc.com/git/readme.com"
        raw_text = "fad894y89 457437651er7" + url + " http:/d'39"
        self.assertEqual(self.hw._extract_url(raw_text), url)

    def test_set_urls(self):
        self.hw.set_urls()
        self.assertEqual(self.hw.answer_sheets[0][2]['url'], \
                         'http://imgur.com/mC2uo')


if __name__=='__main__':
    unittest.main()
