import pickle
from collections import defaultdict

class GradeSheet:
    def __init__(self):
        self._grade = defaultdict(list)

    def receive(self, week_number, graded_homeworks):
        for hw in graded_homeworks:
            graded = {}
            graded['name'] = hw.name
            graded['login'] = hw.login
            graded['score'] = hw.final_score
            graded['expected'] = hw.expected_score
            graded['ambiguity'] = hw.ambiguity
            self._grade[week_number].append(graded)

    def to_pickle(self, file_name):
        with open(file_name, "wb") as fp:
            pickle.dump(self._grade, fp)

    def read_pickle(self, file_name):
        with open(file_name, "rb") as fp:
            self._grade = pickle.load(fp)
