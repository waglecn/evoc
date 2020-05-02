from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class Test_db_molecule:
    def __init__(self):
        self.molecule_id = 1
        self.type_id = 1
        self.cluster_id = 1

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS molecule"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_add_molecule(self):
        """Add a molecule"""
        connection = self.connection
        type_id = self.type_id
        cluster_id = self.cluster_id
        result = db.add_molecule(
            connection,
            type_id=type_id,
            cluster_id=cluster_id,
        )
        assert_equal(result, True)

    def test_02_check_moecule_by_id(self):
        """Check molecule by id"""
        connection = self.connection

        molecule_id = self.molecule_id
        type_id = self.type_id
        cluster_id = self.cluster_id

        result = db.check_molecule(
            connection,
            molecule_id=molecule_id
        )
        item = (molecule_id, type_id, cluster_id)
        assert_equal(item, result[0])

    def test_03_check_all_molecules(self):
        """Check for all molecules"""
        connection = self.connection
        result = db.check_molecule(connection)
        assert_not_equal(result, False)
        assert_equal(len(result), 1)

    def test_04_add_invalid_molecule(self):
        """try to add an invalid molecule type"""
        connection = self.connection
        result = db.add_molecule(
            connection, type_id='X', cluster_id=1
        )
        assert_equal(result, False)

        result = db.add_molecule(
            connection, type_id=1, cluster_id='X'
        )
        assert_equal(result, False)

    def test_05_check_molecule_by_cluster(self):
        """check for the molecules entered by cluster"""
        connection = self.connection
        result_1 = db.check_molecule(connection, type_id=1)
        result_2 = db.check_molecule(connection, cluster_id=1)
        assert_equal(result_1, result_2)

        result = db.check_molecule(connection, molecule_id=999999)
        assert_equal(result, [])
        result = db.check_molecule(connection, cluster_id=999999)
        assert_equal(result, [])
        result = db.check_molecule(connection, type_id=999999)
        assert_equal(result, [])

    def test_06_check_invalid_molecule(self):
        """test for checking an invalid molecule"""
        connection = self.connection
        result = db.check_molecule(connection, type_id='X')
        assert_equal(result, False)
        result = db.check_molecule(connection, molecule_id='X')
        assert_equal(result, False)
        result = db.check_molecule(connection, cluster_id='X')
        assert_equal(result, False)
