import sqlite3
from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises

class Test_db_type:
    def __init__(self):
        self.description = 'an example type'
        self.name = 'example'
        self.type_id = 1
        self.test_bulk = [
            ('add_1', 'bulk add 1',),
            ('add_2', 'bulk add 2',),
            ('add_3', 'bulk add 3',),
        ]
        self.test_bulk_result = [
            (2, 'add_1', 'bulk add 1'),
            (3, 'add_2', 'bulk add 2'),
            (4, 'add_3', 'bulk add 3'),
        ]

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
        result = db.add_type(connection, name=name, description=description)
        assert_equal(result, True)

    def test_02_add_null_type(self):
        """Add an example type without description"""
        connection = self.connection
        result = db.add_type(connection)
        assert_equal(result, False)

    def test_03_bulk_add_types(self):
        """test bulk adding of types"""
        connection = self.connection
        test_bulk = self.test_bulk
        result = db.bulk_add_types(connection, test_bulk)
        assert_equal(result, True)

    def test_04_type_by_type_id(self):
        """check an added type by type_id"""
        connection = self.connection
        type_id = self.type_id
        description = self.description
        name = self.name
        item = (type_id, name, description)
        result = db.check_type(connection, type_id=type_id)
        assert_equal(result[0], item)

    def test_05_type_by_description(self):
        """check an added type by description"""
        connection = self.connection
        type_id = self.type_id
        description = self.description
        name = self.name
        item = (type_id, name, description)
        result = db.check_type(connection, description=description)
        assert_equal(result[0], item)

    def test_06_type_multiple_result(self):
        """check the return of multiple results without description"""
        connection = self.connection
        result = db.check_type(connection)
        assert_not_equal(result, False)
        if result is not False:
            assert_equal(len(result), 4)

    def test_07_missing_type(self):
        """check that a a missing type returns correct False"""
        connection = self.connection
        result = db.check_type(connection, name='King Kong')
        assert_equal(result, [])

    def test_08_add_duplicate_type(self):
        """Try adding a duplicate type"""
        connection = self.connection
        result = db.add_type(
            connection,
            name='is_a',
            description='an axiomatic relationship'
        )
        assert_equal(True, result)
        assert_raises(
            sqlite3.IntegrityError,
            db.add_type,
            connection,
            name='is_a', description='another axiomatic relationship'
        )

    def test_09_check_invalid_params(self):
        """Check with invalid parameters"""
        connection = self.connection
        result = db.check_type(connection, type_id='X')
        assert_equal(result, None)

        connection = None
        result = db.check_type(connection, type_id=1)
        assert_equal(result, None)

    def test_10_bulk_add_unpaired_types(self):
        """Check bulk add with unpaired type"""
        connection = self.connection
        types = [
            ('A', 'A'),
            ('B'),
            ('C', 'C')
        ]
        result = db.bulk_add_types(connection, types)
        assert_equal(result, False)
