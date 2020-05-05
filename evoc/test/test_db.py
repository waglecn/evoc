import os
from evoc import db
from nose.tools import assert_equal, assert_raises


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
        db.init_db(self.dbname)

    def test_02_backup_db(self):
        """backing up a test db"""
        db.dump_backup(self.dbname, self.dbname_backup)

    def test_03_restore_backup_db(self):
        """load a db backup"""
        db.load_backup(self.dbname_backup, self.dbname_new)

        # then actually open it without error
        db.init_db(self.dbname_new)

    def test_04_restore_bad_file(self):
        """try to load a non-existent db backup"""
        assert_raises(
            FileNotFoundError,
            db.load_backup,
            "doesnoexistfile",
            self.dbname_new
        )
