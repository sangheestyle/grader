import pickle
from collections import defaultdict
import pandas as pd


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

    def to_excel(self, file_name):
        brief_df = self.get_brief()
        brief_df.to_excel(file_name)

    def get_brief(self):
        base_df = pd.DataFrame()
        for week in self._grade:
            index = week
            logins = []
            scores = []
            for entry in self._grade[week]:
                logins.append(entry['login'])
                expected = entry['expected']
                score = entry['score']
                scores.append(max(expected, score))
            week_sheet = pd.DataFrame([scores], columns=logins, index=[index])
            base_df = pd.concat([base_df, week_sheet])
        return base_df


if __name__=="__main__":
    a = GradeSheet()
    a.read_pickle('../scored/grade_sheet1-9.pkl')
    a.to_excel('1-9.xls')