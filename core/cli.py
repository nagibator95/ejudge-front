import os
import sys
import unittest

import click
from flask.cli import with_appcontext
from teamcity.unittestpy import TeamcityTestRunner

THIS_FILE = os.path.abspath(os.path.dirname(__file__))
TESTS_DIR = os.path.join(THIS_FILE, 'tests/')


@click.command('test')
@click.option('--teamcity', is_flag=True, default=False)
@click.option('--verbosity', '-v', default=2)
@with_appcontext
def test(teamcity, verbosity):
    loader = unittest.TestLoader()
    tests = loader.discover(TESTS_DIR, pattern='test*.py')

    if teamcity:
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner(verbosity=verbosity)

    result = runner.run(tests)

    exit_code = 1
    if result.wasSuccessful():
        exit_code = 0

    sys.exit(exit_code)
