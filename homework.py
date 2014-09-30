class Homework:
    def __init__(self, email, login, title, submitted_at, commits, files):
        self.email = email
        self.login = login
        self.title = title
        self.submitted_at = submitted_at
        self.commits = commits
        self.files = files
        self.answer_urls = []
        self.answer_sheets = []
        self.scores = []
        self.ambiguity = False
        self.final_score = 0

    def set_final_scores(self):
        self.final_score = max(self.scores)
