import unittest
from homework import Homework

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
                                     'head_contents': '# How many points'},
                                  2:{'main_contents': 'http://imgur.com/mC2uo',
                                     'head_contents': '## Checkpoint 1 (10 points)'}}
                                ]

    def test_set_name(self):
        self.hw.set_name()
        self.assertEqual(self.hw.name, 'First Last')

    def test_set_expected_score(self):
        self.hw.set_expected_score()
        self.assertEqual(self.hw.expected_score, 90)


if __name__=='__main__':
    unittest.main()
