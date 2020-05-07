from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_raises

from evoc.logger import logger

logger.setLevel(5)


class Test_db_gb:
    def __init__(self):
        self.gb_id = 1
        self.gb_filename = './tests/test.gb'
        self.prefix = 'prefix'
        self.gb = ''

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')
        cls.test_taxon = db.add_taxon(cls.connection, type_id=1, NCBI_tax_id=2)

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS gb"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_db_add_gb(self):
        """Add a gb"""
        connection = self.connection
        taxon_id = self.test_taxon.taxon_id
        prefix = self.prefix
        gb = self.gb
        loc = self.gb_filename

        result = db.add_gb(
            connection,
            taxon_id=taxon_id,
            prefix=prefix,
            gb=gb,
            loc=loc
        )
        assert_equal(True, isinstance(result, db.GbRow))

    def test_02_db_check_gb_by_gb_id(self):
        """Check a gb by gb_id"""
        connection = self.connection

        taxon_id = self.test_taxon.taxon_id
        prefix = self.prefix
        gb = self.gb
        loc = self.gb_filename

        result = db.check_gb(connection, gb_id=1)[0]
        item = db.GbRow(result.gb_id, taxon_id, prefix, loc, gb)
        assert_equal(item, result)

    def test_03_db_check_gb_without_where(self):
        """Check for all gb rows"""
        connection = self.connection
        result = db.check_gb(connection)
        assert_equal(len(result), 1)

    def test_04_db_add_empty_gb(self):
        """Try making empty add gb"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_gb,
            connection
        )

    def test_05_db_check_gb_by_parts(self):
        """Check for gb with different paramters"""
        connection = self.connection

        result = db.check_gb(
            connection,
            prefix=self.prefix
        )
        assert_equal(True, isinstance(result[0], db.GbRow))

        result = db.check_gb(
            connection,
            gb=self.gb
        )
        assert_equal(True, isinstance(result[0], db.GbRow))

    def test_06_check_empty_gb_result(self):
        """Check for returning an empty result"""
        connection = self.connection
        result = db.check_gb(
            connection,
            gb_id=100
        )
        assert_equal(result, [])

    def test_07_add_invalid(self):
        """Try adding a gb with invalid parameters"""
        connection = self.connection

        assert_raises(
            SystemExit,
            db.add_gb,
            connection,
            taxon_id=1000,
            gb=self.gb
        )

        assert_raises(
            SystemExit,
            db.add_gb,
            connection,
            taxon_id='X',
            gb=self.gb
        )

    def test_08_check_invalid_gb(self):
        """Check for a gb with an invalid gb_id"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.check_gb,
            connection,
            gb_id='X'
        )

    def test_09_check_invalid_connection(self):
        """Check for passing an invalid connection"""
        assert_raises(
            SystemExit,
            db.add_gb,
            None,
            taxon_id=self.test_taxon.taxon_id,
            prefix=self.prefix,
            gb=self.gb,
            loc=self.gb_filename
        )

        assert_raises(
            SystemExit,
            db.add_gb,
            'X',
            taxon_id=self.test_taxon.taxon_id,
            prefix=self.prefix,
            gb=self.gb,
            loc=self.gb_filename
        )

        assert_raises(
            SystemExit,
            db.check_gb,
            None
        )
