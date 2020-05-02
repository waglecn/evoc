import os
from evoc import db
from nose.tools import assert_equal


class Test_db:
    dbname = 'testdb.sqlite3'
    dbname_backup = 'testdb.bak'
    dbname_new = 'testdb.new'

    def __init__(self):
        pass

    @classmethod
    def teardown_class(cls):
        """ Remove tempdb file"""
        os.remove(cls.dbname)
        os.remove(cls.dbname_backup)
        os.remove(cls.dbname_new)

    def test_01_init_db(self):
        """Creating test db"""
        try:
            db.init_db(self.dbname)
        except Exception:
            assert_equal(True, False)

    def test_02_backup_db(self):
        """backing up a test db"""
        assert_equal(db.backup_db(self.dbname, self.dbname_backup), True)

    def test_03_restore_backup_db(self):
        """load a db backup"""
        assert_equal(
            db.load_backup(self.dbname_backup, self.dbname_new),
            True
        )

        # then actually open it
        db.init_db(self.dbname_new)

    def test_04_restore_bad_file(self):
        """load a non-existent db backup"""
        assert_equal(
            db.load_backup(
                "doesnoexistfile",
                self.dbname_new
            ), False
        )
