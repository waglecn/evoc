import os
from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_raises
from evoc.logger import logger

logger.setLevel(5)


class Test_db_taxon:
    def __init__(self):
        self.NCBI_tax_id = 2
        self.taxon_id = 1
        self.type_id = 1

    @classmethod
    def setup_class(cls):
        cls.dbname = './testdb.sqlite3'
        cls.connection = db.init_db(cls.dbname)

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS taxon"
        cls.connection.execute(cmd)
        cls.connection.commit()
        cls.connection.close()
        try:
            os.remove(cls.dbname)
        except OSError:
            pass

    def test_01_add_taxon_1(self):
        """adding a taxon with all information"""

        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        type_id = self.type_id

        result = db.add_taxon(
            connection,
            NCBI_tax_id=NCBI_tax_id,
            type_id=type_id,
        )
        assert_equal(True, isinstance(result, db.TaxonRow))

    def test_02_add_taxon_2(self):
        """adding another taxon with all information"""

        connection = self.connection
        NCBI_tax_id = 2
        type_id = 2

        db.add_taxon(
            connection,
            NCBI_tax_id=NCBI_tax_id,
            type_id=type_id
        )

    def test_03_add_taxon_null(self):
        """Try adding a taxon with no information"""
        connection = self.connection
        assert_raises(SystemExit, db.add_taxon, connection)

    def test_04_check_taxon_by_NCBI_id(self):
        """Checking via taxon.NCBI_tax_id"""
        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        result = db.check_taxon(connection, NCBI_tax_id=NCBI_tax_id)
        assert_equal(len(result), 2)

    def test_05_check_taxon_by_taxon_id(self):
        """Checking via taxon.taxon_id"""
        connection = self.connection
        taxon_id = self.taxon_id
        result = db.check_taxon(connection, taxon_id=taxon_id)
        assert_equal(len(result), 1)

    def test_06_check_multiple_taxa(self):
        """Checking via NCBI_tax_id (2:Bacteria) for 2 rows"""
        connection = self.connection
        NCBI_tax_id = self.NCBI_tax_id
        result = db.check_taxon(
            connection,
            NCBI_tax_id=NCBI_tax_id
        )
        assert_equal(len(result), 2)

    def test_07_add_invalid_taxon(self):
        """Try add a taxon with invalid data"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_taxon,
            connection,
            NCBI_tax_id='X',
            type_id=1
        )

        assert_raises(
            SystemExit,
            db.add_taxon,
            connection,
            NCBI_tax_id=1,
            type_id='X'
        )

        assert_raises(
            SystemExit,
            db.add_taxon,
            None,
            NCBI_tax_id=self.NCBI_tax_id,
            type_id=self.type_id
        )

    def test_08_check_invalid_params(self):
        """Check using invalid paramters"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.check_taxon,
            connection,
            taxon_id='X'
        )

        assert_raises(
            SystemExit,
            db.check_taxon,
            connection,
            NCBI_tax_id='X'
        )

        assert_raises(
            SystemExit,
            db.check_taxon,
            connection,
            type_id='X'
        )

    def test_09_check_empty_result(self):
        """Check for correctly returned empty result"""
        connection = self.connection
        result = db.check_taxon(connection, taxon_id=9999999)
        assert_equal(result, [])

        result = db.check_taxon(connection, NCBI_tax_id=999999)
        assert_equal(result, [])

        result = db.check_taxon(connection, type_id=99999999)
        assert_equal(result, [])

    def test_10_add_nonexistant_taxon_type(self):
        """Try to add a taxon with a non-existant type_id"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_taxon,
            connection,
            type_id=99999,
            NCBI_tax_id=2
        )
