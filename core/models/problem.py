import glob
import os
from zipfile import ZipFile

from core.ejudge.serve_internal import EjudgeContestCfg
from core.models.base import db, UNIQUE_IDENTITY_SIZE
from core.utils.run import read_file_unknown_encoding


class Problem(db.Model):
    __tablename__ = 'problem'
    id = db.Column(db.Integer, primary_key=True)
    problem_identity = db.Column(db.String(UNIQUE_IDENTITY_SIZE), nullable=False)

    ejudge_contest_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=False)
    ejudge_problem_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=False)  # id in contest

    def get_test(self, test_num, size=255):
        conf = EjudgeContestCfg(number=self.ejudge_contest_id)
        prob = conf.getProblem(self.problem_id)

        test_file_name = (prob.tests_dir + prob.test_pat) % int(test_num)
        if os.path.exists(test_file_name):
            res = read_file_unknown_encoding(test_file_name, size)
        else:
            res = test_file_name
        return res

    def get_test_size(self, test_num):
        conf = EjudgeContestCfg(number=self.ejudge_contest_id)
        prob = conf.getProblem(self.problem_id)

        test_file_name = (prob.tests_dir + prob.test_pat) % int(test_num)
        return os.stat(test_file_name).st_size

    def get_corr(self, test_num, size=255):
        conf = EjudgeContestCfg(number=self.ejudge_contest_id)
        prob = conf.getProblem(self.problem_id)

        corr_file_name = (prob.tests_dir + prob.corr_pat) % int(test_num)
        if os.path.exists(corr_file_name):
            res = read_file_unknown_encoding(corr_file_name, size)
        else:
            res = corr_file_name
        return res

    def get_test_full(self, test_num, size=255):
        """
        Возвращает словарь с полной информацией о тесте
        """
        test = {}
        if self.get_test_size(int(test_num)) <= 255:
            test["input"] = self.get_test(int(test_num), size=size)
            test["big_input"] = False
        else:
            test["input"] = self.get_test(int(test_num), size=size) + "...\n"
            test["big_input"] = True

        if self.get_corr_size(int(test_num)) <= 255:
            test["corr"] = self.get_corr(int(test_num), size=size)
            test["big_corr"] = False
        else:
            test["corr"] = self.get_corr(int(test_num), size=size) + "...\n"
            test["big_corr"] = True
        return test

    def get_corr_size(self, test_num):
        conf = EjudgeContestCfg(number = self.ejudge_contest_id)
        prob = conf.getProblem(self.problem_id)

        corr_file_name = (prob.tests_dir + prob.corr_pat) % int(test_num)
        return os.stat(corr_file_name).st_size

    def get_checker(self):
        conf = EjudgeContestCfg(number = self.ejudge_contest_id)
        prob = conf.getProblem(self.problem_id)

        # generate dir with checker
        if conf.advanced_layout:
            checker_dir = os.path.join(conf.contest_path, "problems", prob.internal_name)
        else:
            checker_dir = os.path.join(conf.contest_path, "checkers")

        # trying to find checker
        find_res = glob.glob(os.path.join(checker_dir, "check_{0}.*".format(prob.internal_name)))
        check_src = None
        checker_ext = None
        if find_res:
            check_src = open(find_res[0], "r").read()
            checker_ext = os.path.splitext(find_res[0])[1]

        # if checker not found then try polygon package
        downloads_dir = os.path.join(conf.contest_path, "download")
        if check_src is None and os.path.exists(downloads_dir):
            download_archive_mask = "{0}-*$linux.zip".format(prob.internal_name)
            find_archive_result = glob.glob(os.path.join(downloads_dir, download_archive_mask))
            download_archive_path = find_archive_result[0] if find_archive_result else None
            archive = None
            if download_archive_path is not None:
                archive = ZipFile(download_archive_path)
            if archive is not None:
                member_path = None
                for file in archive.namelist():
                    if file.startswith("check."):
                        member_path = file
                        break
                try:
                    check_src = archive.open(member_path).read()
                    checker_ext = os.path.splitext(member_path)[1]
                except KeyError:
                    check_src = None

        if check_src is None:
            check_src = "checker not found"

        return check_src, checker_ext

    def generate_samples_json(self, force_update=False):
        if self.sample_tests != '':
            if not self.sample_tests_json:
                self.sample_tests_json = {}
            for test in self.sample_tests.split(','):
                if not force_update and test in self.sample_tests_json:
                    continue

                test_input = self.get_test(test, 4096)
                test_correct = self.get_corr(test, 4096)

                self.sample_tests_json[test] = {
                    'input': test_input,
                    'correct': test_correct,
                }
