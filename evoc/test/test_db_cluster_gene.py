from evoc import db
from nose.tools import assert_equal


class Test_db_cluster_gene:
    def __init__(self):
        self.cluster_gene_id = 1
        self.cluster_id = 1
        self.gene_id = 1

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS cluster_gene"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_db_add_cluster_gene(self):
        """Add a cluster_gene entry"""
        connection = self.connection
        cluster_id = self.cluster_id
        gene_id = self.gene_id
        result = db.add_cluster_gene(
            connection,
            cluster_id=cluster_id,
            gene_id=gene_id
        )
        assert_equal(result, True)

    def test_02_db_check_cluster_gene_by_cluster_gene_id(self):
        """Check a cluster by cluster_id"""
        connection = self.connection
        cluster_gene_id = self.cluster_gene_id
        cluster_id = self.cluster_id
        gene_id = self.gene_id
        result = db.check_cluster_gene(
            connection,
            cluster_gene_id=cluster_gene_id
        )
        item = (cluster_gene_id, cluster_id, gene_id)
        assert_equal(result[0], item)

    def test_03_db_check_cluster_gene_without_selection(self):
        """Check all clusters"""
        connection = self.connection
        result = db.check_cluster_gene(connection)
        assert_equal(len(result), 1)

    def test_04_db_add_invalid_cluster_gene(self):
        """add an invalid cluster_gene entry"""
        connection = self.connection
        result = db.add_cluster_gene(
            connection,
            gene_id=1,
            cluster_id='X'
        )
        assert_equal(result, False)

        result = db.add_cluster_gene(
            connection,
            gene_id='X',
            cluster_id=1
        )
        assert_equal(result, False)

    def test_05_db_check_cluster_gene_by_cluster_id(self):
        """Check for a cluster by cluster_id"""
        connection = self.connection
        cluster_gene_id = self.cluster_gene_id
        cluster_id = self.cluster_id
        gene_id = self.gene_id

        item = (cluster_gene_id, cluster_id, gene_id)

        result = db.check_cluster_gene(connection, cluster_id=1)
        assert_equal(result[0], item)

        result = db.check_cluster_gene(connection, gene_id=1)
        assert_equal(result[0], item)

    def test_05_db_check_invalid(self):
        """Check for a cluster using invalid parameters"""
        connection = self.connection
        result = db.check_cluster_gene(connection, gene_id=300)
        assert_equal(result, [])

        result = db.check_cluster_gene(connection, gene_id='X')
        assert_equal(result, False)

        connection = None
        result = db.check_cluster_gene(connection)
        assert_equal(result, False)
