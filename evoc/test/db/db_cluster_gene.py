from evoc import db
from evoc.logger import logger
from nose.tools import assert_equal
from nose.tools import assert_raises

logger.setLevel(5)


class Test_db_cluster_gene:
    def __init__(self):
        self.cluster_gene_id = 1
        self.cluster_id = 1
        self.gene_id = 1

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(':memory:')
        cls.test_taxon = db.add_taxon(
            cls.connection, type_id=1, NCBI_tax_id=2
        )
        cls.test_gb = db.add_gb(
            cls.connection, cls.test_taxon.taxon_id, prefix='test',
            gb="", loc='/dev/null'
        )
        cls.test_cluster = db.add_cluster(
            cls.connection, type_id=1
        )
        cls.test_gene_1 = db.add_gene(
            cls.connection, uniquename='test1', gb_id=cls.test_gb.gb_id,
            type_id=1, pro_id='1', nuc_id='1',
            location=db.encode_gene_location([1, 1, 5]),
            seq='AAA', start=1, end=3
        )
        cls.test_gene_2 = db.add_gene(
            cls.connection, uniquename='test2', gb_id=cls.test_gb.gb_id,
            type_id=1, pro_id='2', nuc_id='2',
            location=db.encode_gene_location([1, 1, 5]),
            seq='CCC', start=1, end=3
        )
        cls.test_gene_3 = db.add_gene(
            cls.connection, uniquename='test3', gb_id=cls.test_gb.gb_id,
            type_id=1, pro_id='3', nuc_id='3',
            location=db.encode_gene_location([1, 1, 5]),
            seq='DDD', start=1, end=3
        )

    @classmethod
    def teardown_class(cls):
        pass

    def test_01_db_add_cluster_genes(self):
        """Add a cluster_gene entry"""
        connection = self.connection
        cluster_id = self.test_cluster.cluster_id
        result1 = db.add_cluster_gene(
            connection,
            cluster_id=cluster_id,
            gene_id=self.test_gene_1.gene_id
        )
        result2 = db.add_cluster_gene(
            connection,
            cluster_id=cluster_id,
            gene_id=self.test_gene_2.gene_id
        )
        result3 = db.add_cluster_gene(
            connection,
            cluster_id=cluster_id,
            gene_id=self.test_gene_3.gene_id
        )
        assert_equal(True, isinstance(result1, db.ClusterGeneRow))
        assert_equal(True, isinstance(result2, db.ClusterGeneRow))
        assert_equal(True, isinstance(result3, db.ClusterGeneRow))

    def test_02_db_check_cluster_gene_by_cluster_gene_id(self):
        """Check a cluster by cluster_id"""
        connection = self.connection
        result = db.check_cluster_gene(
            connection,
            cluster_gene_id=1
        )
        assert_equal(True, isinstance(result[0], db.ClusterGeneRow))

    def test_03_db_check_cluster_gene_without_selection(self):
        """Check all clusters"""
        connection = self.connection
        result = db.check_cluster_gene(connection)
        assert_equal(len(result), 3)

    def test_04_db_add_invalid_cluster_gene(self):
        """add an invalid cluster_gene entry"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_cluster_gene, connection,
            gene_id=1,
            cluster_id='X'
        )
        assert_raises(
            SystemExit,
            db.add_cluster_gene, connection,
            gene_id=1,
            cluster_id=None
        )
        assert_raises(
            SystemExit,
            db.add_cluster_gene, connection,
            gene_id='X',
            cluster_id=1
        )
        assert_raises(
            SystemExit,
            db.add_cluster_gene, connection,
            gene_id=None,
            cluster_id=1
        )

    def test_05_db_check_cluster_gene_by_cluster_id(self):
        """Check with cluster_id"""
        connection = self.connection
        cluster_id = self.cluster_id
        result = db.check_cluster_gene(connection, cluster_id=cluster_id)
        assert_equal(len(result), 3)

    def test_06_db_check_invalid(self):
        """Check for a cluster using invalid parameters"""
        connection = self.connection
        result = db.check_cluster_gene(connection, gene_id=300)
        assert_equal(result, [])

        result = db.check_cluster_gene(connection, cluster_id=300)
        assert_equal(result, [])

    def test_07_check_invalid_connection(self):
        """Try supplying invalid connection"""
        assert_raises(
            SystemExit,
            db.add_cluster_gene,
            None,
            gene_id=3, cluster_id=1
        )
        assert_raises(
            SystemExit,
            db.add_cluster_gene,
            'X',
            gene_id=3, cluster_id=1
        )

        assert_raises(
            SystemExit,
            db.check_cluster_gene,
            None,
            cluster_id=1
        )
        assert_raises(
            SystemExit,
            db.check_cluster_gene,
            'X',
            cluster_id=1
        )

    def test_08_add_nonexistant_type_cluster(self):
        """Try violoating foreign key constraint"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_cluster_gene,
            connection,
            gene_id=300,
            cluster_id=1
        )
        assert_raises(
            SystemExit,
            db.add_cluster_gene,
            connection,
            gene_id=1,
            cluster_id=300
        )
