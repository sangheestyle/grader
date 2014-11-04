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

    def to_excel(self, file_name, method="expected"):
        brief_df = self.get_brief(method)
        brief_df.to_excel(file_name)

    def get_brief(self, method="expected"):
        """
        method:
            expected: get max between expected and scored
            score: get scored only
        """
        base_df = pd.DataFrame()
        for week in self._grade:
            index = week
            logins = []
            scores = []
            for entry in self._grade[week]:
                logins.append(entry['name'])
                expected = entry['expected']
                score = entry['score']
                if method == "expected":
                    scores.append(max(expected, score))
                elif method == "score":
                    scores.append(score)
                elif method == "mixed":
                    if expected == score:
                        scores.append(score)
                    else:
                        diff = abs(score-expected)
                        mark = str(score)+"/"+str(expected)+":"+str(diff)
                        if score > expected:
                            mark = mark + "S"
                        else:
                            mark = mark + "E"
                        scores.append(mark)
                else:
                    assert "Don't have methods"
            week_sheet = pd.DataFrame([scores], columns=logins, index=[index])
            base_df = pd.concat([base_df, week_sheet])
        return base_df

    def sync_name_login(self):
        """
        Some people sometimes did not write their name on weekly homework.
        So, need to set their name based on the name on the other weekly homework.
        """
        login_name = defaultdict(set)
        for week in self._grade:
            for entry in self._grade[week]:
                login_name[entry['login']].add(entry['name'])

        login_name_map = {}
        for login in login_name:
            if len(login_name[login]) > 1:
                login_name_map[login] = min([name for name in login_name[login]
                                         if name != login], key=len)
            else:
                login_name_map[login] = list(login_name[login])[0]

        for week in self._grade:
            for entry in self._grade[week]:
                entry['name'] = login_name_map[entry['login']]
