from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_raises


class Test_db_cluster:
    def __init__(self):
        self.cluster_id = 1
        self.type_id = 1

    @classmethod
    def setup_class(cls):
        cls.test_db_file = ':memory:'
        cls.connection = db.init_db(cls.test_db_file)

    @classmethod
    def teardown_class(cls):
        pass

    def test_01_db_add_cluster(self):
        "Add a cluster"
        connection = self.connection
        type_id = self.type_id
        result = db.add_cluster(connection, type_id=type_id)
        assert_equal(True, isinstance(result, db.ClusterRow))

    def test_02_db_check_cluster_by_cluster_id(self):
        """Check a cluster by cluster_id"""
        connection = self.connection
        cluster_id = self.cluster_id
        type_id = self.type_id
        result = db.check_cluster(connection, cluster_id=cluster_id)
        item = db.ClusterRow(cluster_id, type_id)
        assert_equal(result[0], item)

    def test_03_db_check_cluster_without_selection(self):
        """Check all clusters"""
        connection = self.connection
        result = db.check_cluster(connection)
        assert_equal(len(result), 1)

    def test_04_db_add_invalid_cluster(self):
        """Try adding an invalid cluster"""
        connection = self.connection

        assert_raises(
            SystemExit,
            db.add_cluster,
            connection,
            type_id='X'
        )

        assert_raises(
            SystemExit,
            db.add_cluster,
            connection,
            type_id=99999
        )

    def test_05_db_check_invalid_cluster_id_int(self):
        """Check for an invalid cluster_id int"""
        connection = self.connection

        result = db.check_cluster(
            connection,
            cluster_id=9999999
        )
        assert_equal(result, [])

    def test_06_db_check_invalid_cluster_id_string(self):
        """Check for an invalid cluster_id string"""
        connection = self.connection

        assert_raises(
            SystemExit,
            db.check_cluster,
            connection,
            cluster_id='X'
        )

    def test_07_db_check_invalid_cluster_type_id_int(self):
        """Try adding with an invalid connection"""
        assert_raises(
            SystemExit,
            db.add_cluster,
            None,
            type_id=1
        )
        assert_raises(
            SystemExit,
            db.add_cluster,
            1,
            type_id=1
        )

    def test_08_db_check_invalid_cluster_type_id_string(self):
        """Try checking with an invalid connection"""
        assert_raises(
            SystemExit,
            db.check_cluster,
            None,
            cluster_id=1
        )
        assert_raises(
            SystemExit,
            db.check_cluster,
            1,
            cluster_id=1
        )
