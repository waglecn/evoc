def domain_init():
    domain = """
        CREATE TABLE IF NOT EXISTS domain(
            domain_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            source_gene_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES types(type_id)
            FOREIGN KEY (source_gene_id) REFERENCES gene(gene_id)
        )
    """
    return domain


def add_domain(
    connection,
    source_gene_id=None,
    type_id=None,
    start=None,
    end=None
):
    cur = connection.cursor()

    fields = []
    values = []
    where = []

    if source_gene_id is not None:
        fields.append('source_gene_id')
        where.append(source_gene_id)
        try:
            int(source_gene_id)
        except Exception:
            return False
    if type_id is not None:
        fields.append('type_id')
        where.append(type_id)
        try:
            int(type_id)
        except Exception:
            return False
    if start is not None:
        fields.append('start')
        where.append(start)
        try:
            int(start)
        except Exception:
            return False
    if end is not None:
        fields.append('end')
        where.append(end)
        try:
            int(end)
        except Exception:
            return False

    try:
        assert(len(fields) == len(where))
        assert(len(fields) > 0)
        for x in range(len(fields)):
            values.append('?')
        values = ','.join(values)
        fields = ','.join(fields)
        where = tuple(where)

        cmd = """INSERT INTO domain (""" + fields + """)
            VALUES (""" + values + """)
        """
        cur.execute(cmd, where)
        return True
    except Exception as e:
        print(e)

    return False


def check_domain(
    connection,
    domain_id=None,
    source_gene_id=None,
    type_id=None,
    start=None,
    end=None,
):
    """
    returns:
        domain_id, source_gene_id, type_id, descroption, start, end
    """
    cur = connection.cursor()

    fields = []
    where = []

    if domain_id is not None:
        where.append('domain_id = ?')
        fields.append(domain_id)
    if start is not None:
        where.append('start = ?')
        fields.append(start)
    if end is not None:
        where.append('end = ?')
        fields.append(end)
    if source_gene_id is not None:
        where.append('source_gene_id = ?')
        fields.append(source_gene_id)
    if type_id is not None:
        where.append('type_id = ?')
        fields.append(type_id)
    assert(len(fields) == len(where))

    cmd = """
        SELECT
            domain_id,
            source_gene_id,
            type_id,
            start,
            end
        FROM domain
    """

    if len(fields) > 0:
        where = ' AND '.join(where)
        fields = tuple(fields)
        cmd += " WHERE " + where
        result = cur.execute(cmd, fields).fetchall()
    else:
        result = cur.execute(cmd).fetchall()

    if len(result) > 0:
        return result
    else:
        return []
