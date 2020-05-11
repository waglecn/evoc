from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_raises
from evoc.logger import logger

logger.setLevel(5)


class Test_db_domain:
    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(':memory:')
        cls.test_taxon = db.add_taxon(cls.connection, type_id=1, NCBI_tax_id=1)
        cls.test_gb = db.add_gb(
            cls.connection, taxon_id=cls.test_taxon.taxon_id, prefix='prefix',
            gb='', loc="/dev/null"
        )
        cls.test_gene = db.add_gene(
            cls.connection, uniquename='test_gene_1', gb_id=cls.test_gb.gb_id,
            type_id=1, pro_id='1.1', nuc_id='1.1',
            location=db.encode_gene_location([1, 1, 9]),
            seq='AAA', start=1, end=5
        )

    @classmethod
    def teardown_class(cls):
        pass

    def test_01_add_domain(self):
        """Add a domain"""
        connection = self.connection
        result = db.add_domain(
            connection,
            source_gene_id=self.test_gene.gene_id,
            type_id=1,
            start=1,
            end=3
        )
        assert_equal(True, isinstance(result, db.DomainRow))
        result = db.add_domain(
            connection,
            source_gene_id=self.test_gene.gene_id,
            type_id=1,
            start=2,
            end=3
        )
        assert_equal(True, isinstance(result, db.DomainRow))

    def test_02_check_domain_by_id(self):
        """Check domain by domain_id"""
        connection = self.connection
        result1 = db.check_domain(connection, domain_id=1)
        result2 = db.check_domain(connection, domain_id=2)
        assert_equal(True, isinstance(result1[0], db.DomainRow))
        assert_equal(True, isinstance(result2[0], db.DomainRow))

    def test_03_check_all_domains(self):
        """Check for all domains"""
        connection = self.connection
        result = db.check_domain(connection)
        assert_equal(len(result), 2)

    def test_04_add_invalid_domain(self):
        """Try to add domain with invalid type"""
        connection = self.connection

        assert_raises(
            SystemExit,
            db.add_domain,
            connection,
            type_id='X',
            source_gene_id=self.test_gene.gene_id,
            start=1,
            end=1
        )

        assert_raises(
            SystemExit,
            db.add_domain,
            connection,
            type_id=100,
            source_gene_id=self.test_gene.gene_id,
            start=1,
            end=1
        )

    def test_05_add_invalid_domain_gene(self):
        """Try to add domain with invalid source"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_domain,
            connection,
            type_id=1,
            source_gene_id='X',
            start=1, end=1
        )
        assert_raises(
            SystemExit,
            db.add_domain,
            connection,
            type_id=1,
            source_gene_id=1000,
            start=1, end=1
        )

    def test_06_add_invalid_domain_coords(self):
        """Try to add domain with invalid source"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_domain,
            connection,
            type_id=1,
            source_gene_id=self.test_gene.gene_id,
            start='X', end=1
        )
        assert_raises(
            SystemExit,
            db.add_domain,
            connection,
            type_id=1,
            source_gene_id=self.test_gene.gene_id,
            start=1, end='X'
        )

    def test_07_add_empty_domain(self):
        """Try to add empty domain"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_domain,
            connection
        )

    def test_07_add_domain_invalid_connection(self):
        """Try adding domain with invalid connection"""
        assert_raises(
            SystemExit, db.add_domain, None,
            type_id=1, source_gene_id=self.test_gene.gene_id,
            start=1, end=3
        )
        assert_raises(
            SystemExit, db.add_domain, 'X',
            type_id=1, source_gene_id=self.test_gene.gene_id,
            start=1, end=3
        )

    def test_08_check_domain_result(self):
        """Try checking for domain with various information"""
        connection = self.connection
        result = db.check_domain(connection, domain_id=1)
        assert_equal(len(result), 1)
        assert_equal(True, isinstance(result[0], db.DomainRow))

        result = db.check_domain(connection, source_gene_id=1)
        assert_equal(len(result), 2)
        assert_equal(True, isinstance(result[0], db.DomainRow))

        result = db.check_domain(connection, type_id=1)
        assert_equal(len(result), 2)
        assert_equal(True, isinstance(result[0], db.DomainRow))

        result = db.check_domain(connection, domain_id=100)
        assert_equal(result, [])

        result = db.check_domain(connection, source_gene_id=100)
        assert_equal(result, [])

        result = db.check_domain(connection, type_id=100000)
        assert_equal(result, [])

    def test_09_check_domain_invalid(self):
        """Try checking domain with invalid query"""
        connection = self.connection

        assert_raises(
            SystemExit,
            db.check_domain,
            connection,
            domain_id='X'
        )

        assert_raises(
            SystemExit,
            db.check_domain,
            connection,
            source_gene_id='X'
        )

        assert_raises(
            SystemExit,
            db.check_domain,
            connection,
            type_id='X'
        )

    def test_11_check_domain_invalid_connection(self):
        """Try to check domain with an invalid connection"""
        assert_raises(SystemExit, db.check_domain, None)
        assert_raises(SystemExit, db.check_domain, 'X')
