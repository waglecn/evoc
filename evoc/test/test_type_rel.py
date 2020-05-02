import sys
import os

from evoc import utils
from evoc import db
from evoc import type_rel

from nose.tools import assert_equal
from nose.tools import assert_raises


class Test_type_rel:
    dbname = 'testdb.sqlite3'

    mock_cmap = {
        2: {'label': 'parent',
            'color': '0x6F6F6F'},
        3: {'label': 'child',
            'color': '0x6F6F6F'}
    }

    def __init__(self):
        import os
        self.test_dir = os.path.dirname(__file__)
        self.rel_tsv_file = os.path.join(self.test_dir, 'test_types.tsv')
        self.test_gb_file = os.path.join(self.test_dir, 'test.gb')

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(cls.dbname)

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        cls.connection.close()
        import os
        os.remove(cls.dbname)
        os.remove('test.thv')

    def test_01_check_children_invalid(self):
        """Check children of an invalid term"""
        connection = self.connection

        rel_tsv_file = self.rel_tsv_file
        types, relationships = utils.read_relationship_tsv(rel_tsv_file)
        db.load_relationships(connection, types, relationships)

        rel_type = db.check_type(connection, name='is_a')[0]
        rel_id = rel_type[0]

        with assert_raises(SystemExit):
            type_rel.check_children(connection, 99, rel_id, 0, [])

    def test_02_check_children(self):
        """Check children of parent type"""
        connection = self.connection

        parent_type = db.check_type(connection, name='parent')[0]
        parent_id = parent_type[0]

        rel_type = db.check_type(connection, name='is_a')[0]
        rel_id = rel_type[0]

        result = type_rel.check_children(connection, parent_id, rel_id, 0, [])
        assert_equal(len(result), 1)

    def test_03_test_print_types_rels(self):
        """Check printing of types and relationships"""

        # swap stdout
        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [],    # ids
            [],     # parents
            [],     # children
            False,  # graphviz
            [],     # excluded ids
            False   # unjoin
        )

        result = sys.stdout.getvalue()

        # replace stdout
        sys.stdout = original_stdout
        print(result)
        assert_equal(len(result.split('\n')), 7)

    def test_04_test_print_specific_types(self):
        """Check printing types with specific ids"""

        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [2],    # ids
            [],     # parents
            [],     # children
            False,  # graphviz
            None,     # excluded ids
            False   # unjoin
        )

        result = sys.stdout.getvalue()

        # replace stdout
        sys.stdout = original_stdout
        assert_equal(len(result.split('\n')), 3)

    def test_05_test_print_excluded_types(self):
        """Check printing types with excluded ids"""

        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [],    # ids
            [],     # parents
            [],     # children
            False,  # graphviz
            [2, 3],     # excluded ids
            False   # unjoin
        )

        result = sys.stdout.getvalue()

        # replace stdout
        sys.stdout = original_stdout
        assert_equal(len(result.split('\n')), 6)

    def test_06_test_non_root_types(self):
        """Check printing non root types"""

        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [3],    # ids
            [],     # parents
            [],     # children
            False,  # graphviz
            None,     # excluded ids
            False   # unjoin
        )

        result = sys.stdout.getvalue()

        # replace stdout
        sys.stdout = original_stdout
        assert_equal(len(result.split('\n')), 2)

    def test_07_test_unjoined_non_root_types(self):
        """Check printing unjoined non root types"""

        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [2],    # ids
            [],     # parents
            [],     # children
            False,  # graphviz
            None,     # excluded ids
            True   # unjoin
        )

        result = sys.stdout.getvalue()

        # replace stdout
        sys.stdout = original_stdout
        assert_equal(len(result.split('\n')), 2)

    def test_08_test_print_types_graphviz(self):
        """Check graphviz printing of types and relationships"""

        # swap stdout
        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        from unittest import mock
        from evoc import cluster
        with mock.patch.object(cluster, 'cmap', self.mock_cmap):
            type_rel.print_types_rels(
                self.dbname,
                [],    # ids
                [],     # parents
                [],     # children
                True,  # graphviz
                None,     # excluded ids
                False   # unjoin
            )

        sys.stdout.getvalue()

        # replace stdout
        sys.stdout = original_stdout
        assert_equal(os.path.exists('types.png'), True)
        os.remove('types.png')

    def test_09_test_fail_graphviz(self):
        """Try to import missing pygraphviz"""

        # import target, and save original function
        import builtins
        original_import = builtins.__import__

        from unittest import mock

        # define the mock function to raise expected error when needed
        def raiseError(name, *args):
            if name == 'pygraphviz':
                raise ImportError
            else:
                return original_import(name, *args)

        with mock.patch.object(builtins, '__import__', side_effect=raiseError):
            with assert_raises(SystemExit):
                    type_rel.print_types_rels(
                        self.dbname,
                        [],
                        [],
                        [],
                        True,
                        None,
                        False
                    )

    def test_09_test_load_type_thv(self):
        """Test load type thv function"""
        # need default rel_id for is_a
        connection = self.connection
        rel_type = db.check_type(connection, name='is_a')[0]
        rel_id = rel_type[0]

        # swap stdout
        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [],
            [],
            [],
            False,
            None,
            False
        )

        result = sys.stdout.getvalue()
        sys.stdout = original_stdout
        with open('test.thv', 'w') as outh:
            for line in result.split('\n'):
                if line.startswith('(6'):
                    outh.write('\t' + line + '\t' + str(rel_id) + '\n')
                elif line.startswith('(1'):
                    line = line.replace('nothing', 'really nothing')
                    outh.write(line + '\n')
                else:
                    outh.write(line + '\n')

        type_rel.load_type_thv(
            self.dbname,
            'test.thv',
            True,
            True
        )

        result = db.check_type(connection, name='none')
        assert_equal(result[0][2], 'really nothing')

        result = db.check_relationship(connection, subject_id=6)
        assert_equal(result[0], (2, 5, 6, 4))

    def test_10_check_load_type_thv_invalid(self):
        """try load type thv with invalid input"""

        # steal stdout
        from io import StringIO
        stdout = StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout

        type_rel.print_types_rels(
            self.dbname,
            [], [], [], False, None, False
        )

        result = sys.stdout.getvalue()
        # replace stdout
        sys.stdout = original_stdout

        # write incorrect thv file
        with open('test.thv', 'w') as outh:
            for line in result.split('\n'):
                if line.startswith('\t(6'):
                    outh.write(
                        '\t' + line + '\t' + line + '\t' + line + '\n'
                    )
                else:
                    outh.write(line + '\n')

        with assert_raises(SystemExit):
            type_rel.load_type_thv(
                self.dbname,
                'test.thv',
                True,
                True
            )

        with open('test.thv', 'w') as outh:
            for line in result.split('\n'):
                if line.startswith('\t(6'):
                    outh.write(
                        '\t{0}\n'.format('(6, \'none\', \'new\')')
                    )
                else:
                    outh.write(line + '\n')
        with assert_raises(SystemExit):
            type_rel.load_type_thv(
                self.dbname,
                'test.thv',
                True,
                True
            )
