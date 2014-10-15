import unittest
from grace.homework import Homework, extract_url, url_exists


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        email = "homework@homework.com"
        login = "homework"
        title = "challenge-week-1"
        submitted_at = ""
        commits = None
        files = None

        self.hw = Homework(email, login, title, submitted_at, commits, files)
        self.hw.ans_sheets = [{0:{'main': 'First Last',
                                     'head': '# Name'},
                                  1:{'main': "90/100(Make your",
                                     'head': '# How many points have'},
                                  2:{'main': 'http://imgur.com/mC2uo',
                                     'head': '## Checkpoint 1 (10 points)'}}
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
        self.assertEqual(extract_url(raw_text), url)

    def test_set_urls(self):
        self.hw.set_urls()
        self.assertEqual(self.hw.ans_sheets[0][2]['url'], \
                         'http://imgur.com/mC2uo')

    def test_check_url(self):
        valid_url = r"https://raw.githubusercontent.com/sangheestyle/grader/"\
                     "a2c95a5e952a7f9f4d222c134bf76c83c9611f67/tests.py"
        invalid_url = r"https://raw.githubusercontent.com/sangheestyle/grader/"\
                       "a2c95a5e952a7f9f4d222c134bf76c83c9611f67/tests.py.py"
        self.assertNotEqual(url_exists(valid_url), 404)
        self.assertEqual(url_exists(invalid_url), 404)


if __name__=='__main__':
    unittest.main()
