import sqlite3


def types_init():
    """
    types table init string

    arguments:

    return:
        string type table SQL

    """

    types = """
        CREATE TABLE IF NOT EXISTS type(
            type_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL
        )
    """
    return types


def rels_init():
    """
    relationships table init string

    arguments:

    return:
        string type_relationships table SQL

    """

    type_relationships = """
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
    return type_relationships


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

    cmd = """
        INSERT INTO type (name, description) VALUES(?, ?)
    """

    try:
        cur = connection.cursor()
        assert name is not None
        assert description is not None
        cur.execute(cmd, (name, description))
        return True
    except sqlite3.IntegrityError as e:
        # catch not null exception
        print('Caught: {0}'.format(str(e)))
        print(
            'Error adding type (name) {0} (description) {1}'.format(
                name, description
            )
        )
        raise sqlite3.IntegrityError
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


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

        cur = connection.cursor()

        if len(fields) > 0:
            cmd = """SELECT type_id, name, description
                FROM type
                WHERE """ + fields
            results = cur.execute(cmd, values).fetchall()
        else:
            cmd = """SELECT type_id, name, description FROM type"""
            results = cur.execute(cmd).fetchall()

        return results
    except Exception as e:
        print('Caught: {0}'.format(str(e)))


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
        cur = connection.cursor()
        int(object_id)
        int(subject_id)
        int(type_id)
        assert object_id is not None
        assert subject_id is not None
        assert type_id is not None
        cur.execute(cmd, (object_id, subject_id, type_id))
        return True
    except Exception as e:
        print('Caught: {0} adding sub {1}, type {2}, ob {3}'.format(
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

    fields = []
    values = []

    try:
        if relationship_id is not None:
            fields.append('relationship_id = ?')
            values.append(relationship_id)
        if object_id is not None:
            fields.append('object_id = ?')
            values.append(object_id)
        if subject_id is not None:
            fields.append('subject_id = ?')
            values.append(subject_id)
        if type_id is not None:
            fields.append('type_id =?')
            values.append(type_id)

        assert(len(fields) == len(values))

        for i in values:
            int(i)

        cmd = """SELECT
                relationship_id,
                object_id,
                subject_id,
                type_id
            FROM type_relationship
        """

        cur = connection.cursor()
        fields = " AND ".join(fields)
        values = tuple(values)

        if(len(fields) > 0):
            cmd += " WHERE " + fields
            results = cur.execute(cmd, values).fetchall()
        else:
            results = cur.execute(cmd).fetchall()

        return results
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def bulk_add_types(connection, types):
    """
    Bulk add types to type table, not checked for duplicates. This might
    Be a bad idea.

    connection: db connection object
    types: list of ('name', 'description') tuples to be loaded

    return Boolean success/failure
    """

    cur = connection.cursor()

    cmd = """INSERT INTO type (name, description) VALUES(?, ?)"""

    try:
        for pair in types:
            assert len(pair) == 2
        cur.executemany(cmd, types)
        return True
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def load_relationships(connection, types, relationships):
    """
    Add a set of types and relationships. This will not add duplicates.

    arguments:
        types: from utils.read_relationship_tsv
        relationships: from utils.read_relationship_tsv

    return:
        Boolean success/failure
    """

    type_map = {}
    rels_to_add = []

    try:
        base_types = check_type(connection)
        for base in base_types:
            if base[1] not in type_map:
                type_map[base[1]] = base[0]

        for item in types:
            temp = check_type(connection, name=item[0])
            if not temp:
                assert add_type(
                    connection, name=item[0], description=item[1]
                ), 'could not add type'
                temp = check_type(
                    connection, name=item[0], description=item[1]
                )
            type_key = temp[0][1]
            type_id = temp[0][0]
            if type_key not in type_map:
                type_map[type_key] = type_id

        for rel in relationships:
            object_id = type_map[rel[0]]
            subject_id = type_map[rel[1]]
            type_id = type_map[rel[2]]
            new_item = (object_id, subject_id, type_id)
            if (
                new_item not in rels_to_add and
                not check_relationship(
                    connection,
                    object_id=new_item[0],
                    subject_id=new_item[1],
                    type_id=new_item[2]
                )
            ):
                rels_to_add.append(new_item)

        cmd = """
            INSERT INTO type_relationship (object_id, subject_id, type_id)
                VALUES (?, ?, ?)
        """
        cur = connection.cursor()
        cur.executemany(cmd, rels_to_add)
        return True
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False

