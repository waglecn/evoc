def molecules_init():
    """init statement for molecules"""
    molecules_init_statement = """
        CREATE TABLE IF NOT EXISTS molecule(
            molecule_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER NOT NULL,
            cluster_id INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
            FOREIGN KEY (cluster_id) REFERENCES cluster(cluster_id)
        )
    """
    return molecules_init_statement


def add_molecule(
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
            INSERT INTO molecule (""" + fields + """)
            VALUES (""" + values + """)
        """
        cur.execute(cmd, where)

        return True
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def check_molecule(
    connection,
    molecule_id=None,
    type_id=None,
    cluster_id=None
):
    cur = connection.cursor()

    fields = []
    where = []

    try:
        if molecule_id is not None:
            where.append('molecule_id = ?')
            int(molecule_id)
            fields.append(molecule_id)
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
                molecule_id,
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
