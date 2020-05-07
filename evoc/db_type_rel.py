import sqlite3
from collections import namedtuple
from evoc.logger import logger

TypeRow = namedtuple('TypeRow', 'type_id, name, description')
RelRow = namedtuple(
    'RelRow', 'relationship_id, object_id, subject_id, type_id'
)


def type_init():
    """
    types table init string

    arguments:

    return:
        string type table SQL

    """

    TYPE_SQL = """
        CREATE TABLE IF NOT EXISTS type(
            type_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL
        )
    """
    return TYPE_SQL


def rel_init():
    """
    relationships table init string

    arguments:

    return:
        string type_relationships table SQL

    """

    REL_SQL = """
        CREATE TABLE IF NOT EXISTS type_relationship(
            relationship_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            subject_id INTEGER NOT NULL,
            object_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            UNIQUE(subject_id, object_id, type_id),
            FOREIGN KEY (subject_id) REFERENCES type(type_id),
            FOREIGN KEY (object_id) REFERENCES type(type_id),
            FOREIGN KEY (type_id) REFERENCES type(type_id)
        )
    """
    return REL_SQL


def add_type(connection, name=None, description=None):
    """
    Add a single type to the type table

    arguments:
        connection: db connectio object
        name: string (None)
        description: string (None)

    return:
        Boolean success/failure

    """
    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    cmd = """
        INSERT INTO type (name, description) VALUES(?, ?)
    """

    try:
        assert name is not None
        assert description is not None
        connection.execute(cmd, (name, description))
    except sqlite3.IntegrityError:
        logger.debug(
            'Duplicate add type (name) {0} (description) {1}'.format(
                name, description
            )
        )
    except AssertionError as e:
        logger.error('NoneType caught: {0}'.format(str(e)))
        raise SystemExit('Exiting.')

    return TypeRow(*connection.execute(
        "SELECT * FROM type WHERE name = ?", (name,)
    ).fetchone())


def check_type(connection, type_id=None, name=None, description=None):
    """
        Check for a type by id, name or description, return matches
        If no criteria specified, return all types

    arguments:
        connection: db connection object
        type_id: integer (None)
        name: string (None)
        description: string (None)

    return:
        [(type_id, name, description)]
            list of matching type rows
        False on failure
    """
    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    fields = []
    values = []
    try:
        if name is not None:
            fields.append('name = ?')
            values.append(name)
        if description is not None:
            fields.append('description = ?')
            values.append(description)
        if type_id is not None:
            fields.append('type_id = ?')
            int(type_id)
            values.append(type_id)

        fields = ' AND '.join(fields)
        values = tuple(values)

        if len(fields) > 0:
            cmd = """SELECT type_id, name, description
                FROM type
                WHERE """ + fields
            results = connection.execute(cmd, values)
        else:
            cmd = """SELECT type_id, name, description FROM type"""
            results = connection.execute(cmd)
        return [TypeRow(*r) for r in results]
    except ValueError as e:
        logger.exception('Invalid input: {0}'.format(str(e)))
        raise SystemExit


def add_relationship(
    connection, object_id=None, subject_id=None, type_id=None
):
    """
    Add a single relationship to the type_relatioship table

    arguments:
        connection: db object connection
        object_id: integer (None)
        subject_id: integer (None)
        type_id: integer (None)

    return:
        Boolean success/failure

    """

    cmd = """INSERT INTO type_relationship (object_id, subject_id, type_id)
        VALUES (?, ?, ?)
    """

    try:
        int(object_id)
        int(subject_id)
        int(type_id)
        assert object_id is not None
        assert subject_id is not None
        assert type_id is not None
        connection.execute(cmd, (object_id, subject_id, type_id))
        return True
    except Exception as e:
        logger.exception('Caught: {0} adding sub {1}, type {2}, ob {3}'.format(
            str(e), subject_id, type_id, object_id)
        )
        return False


def check_relationship(
    connection,
    relationship_id=None,
    object_id=None,
    subject_id=None,
    type_id=None
):
    """
    Check for a relationship by id, or any combination of participating
    types. If not specified, return all relationships.

    connection: db connection object
    relationship_id: integer (None)
    object_id: integer (None)
    subjet_id integer (None)
    type_id: integer (None)

    return:
        [(relationship_id, object_id, subject_id, type_id)]
            list of result rows, may be empty
        False on failure
    """
    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    fields = []
    values = []

    try:
        if relationship_id is not None:
            fields.append('relationship_id = ?')
            values.append(int(relationship_id))
        if object_id is not None:
            fields.append('object_id = ?')
            values.append(int(object_id))
        if subject_id is not None:
            fields.append('subject_id = ?')
            values.append(int(subject_id))
        if type_id is not None:
            fields.append('type_id =?')
            values.append(int(type_id))

        assert(len(fields) == len(values))

        cmd = """SELECT
                relationship_id,
                object_id,
                subject_id,
                type_id
            FROM type_relationship
        """

        fields = " AND ".join(fields)
        values = tuple(values)

        if(len(fields) > 0):
            cmd += " WHERE " + fields
            results = connection.execute(cmd, values)
        else:
            results = connection.execute(cmd)

        return [RelRow(*r) for r in results]
    except Exception as e:
        logger.exception('Caught: {0}'.format(str(e)))
        return False
