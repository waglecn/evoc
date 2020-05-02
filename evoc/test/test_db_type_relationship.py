from evoc import db
from evoc import utils
from nose.tools import assert_equal
from nose.tools import assert_not_equal


class Test_db_type_relationship:
    def __init__(self):
        import os
        test_dir = os.path.dirname(__file__)
        self.relationship_file = os.path.join(test_dir, 'test_types.tsv')
        self.types, self.relationships = utils.read_relationship_tsv(
            self.relationship_file
        )
        self.relationship_id = 1

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db('./testdb.sqlite3')

    @classmethod
    def teardown_class(cls):
        cmd = "DROP TABLE IF EXISTS type_relationship"
        cur = cls.connection.cursor()
        cur.execute(cmd)
        cls.connection.commit()
        cls.connection.close()
        import os
        try:
            os.remove('./testdb.sqlite3')
        except Exception:
            pass

    def test_01_load_relationships(self):
        """Given a set of types and relationships, load into db"""
        connection = self.connection
        types = self.types
        relationships = self.relationships
        for item in types:
            if not (
                db.check_type(connection, name=item[0], description=item[1])
            ):
                db.add_type(connection, name=item[0], description=item[1])

            assert_not_equal(
                db.check_type(connection, name=item[0], description=item[1]),
                False
            )

        result = db.load_relationships(connection, types, relationships)
        assert_equal(result, True)

    def test_02_check_default_relationship(self):
        """Check for the example relationship"""
        connection = self.connection

        child = self.relationships[0][1]
        relationship = self.relationships[0][2]
        parent = self.relationships[0][0]

        all_types = db.check_type(connection)
        for item in all_types:
            if item[1] == child:
                child_type = item[0]
            if item[1] == parent:
                parent_type = item[0]
            if item[1] == relationship:
                rel_type = item[0]
        result = db.check_relationship(connection)
        # (rel_id, object_id, subject_id, rel_id) (1, 2, 3, 4)

        result = db.check_relationship(
            connection,
            object_id=parent_type,
            subject_id=child_type,
            type_id=rel_type
        )
        assert_not_equal(result, False)

    def test_03_add_single_relationship(self):
        """Add a single relationship"""
        connection = self.connection

        new_parent_name = "Mother"
        new_parent_description = "A Mother"

        new_child_name = "Baby"
        new_child_description = "A Baby"

        try:
            db.add_type(
                connection,
                name=new_parent_name,
                description=new_parent_description
            )
            db.add_type(
                connection,
                name=new_child_name,
                description=new_child_description
            )
            db.add_type(
                connection,
                name='child_of',
                description='another relationship'
            )
        except Exception as e:
            print(e)
            assert_equal(True, False)

        all_types = db.check_type(connection)
        for item in all_types:
            if item[1] == 'Mother':
                parent_id = item[0]
            if item[1] == 'Baby':
                child_id = item[0]
            if item[1] == 'child_of':
                type_id = item[0]

        result = db.add_relationship(
            connection,
            object_id=parent_id,
            subject_id=child_id,
            type_id=type_id
        )
        assert_equal(result, True)

    def test_04_check_relationship_by_relationship_id(self):
        """Check for default relationship by relationship_id"""
        connection = self.connection
        rel_id = self.relationship_id
        result = db.check_relationship(connection, relationship_id=rel_id)
        assert_not_equal(result, False)
        # (relationship_id = 0, Parent, Child, is_a)
        assert_equal(result[0], (1, 2, 3, 4))
  

    def test_05_add_invalid_relationship(self):
        """Try to add an invalid relationship"""
        connection = self.connection
        result = db.add_relationship(
            connection,
            subject_id='X',
            object_id=1,
            type_id=1
        )
        assert_equal(result, False)

        result = db.add_relationship(
            connection,
            subject_id=1,
            object_id='X',
            type_id=1
        )
        assert_equal(result, False)

        result = db.add_relationship(
            connection,
            subject_id=1,
            object_id=1,
            type_id='X'
        )
        assert_equal(result, False)

        result = db.add_relationship(
            None,
            subject_id=1,
            object_id=1,
            type_id=1
        )
        assert_equal(result, False)

        result = db.add_relationship(connection)
        assert_equal(result, False)


    def test_06_check_invalid_rel(self):
        """Check for a relationship with invalid parameters"""
        connection = self.connection

        child = self.relationships[0][1]
        relationship = self.relationships[0][2]
        parent = self.relationships[0][0]

        result = db.check_relationship(
            connection,
            subject_id='X',
            object_id=parent,
            type_id=relationship
        )
        assert_equal(result, False)

        result = db.check_relationship(
            connection,
            subject_id=child,
            object_id='X',
            type_id=relationship
        )
        assert_equal(result, False)

        result = db.check_relationship(
            connection,
            subject_id=child,
            object_id=parent,
            type_id='X'
        )
        assert_equal(result, False)

        result = db.check_relationship(
            None,
            subject_id=child,
            object_id=parent,
            type_id=relationship
        )
        assert_equal(result, False)

    def test_07_add_invalid_rels(self):
        """try to add bulk add relationships with invalid paramters"""
        result = db.load_relationships(None, self.types, self.relationships)
        assert_equal(result, False)