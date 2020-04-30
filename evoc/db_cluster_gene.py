def cluster_gene_init():
    """cluster_gene table init string"""

    cluster_gene = """
        CREATE TABLE IF NOT EXISTS cluster_gene(
            cluster_gene_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            cluster_id INTEGER NOT NULL,
            gene_id INTEGER NOT NULL,
            FOREIGN KEY (cluster_id) REFERENCES cluster(cluster_id),
            FOREIGN KEY (gene_id) REFERENCES gene(gene_id)
        )
    """
    return cluster_gene


def add_cluster_gene(connection, cluster_id=None, gene_id=None):
    """Add a single entry to the cluster_gene table"""

    cur = connection.cursor()
    insert = []
    values = []
    where = []

    if cluster_id is not None:
        insert.append('cluster_id')
        values.append('?')
        where.append(cluster_id)
    if gene_id is not None:
        insert.append('gene_id')
        values.append('?')
        where.append(gene_id)

    assert len(values) == len(where) == len(insert)
    if len(values) > 0:
        insert = ', '.join(insert)
        values = ', '.join(values)
        where = tuple(where)

        cmd = """
            INSERT INTO cluster_gene (""" + insert + """) VALUES(""" + values \
            + """)
        """
        try:
            for i in where:
                int(i)

            cur.execute(cmd, where)
            return True
        except Exception as e:
            print(e)

    return False


def check_cluster_gene(
    connection,
    cluster_gene_id=None,
    cluster_id=None,
    gene_id=None
):
    """Check for a single entry in the cluster_gene table by id, gene_id,
        cluster_id. If none provided, will return all entries in the table"""

    values = []
    where = []

    if cluster_gene_id is not None:
        where.append('cluster_gene_id = ?')
        values.append(cluster_gene_id)
    if gene_id is not None:
        where.append('gene_id = ?')
        values.append(gene_id)
    if cluster_id is not None:
        where.append('cluster_id = ?')
        values.append(cluster_id)

    assert(len(values) == len(where))

    try:
        cur = connection.cursor()
        if len(values) == 0:
            cmd = """
                SELECT
                    cluster_gene_id,
                    cluster_id,
                    gene_id
                FROM cluster_gene
            """
            results = cur.execute(cmd).fetchall()
            return results
        else:
            for i in values:
                int(i)
            where = ' AND '.join(where)
            values = tuple(values)
            cmd = """
                SELECT
                    cluster_gene_id,
                    cluster_id,
                    gene_id
                FROM cluster_gene
            WHERE """ + where
            results = cur.execute(cmd, values).fetchall()
            if len(results) > 0:
                return results
            else:
                return []
    except Exception as e:
        print('Caught: {0}'.format(e))

    return False
