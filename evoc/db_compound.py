def compound_init():
    """init statement for compounds"""
    compound_init_statement = """
        CREATE TABLE IF NOT EXISTS compound(
            compound_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER NOT NULL,
            cluster_id INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
            FOREIGN KEY (cluster_id) REFERENCES cluster(cluster_id)
        )
    """
    return compound_init_statement


def add_compound(
    connection,
    type_id=None,
    cluster_id=None
):
    cur = connection.cursor()

    fields = []
    values = []
    where = []

    try:
        if type_id is not None:
            fields.append('type_id')
            int(type_id)
            where.append(type_id)
        if cluster_id is not None:
            fields.append('cluster_id')
            int(cluster_id)
            where.append(cluster_id)

        assert len(where) == len(fields)
        assert len(where) > 0
        for x in range(len(fields)):
            values.append('?')
        values = ','.join(values)
        fields = ','.join(fields)
        where = tuple(where)
        cmd = """
            INSERT INTO compound (""" + fields + """)
            VALUES (""" + values + """)
        """
        cur.execute(cmd, where)

        return True
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def check_compound(
    connection,
    compound_id=None,
    type_id=None,
    cluster_id=None
):
    cur = connection.cursor()

    fields = []
    where = []

    try:
        if compound_id is not None:
            where.append('compound_id = ?')
            int(compound_id)
            fields.append(compound_id)
        if type_id is not None:
            where.append('type_id = ?')
            int(type_id)
            fields.append(type_id)
        if cluster_id is not None:
            where.append('cluster_id = ?')
            int(cluster_id)
            fields.append(cluster_id)

        assert(len(fields) == len(where))

        cmd = """
            SELECT
                compound_id,
                type_id,
                cluster_id
            FROM molecule
        """

        if len(fields) > 0:
            fields = tuple(fields)
            where = ' AND '.join(where)
            cmd += " WHERE " + where
            results = cur.execute(cmd, fields).fetchall()
        else:
            results = cur.execute(cmd).fetchall()
        return results
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False
