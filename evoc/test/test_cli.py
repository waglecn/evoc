import sys
import os
from evoc import cli
from evoc import __main__

from nose.tools import assert_raises
from nose.tools import assert_equal
from unittest import mock

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Test_clis:
    test_path = os.path.dirname(__file__)

    test_tree_input = os.path.join(test_path, 'test.stree.tree')
    test_gtree = os.path.join(test_path, 'test.gtree.tree')
    test_ultrametric_tree = os.path.join(test_path, 'test.um.stree')
    test_tree_output = 'sprime.tree'

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        # cls.connection = db.init_db(cls.dbname)
        pass

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        pass
        # cls.connection.close()
        try:
            os.remove(cls.test_tree_output)
        except Exception:
            pass

    def test_01_test_main(self):
        """Check the entry point for exception"""
        # reassign stderr
        sys.argv = sys.argv[0]

        original_stderr = sys.stderr
        sys.stderr = StringIO()

        # execute the test
        with assert_raises(SystemExit):
            __main__.main()
        # print(sys.stderr.read())

        # # recover original stdout
        sys.stderr = original_stderr

    def test_02_test_entry(self):
        """Testing entry point"""
        sys.argv = sys.argv[0]
        original_stderr = sys.stderr
        sys.stderr = StringIO()

        with mock.patch.object(__main__, '__name__', '__main__'):
            with assert_raises(SystemExit):
                __main__.init()

        sys.stderr = original_stderr

    def test_03_test_cli_subdivide(self):
        """make sure that the dispatch function gets called"""

        output = (
            r"\n"
            r"              /I1/I2/-4\n"
            r"           /-|\n"
            r"          |  |   /I0/-3\n"
            r"          |   \1|\n"
            r"\n"
            r"-pseudo_root    |   /-2\n"
            r"          |      \1|\n"
            r"          |         \-1\n"
            r"          |\n"
            r"           \-1/-1/-1/--1"
        )

        original_stdout = sys.stdout
        sys.stdout = StringIO()
        cli.cli_setup(
            inargs=['subdivide', self.test_tree_input]
        )
        result = sys.stdout.getvalue()
        sys.stdout = original_stdout

        result = result.split('\n')[1:]
        for l in result:
            assert_equal(l in output, True)

        cli.cli_setup(
            inargs=[
                'subdivide',
                self.test_tree_input,
                '-o',
                self.test_tree_output
            ]
        )
        assert_equal(os.path.exists(self.test_tree_output), True)

    def test_04_test_recon(self):
        """Check do recon"""
        import unittest
        import ete3

        try:
            stree = ete3.Tree(self.test_tree_input)
            stree.convert_to_ultrametric(tree_length=100.0)
            stree.write(format=1, outfile=self.test_ultrametric_tree)
        except Exception as e:
            print('skipping: {0}'.format(str(e)))
            unittest.skip('Could not write ultrametric tree')

        cli.cli_setup(
            inargs=[
                'rec',
                '-s', self.test_ultrametric_tree,    # species tree file
                '-g', self.test_gtree,   # gene tree file
                '-o', self.test_path,    # output dir
                '--suffix', 'testing'   # file suffix
            ]
        )
