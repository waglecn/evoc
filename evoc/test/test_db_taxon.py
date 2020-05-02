from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class Test_db_taxon:
    def __init__(self):
        self.NCBI_tax_id = 2
        self.name = 'Example'
        self.taxon_id = 1
        self.type_id = 1

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS taxon"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_add_taxon_1(self):
        """adding a taxon with all information"""

        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        type_id = self.type_id

        assert_equal(
            db.add_taxon(
                connection,
                NCBI_tax_id=NCBI_tax_id,
                type_id=type_id
            ), True
        )

    def test_02_add_taxon_2(self):
        """adding another taxon with all information"""

        connection = self.connection
        NCBI_tax_id = 2
        type_id = 1

        assert_equal(
            db.add_taxon(
                connection,
                NCBI_tax_id=NCBI_tax_id,
                type_id=type_id
            ), True
        )

    def test_03_add_taxon_null(self):
        """adding a taxon with no information"""
        connection = self.connection
        assert_equal(db.add_taxon(connection), False)

    def test_04_check_taxon_by_NCBI_id(self):
        """Checking via taxon.NCBI_tax_id"""
        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        results = db.check_taxon(connection, NCBI_tax_id=NCBI_tax_id)
        assert_equal(len(results), 2)
        item = (
            self.taxon_id,
            self.type_id,
            self.NCBI_tax_id
        )
        assert_equal(results[0], item)

    def test_05_check_taxon_by_taxon_id(self):
        """Checking via taxon.taxon_id"""
        connection = self.connection
        taxon_id = self.taxon_id
        results = db.check_taxon(connection, taxon_id=taxon_id)
        assert_not_equal(results, False)
        assert_equal(len(results), 1)
        item = (
            self.taxon_id,
            self.type_id,
            self.NCBI_tax_id
        )
        assert_equal(results[0], item)

    def test_06_check_taxon_by_mixed_1(self):
        """Checking via mixed information (NCBI_tax_id, description)"""
        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        results = db.check_taxon(
            connection,
            NCBI_tax_id=NCBI_tax_id,
        )
        item = (
            self.taxon_id,
            self.type_id,
            self.NCBI_tax_id
        )
        assert_equal(results[0], item)

    def test_07_check_multiple_taxa(self):
        """Checking via NCBI_tax_id (2:Bacteria) for 2 rows"""
        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        results = db.check_taxon(
            connection,
            NCBI_tax_id=NCBI_tax_id
        )
        item = (
            self.taxon_id,
            self.type_id,
            self.NCBI_tax_id
        )
        item2 = (2, 1, 2)
        assert_equal(results[0], item)
        assert_equal(results[1], item2)

    def test_08_add_invalid_taxon(self):
        """Try to add a taxon with invalid data"""
        connection = self.connection
        result = db.add_taxon(
            connection,
            NCBI_tax_id='X',
            type_id=1
        )
        assert_equal(result, False)

        result = db.add_taxon(
            connection,
            NCBI_tax_id=1,
            type_id='X'
        )
        assert_equal(result, False)

        result = db.add_taxon(
            None,
            NCBI_tax_id=self.NCBI_tax_id,
            type_id=self.type_id
        )

    def test_09_check_invalid_params(self):
        """Check using invalid paramters"""
        connection = self.connection
        result = db.check_taxon(connection, taxon_id='X')
        assert_equal(result, False)

        result = db.check_taxon(connection, NCBI_tax_id='X')
        assert_equal(result, False)

        result = db.check_taxon(connection, type_id='X')
        assert_equal(result, False)

    def test_10_check_empty_result(self):
        """Check for correctly returned empty result"""
        connection = self.connection
        result = db.check_taxon(connection, taxon_id=9999999)
        assert_equal(result, [])

        result = db.check_taxon(connection, NCBI_tax_id=999999)
        assert_equal(result, [])

        result = db.check_taxon(connection, type_id=99999999)
        assert_equal(result, [])

    def test_11_check_for_all_result(self):
        """Check for the result without paramters"""
        connection = self.connection
        result = db.check_taxon(connection)
        assert_equal(len(result) > 1, True)
