import os
from evoc import db
from evoc.logger import logger
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises

logger.setLevel(5)

try:
    import importlib.resources as importlib_resources
except ImportError:
    # Python <3.7 backported `importlib_resources`
    import importlib_resources


class Test_db_type_relationship:
    def __init__(self):
        with importlib_resources.path('evoc', 'basic_types.tsv') as path:
            self.relationship_file = path
        self.types, self.relationships = db.parse_relationship_tsv(
            self.relationship_file
        )

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')
        cls.test_relationship = db.RelRow(*cls.connection.execute(
            "SELECT relationship_id, subject_id, object_id, type_id "
            "FROM type_relationship WHERE relationship_id = 1"
        ).fetchone())

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS type_relationship"
        cls.connection.execute(cmd)
        cls.connection.commit()
        cls.connection.close()

        try:
            os.remove('./testdb.sqlite3')
        except OSError:
            pass

    def test_01_check_default_relationship(self):
        """Check for the example relationship"""
        connection = self.connection

        all_types = db.check_type(connection)
        for item in all_types:
            if item.name == 'child':
                subject_type = item.type_id
            if item.name == 'parent':
                object_type = item.type_id
            if item.name == 'is_a':
                rel_type = item.type_id
        result = db.check_relationship(
            connection,
            object_id=object_type,
            subject_id=subject_type,
            type_id=rel_type
        )[0]
        assert_not_equal(None, result)
        assert_equal(len(result), 4)

    def test_02_add_single_relationship(self):
        """Add a single relationship"""
        connection = self.connection

        new_parent_name = "Mother"
        new_parent_desc = "A Mother"

        new_child_name = "Baby"
        new_child_desc = "A Baby"

        mother = db.add_type(
            connection, name=new_parent_name, description=new_parent_desc
        )
        baby = db.add_type(
            connection, name=new_child_name, description=new_child_desc
        )
        child_of = db.add_type(
            connection, name='child_of', description='another relationship'
        )

        result = db.add_relationship(
            connection,
            object_id=mother.type_id,
            subject_id=baby.type_id,
            type_id=child_of.type_id
        )
        assert_equal(len(result), 4)

    def test_03_check_relationship_by_relationship_id(self):
        """Check for default relationship by relationship_id"""
        connection = self.connection
        rel_id = self.test_relationship.relationship_id
        result = db.check_relationship(connection, relationship_id=rel_id)[0]
        assert_equal(self.test_relationship, result)

    def test_04_add_invalid_relationship(self):
        """Try to add an invalid relationship"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_relationship,
            connection,
            subject_id='X',
            object_id=1,
            type_id=1
        )
        assert_raises(
            SystemExit,
            db.add_relationship,
            connection,
            subject_id=1,
            object_id='X',
            type_id=1
        )
        assert_raises(
            SystemExit,
            db.add_relationship,
            connection,
            subject_id=1,
            object_id=1,
            type_id='X'
        )
        assert_raises(
            SystemExit,
            db.add_relationship,
            None,
            subject_id=1,
            object_id=1,
            type_id=1
        )
        assert_raises(SystemExit, db.add_relationship, connection)

    def test_05_check_invalid_rel(self):
        """Check for a relationship with invalid parameters"""
        connection = self.connection

        test_rel = db.check_relationship(self.connection, relationship_id=1)[0]

        assert_raises(
            SystemExit,
            db.check_relationship,
            connection,
            subject_id='X',
            object_id=test_rel.object_id,
            type_id=test_rel.type_id
        )

        assert_raises(
            SystemExit,
            db.check_relationship,
            connection,
            subject_id=test_rel.subject_id,
            object_id='X',
            type_id=test_rel.type_id
        )

        assert_raises(
            SystemExit,
            db.check_relationship,
            connection,
            subject_id=test_rel.subject_id,
            object_id=test_rel.object_id,
            type_id='X'
        )

        assert_raises(
            SystemExit,
            db.check_relationship,
            None,
            subject_id=test_rel.subject_id,
            object_id=test_rel.object_id,
            type_id=test_rel.type_id
        )

    def test_06_add_invalid_rels(self):
        """Try to add invalid relationship"""
        connection = self.connection
        assert_raises(
            SystemExit,
            db.add_relationship,
            connection,
            subject_id=999,
            object_id=1000,
            type_id=1001,
        )
