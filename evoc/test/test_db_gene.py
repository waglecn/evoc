from evoc import db
from evoc import utils
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class Test_db_gene:
    def __init__(self):
        self.gene_id = 1
        self.uniquename = 'ThisIsAUniqueName'
        self.gb_id = 1
        self.type_id = 1
        self.pro_id = 'proaccession.1'
        self.nuc_id = 'nucaccession.1'
        self.start = 10
        self.end = 100
        self.seq = 'ACHRRDSPLKT'
        self.location = utils.encode_gene_location([(1, 1, 5)])

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS gene"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_db_add_gene(self):
        """Add a gene"""
        connection = self.connection
        uniquename = self.uniquename
        gb_id = self.gb_id
        type_id = self.type_id
        pro_id = self.pro_id
        nuc_id = self.nuc_id
        location = self.location
        start = self.start
        end = self.end
        seq = self.seq

        result = db.add_gene(
            connection,
            uniquename=uniquename,
            type_id=type_id,
            gb_id=gb_id,
            pro_id=pro_id,
            nuc_id=nuc_id,
            location=location,
            seq=seq,
            start=start,
            end=end
        )
        assert_equal(result, True)

    def test_02_db_check_gene_gene_id(self):
        """Check for a gene by gene_id"""
        connection = self.connection
        gene_id = self.gene_id
        uniquename = self.uniquename
        gb_id = self.gb_id
        type_id = self.type_id
        pro_id = self.pro_id
        nuc_id = self.nuc_id
        location = self.location
        start = self.start
        end = self.end
        seq = self.seq
        result = db.check_gene(connection)
        assert_not_equal(result, False)
        item = (
            gene_id,
            uniquename,
            gb_id,
            type_id,
            pro_id,
            nuc_id,
            location,
            seq,
            start,
            end
        )
        assert_equal(result[0], item)

    def test_03_db_check_gene_without_where(self):
        """Check for all genes"""
        connection = self.connection
        result = db.check_gene(connection)
        assert_equal(len(result), 1)

    def test_04_db_check_gene_with_param(self):
        """Check for a gene with only a single parameter"""
        connection = self.connection
        result = db.check_gene(connection, gene_id=self.gene_id)
        assert_equal(len(result), 1)

        result = db.check_gene(connection, pro_id=self.pro_id)
        assert_equal(len(result), 1)

        result = db.check_gene(connection, nuc_id=self.nuc_id)
        assert_equal(len(result), 1)

        result = db.check_gene(connection, start=self.start)
        assert_equal(len(result), 1)

        result = db.check_gene(connection, end=self.end)
        assert_equal(len(result), 1)

        result = db.check_gene(connection, uniquename=self.uniquename)
        assert_equal(len(result), 1)

    def test_05_db_check_gene_by_gb_id(self):
        """Check for a set of genes by gb_id"""
        connection = self.connection
        result = db.add_gene(
            connection,
            uniquename='ThisIsAlsoAUniqueName',
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

        result = db.check_gene(connection, gb_id=self.gb_id)
        assert_equal(len(result), 2)

    def test_06_add_inavlid_gene(self):
        """Try to add an invalid gene"""
        connection = self.connection
        result = db.add_gene(connection, type_id='X')
        assert_equal(result, False)

        result = db.add_gene(connection, gb_id='X')
        assert_equal(result, False)

        result = db.add_gene(connection, start='X')
        assert_equal(result, False)

        result = db.add_gene(connection, end='X')
        assert_equal(result, False)

    def test_06_check_inavlid_gene(self):
        """Check for an invalid gene"""
        connection = self.connection
        result = db.check_gene(connection, gene_id='X')
        assert_equal(result, False)

        result = db.check_gene(connection, type_id='X')
        assert_equal(result, False)

        result = db.check_gene(connection, gb_id='X')
        assert_equal(result, False)

        result = db.check_gene(connection, start='X')
        assert_equal(result, False)

        result = db.check_gene(connection, end='X')
        assert_equal(result, False)

    def test_07_check_empty_gene(self):
        """Check for empty result"""
        connection = self.connection

        result = db.check_gene(connection, gene_id=99999999)
        assert_equal(result, [])

        result = db.check_gene(connection, type_id=99999999)
        assert_equal(result, [])

        result = db.check_gene(connection, gb_id=9999999)
        assert_equal(result, [])

        result = db.check_gene(connection, start=9999999)
        assert_equal(result, [])

        result = db.check_gene(connection, end=9999999)
        assert_equal(result, [])
