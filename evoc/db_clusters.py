def cluster_init():
    """cluster table init string"""

    clusters = """
        CREATE TABLE IF NOT EXISTS cluster(
            cluster_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER UNIQUE NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
        )
    """
    return clusters


def add_cluster(
    connection,
    type_id=None
):
    """Add single cluster to cluster table

    Retur: Boolean success/failure
    """
    cur = connection.cursor()

    insert = []
    values = []
    where = []

    if type_id is not None:
        insert.append('type_id')
        values.append('?')
        where.append(type_id)

    assert(len(values) == len(where) == len(insert))
    if len(values) > 0:
        insert = ', '.join(insert)
        values = ', '.join(values)
        where = tuple(where)

        cmd = """
            INSERT INTO cluster (""" + insert + """) VALUES (""" + values + """)
        """
        try:
            for i in where:
                int(i)
            cur.execute(cmd, where)
            return True
        except Exception as e:
            print('Caught: {0}'.format(e))

    return False


def check_cluster(
    connection,
    cluster_id=None,
    type_id=None
):
    """"Check for a cluster entry by id or type id. If none provided, return
        all cluster entries

    Return: result list, or []
    """

    cur = connection.cursor()

    values = []
    where = []

    if cluster_id is not None:
        where.append('cluster_id = ?')
        values.append(cluster_id)
    if type_id is not None:
        where.append('type_id = ?')
        values.append(type_id)

    assert(len(values) == len(where))
    try:
        for i in values:
            int(i)
        if len(values) == 0:
            cmd = """
                SELECT
                    cluster_id,
                    type_id
                FROM cluster
            """
            results = cur.execute(cmd).fetchall()
            return results
        else:
            where = ' AND '.join(where)
            values = tuple(values)
            cmd = """
                SELECT
                    cluster_id,
                    type_id
                FROM cluster
            WHERE """ + where
            results = cur.execute(cmd, values).fetchall()
            if len(results) > 0:
                return results
            else:
                return []

    except Exception as e:
        print('Caught: {0}'.format(e))

    return []
