from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.plugins.skip import SkipTest


@SkipTest
class Test_db_gb:
    def __init__(self):
        self.gb_id = 1
        self.gb_filename = './tests/test.gb'
        self.nuc_id = 'DQ018711'
        self.taxon_id = 1
        self.prefix = 'prefix'
        self.gb = ''

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

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
        nuc_id = self.nuc_id
        nuc_gi = self.nuc_gi
        taxon_id = self.taxon_id
        prefix = self.prefix
        gb = self.gb

        result = db.add_gb(
            connection,
            nuc_id=nuc_id,
            nuc_gi=nuc_gi,
            taxon_id=taxon_id,
            prefix=prefix,
            gb=gb
        )
        assert_equal(result, True)

    def test_02_db_check_gb_by_gb_id(self):
        """Check a gb by gb_id"""
        connection = self.connection
        gb_id = self.gb_id
        nuc_id = self.nuc_id
        nuc_gi = self.nuc_gi
        taxon_id = self.taxon_id
        prefix = self.prefix
        gb = self.gb

        result = db.check_gb(connection, gb_id=gb_id)
        item = (gb_id, nuc_id, nuc_gi, taxon_id, prefix, gb)
        assert_equal(item, result[0])

    def test_03_db_check_gb_without_where(self):
        """Check for all gb rows"""
        connection = self.connection
        result = db.check_gb(connection)
        assert_equal(len(result), 1)

    def test_04_db_add_empty_gb(self):
        """Try making empty add gb"""
        connection = self.connection
        result = db.add_gb(connection)
        assert_equal(result, False)

    def test_05_db_check_gb_by_parts(self):
        """Check for gb with different paramters"""
        connection = self.connection
        result = db.check_gb(
            connection,
            nuc_id=self.nuc_id
        )
        assert_equal(len(result), True)

        result = db.check_gb(
            connection,
            nuc_gi=self.nuc_gi
        )
        assert_equal(len(result), True)

        result = db.check_gb(
            connection,
            prefix=self.prefix
        )
        assert_equal(len(result), True)

        result = db.check_gb(
            connection,
            gb=self.gb
        )
        assert_equal(len(result), True)

    def test_06_check_empty_gb_result(self):
        """Check for returning and empty result"""
        connection = self.connection
        result = db.check_gb(
            connection,
            gb_id=100
        )
        assert_equal(result, [])

    def test_07_add_invalid(self):
        """try adding a gb with invalid data"""
        connection = self.connection
        result = db.add_gb(
            connection,
            nuc_id='acc',
            nuc_gi='X',
            taxon_id=1,
            gb=self.gb
        )
        assert_equal(result, False)

        result = db.add_gb(
            connection,
            nuc_id='acc',
            nuc_gi=1,
            taxon_id='X',
            gb=self.gb
        )
        assert_equal(result, False)

    def test_08_check_invalid_gb(self):
        """Check for a gb with an invalid gb_id"""
        connection = self.connection
        result = db.check_gb(connection, gb_id='X')
        assert_equal(result, False)

        result = db.check_gb(connection, gb_id=9999999)
        assert_equal(result, [])
