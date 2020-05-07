import os
from evoc import db
from evoc.logger import logger
from nose.tools import assert_equal, assert_raises, assert_not_equal

logger.setLevel(5)


class Test_db:
    dbname = 'testdb.sqlite3'
    dbname_backup = 'testdb.bak'
    dbname_new = 'testdb.new'

    def __init__(self):
        pass

    @classmethod
    def teardown_class(cls):
        """ Remove tempdb file"""
        try:
            os.remove(cls.dbname)
            os.remove(cls.dbname_backup)
            os.remove(cls.dbname_new)
        except FileNotFoundError:
            pass

    def test_01_init_db(self):
        """Creating test db"""
        db.init_db(self.dbname)

    def test_02_backup_db(self):
        """Backing up a test db"""
        db.dump_backup(self.dbname, self.dbname_backup)

    def test_03_restore_backup_db(self):
        """Load a db backup"""
        db.load_backup(self.dbname_backup, self.dbname_new)

        # then actually open it without error
        db.init_db(self.dbname_new)

    def test_04_restore_bad_file(self):
        """Try to load a non-existent db backup"""
        assert_raises(
            FileNotFoundError,
            db.load_backup,
            "doesnoexistfile",
            self.dbname_new
        )

    def test_05_gene_location(self):
        """Encoding a good location"""
        location = [0, 0, 100]
        good_result = db.encode_gene_location(location)
        assert_not_equal(good_result, False)

    def test_06_gene_location(self):
        """Encoding bad location"""
        null_location = None
        assert_raises(SystemExit, db.encode_gene_location, null_location)

    def test_07_gene_location(self):
        """Decoding good location"""
        location = [0, 0, 100]
        good_result = db.encode_gene_location(location)
        decoded = db.decode_gene_location(good_result)
        assert_equal(decoded, location)

    def test_08_gene_location(self):
        """Decoding bad location"""
        assert_raises(SystemExit, db.decode_gene_location, 'None')
