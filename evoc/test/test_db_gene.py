from evoc import db
from evoc.logger import logger
from nose.tools import assert_equal
from nose.tools import assert_raises

logger.setLevel(5)


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
        self.location = db.encode_gene_location([(1, 1, 5)])

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(':memory:')
        cls.test_type = db.check_type(cls.connection, type_id=1)
        cls.test_taxon = db.add_taxon(
            cls.connection, type_id=1, NCBI_tax_id=2
        )
        cls.test_gb = db.add_gb(
            cls.connection, taxon_id=cls.test_taxon.taxon_id,
            prefix='test', gb='', loc='/dev/null'
        )

    @classmethod
    def teardown_class(cls):
        pass

    def test_01_db_add_gene(self):
        """Add a gene"""
        connection = self.connection
        uniquename = self.uniquename
        gb_id = self.test_gb.gb_id
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
        assert_equal(True, isinstance(result, db.GeneRow))

    def test_02_db_check_gene_gene_id(self):
        """Check for a gene by gene_id"""
        connection = self.connection
        result = db.check_gene(connection, gene_id=1)
        assert_equal(result[0].type_id, self.type_id)
        assert_equal(result[0].seq, self.seq)

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

        result = db.check_gene(connection, seq=self.seq)
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
            seq=self.seq * 2,
            start=self.start,
            end=self.end
        )

        result = db.check_gene(connection, gb_id=self.gb_id)
        assert_equal(len(result), 2)
        names = [result[0].uniquename, result[1].uniquename]
        assert_equal(True, 'ThisIsAlsoAUniqueName' in names)
        assert_equal(True, self.uniquename in names)

    def test_06_add_inavlid_gene_type_id(self):
        """Try to add with invalid type_id"""
        connection = self.connection
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename,
            type_id='X',
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename,
            type_id=999999,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

    def test_07_add_inavlid_gene_uniquename(self):
        """Check for an invalid uniquename"""
        connection = self.connection
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename,  # duplicate
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

    def test_08_check_add_empty_gene(self):
        """Check for adding empty"""
        connection = self.connection
        assert_raises(SystemExit, db.add_gene, connection)

    def test_09_add_invalid_gene_gb_id(self):
        """Try adding with an invalid gb_id"""
        connection = self.connection
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id='X',
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=99999,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

    def test_10_add_invalid_gene_gb_id(self):
        """Try adding with no location"""
        connection = self.connection
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=None,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

    def test_11_add_invalid_gene_start_end(self):
        """Try adding with an invalid gb_id"""
        connection = self.connection
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start='X',
            end=self.end
        )
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=None,
            end=self.end
        )

        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end='X'
        )
        assert_raises(
            SystemExit, db.add_gene, connection,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=None
        )

    def test_12_add_invalid_connection(self):
        """Try adding with connection"""
        assert_raises(
            SystemExit, db.add_gene,
            None,
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

        assert_raises(
            SystemExit, db.add_gene,
            'X',
            uniquename=self.uniquename * 2,
            type_id=self.type_id,
            gb_id=self.gb_id,
            pro_id=self.pro_id,
            nuc_id=self.nuc_id,
            location=self.location,
            seq=self.seq,
            start=self.start,
            end=self.end
        )

    def test_13_check_with_invalid_params(self):
        """Try checking with invalid params"""
        connection = self.connection
        assert_raises(SystemExit, db.check_gene, None)
        assert_raises(SystemExit, db.check_gene, 'X')

        assert_raises(SystemExit, db.check_gene, connection, gene_id='X')
        assert_equal([], db.check_gene(connection, gene_id=99999))

        assert_equal([], db.check_gene(connection, uniquename=99999))
        assert_raises(SystemExit, db.check_gene, connection, gb_id='X')
        assert_raises(SystemExit, db.check_gene, connection, type_id='X')
        assert_raises(SystemExit, db.check_gene, connection, start='X')
        assert_raises(SystemExit, db.check_gene, connection, end='X')
