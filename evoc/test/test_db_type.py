from evoc import db
from evoc.logger import logger
from nose.tools import assert_equal
from nose.tools import assert_raises

logger.setLevel(5)


class Test_db_type:
    def __init__(self):
        self.description = 'an example type'
        self.name = 'example'

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS type"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

    def test_01_add_type(self):
        """Add an example type"""
        connection = self.connection
        description = self.description
        name = self.name
        t_result = db.add_type(connection, name=name, description=description)
        self.type_id = t_result.type_id

    def test_02_add_null_type(self):
        """Add an example type without description"""
        connection = self.connection
        assert_raises(SystemExit, db.add_type, connection)

    def test_03_type_by_type_id(self):
        """Check an added type by type_id"""
        item1 = db.check_type(self.connection, name=self.name)[0]
        item2 = db.check_type(self.connection, type_id=item1.type_id)[0]
        assert_equal(item1, item2)

    def test_04_type_by_description(self):
        """check an added type by description"""
        connection = self.connection
        item1 = db.check_type(connection, name=self.name)[0]
        item2 = db.check_type(connection, description=self.description)[0]
        assert_equal(item1, item2)

    def test_05_type_multiple_result(self):
        """check the return of multiple results without description"""
        connection = self.connection
        expected_len = connection.execute(
            """SELECT count(*) FROM type"""
        ).fetchone()[0]
        result = db.check_type(connection)
        assert_equal(len(result), expected_len)

    def test_06_missing_type(self):
        """check that a a missing type returns correct False"""
        connection = self.connection
        result = db.check_type(connection, name='King Kong')
        assert_equal(result, [])

    def test_07_add_duplicate_type(self):
        """Try adding a duplicate type"""
        connection = self.connection
        result1 = db.add_type(
            connection,
            name='a_type',
            description='an axiomatic relationship'
        )
        result2 = db.add_type(
            connection,
            name='a_type',
            description='the same axiomatic relationship'
        )
        assert_equal(result1, result2)

    def test_08_check_invalid_params(self):
        """Check with invalid parameters"""
        connection = self.connection
        assert_raises(SystemExit, db.check_type, connection, type_id='X')

        connection = None
        assert_raises(SystemExit, db.check_type, connection, type_id=1)
