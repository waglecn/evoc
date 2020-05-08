from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_raises


class Test_db_molecule:
    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(':memory:')
        cls.test_cluster = db.add_cluster(cls.connection, type_id=1)

    @classmethod
    def teardown_class(cls):
        pass

    def test_01_add_compound(self):
        """Add a molecule"""
        connection = self.connection
        result = db.add_compound(
            connection,
            type_id=1,
            cluster_id=self.test_cluster.cluster_id,
        )
        result = db.add_compound(
            connection,
            type_id=1,
            cluster_id=self.test_cluster.cluster_id,
        )
        assert_equal(True, isinstance(result, db.CompoundRow))

    def test_02_check_moecule_by_id(self):
        """Check compound by id"""
        connection = self.connection
        result = db.check_compound(
            connection,
            compound_id=1
        )
        assert_equal(True, isinstance(result[0], db.CompoundRow))

    def test_03_check_all_compounds(self):
        """Check for all molecules"""
        connection = self.connection
        result = db.check_compound(connection)
        assert_equal(len(result), 2)

    def test_04_add_invalid_compound(self):
        """try to add an invalid compound type"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_compound,
            connection, type_id='X', cluster_id=1
        )
        assert_raises(
            SystemExit,
            db.add_compound,
            connection, type_id=99999, cluster_id=1
        )

        assert_raises(
            SystemExit,
            db.add_compound,
            connection, type_id=1, cluster_id='X'
        )
        assert_raises(
            SystemExit,
            db.add_compound,
            connection, type_id=1, cluster_id=20
        )

    def test_05_add_empty_compound(self):
        """Try adding an empty compound"""
        connection = self.connection
        assert_raises(SystemExit, db.add_compound, connection)

    def test_06_check_compound_by_cluster(self):
        """Check for the compounds entered by cluster"""
        connection = self.connection
        result1 = db.check_compound(connection, type_id=1)
        assert_equal(len(result1), 2)

        result2 = db.check_compound(connection, cluster_id=1)
        assert_equal(len(result2), 2)

    def test_07_check_nonexistant_query(self):
        """Check for a compound with a non-existant query"""
        connection = self.connection
        result1 = db.check_compound(connection, type_id=9999)
        assert_equal(result1, [])

        result2 = db.check_compound(connection, cluster_id=9999)
        assert_equal(result2, [])

    def test_08_check_bad_connection(self):
        """Try add and check with bad connection"""
        assert_raises(
            SystemExit, db.add_compound, None, type_id=1, cluster_id=1
        )
        assert_raises(
            SystemExit, db.check_compound, None, type_id=1, cluster_id=1
        )

        assert_raises(
            SystemExit, db.add_compound, 'X', type_id=1, cluster_id=1
        )
        assert_raises(
            SystemExit, db.check_compound, 'X', type_id=1, cluster_id=1
        )
