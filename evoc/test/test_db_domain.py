from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class Test_db_domain:
    def __init__(self):
        self.domain_id = 1
        self.type_id = 1
        self.source_gene_id = 100
        self.start = 1
        self.end = 100

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS domain"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_add_domain(self):
        """Add a domain"""
        connection = self.connection
        source_gene_id = self.source_gene_id
        type_id = self.type_id
        start = self.start
        end = self.end
        result = db.add_domain(
            connection,
            source_gene_id=source_gene_id,
            type_id=type_id,
            start=start,
            end=end
        )
        assert_equal(result, True)

    def test_02_check_domain_by_id(self):
        """Check domain by domain_id"""
        connection = self.connection
        domain_id = self.domain_id
        source_gene_id = self.source_gene_id
        type_id = self.type_id
        start = self.start
        end = self.end
        result = db.check_domain(connection, domain_id=domain_id)
        item = (domain_id, source_gene_id, type_id, start, end)
        assert_equal(result[0], item)

    def test_03_check_all_domains(self):
        """Check for all domains"""
        connection = self.connection
        result = db.check_domain(connection)
        assert_not_equal(result, False)
        assert_equal(len(result), 1)

    def test_04_add_invalid_domain(self):
        """try to add an invalid domain"""
        connection = self.connection
        result = db.add_domain(
            connection,
            type_id='X'
        )
        assert_equal(result, False)

        result = db.add_domain(
            connection,
            type_id='X',
            source_gene_id=self.source_gene_id,
            start=1,
            end=100
        )
        assert_equal(result, False)

        result = db.add_domain(
            connection,
            source_gene_id='X'
        )
        assert_equal(result, False)

        result = db.add_domain(
            connection,
            start='X'
        )
        assert_equal(result, False)

        result = db.add_domain(
            connection,
            end='X'
        )
        assert_equal(result, False)

        result = db.add_domain(
            connection,
        )
        assert_equal(result, False)

    def test_04_check_domain_by_coords(self):
        """Check domain by start and end"""
        connection = self.connection
        result = db.check_domain(
            connection,
            domain_id=1,
            start=1
        )
        assert_equal(len(result), 1)

        result = db.check_domain(
            connection,
            domain_id=1,
            end=100
        )
        assert_equal(len(result), 1)
