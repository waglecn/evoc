def gb_init():
    """gb table init string"""

    gb = """
        CREATE TABLE IF NOT EXISTS gb(
            gb_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            prefix TEXT NOT NULL,
            taxon_id INTEGER NOT NULL,
            loc TEXT UNIQUE NOT NULL,
            gb TEXT,
            FOREIGN KEY (taxon_id) REFERENCES taxa(taxon_id)
        )
    """
    return gb


def add_gb(
    connection,
    taxon_id=None,
    prefix=None,
    gb=None,
    loc=None
):
    cur = connection.cursor()

    insert = []
    values = []
    where = []

    try:
        if taxon_id is not None:
            insert.append('taxon_id')
            values.append('?')
            int(taxon_id)
            where.append(taxon_id)
        if prefix is not None:
            insert.append('prefix')
            values.append('?')
            where.append(prefix)
        if loc is not None:
            insert.append('loc')
            values.append('?')
            where.append(loc)
        if gb is not None:
            insert.append('gb')
            values.append('?')
            where.append(gb)

        assert(len(values) == len(where) == len(insert))
        if len(values) > 0:
            insert = ', '.join(insert)
            values = ', '.join(values)
            where = tuple(where)

            cmd = """
                INSERT INTO gb (""" + insert + """) VALUES (""" + values + """)
            """
            cur.execute(cmd, where)
            return cur.lastrowid
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False

    return False


def check_gb(
    connection,
    gb_id=None,
    taxon_id=None,
    prefix=None,
    loc=None,
    gb=None
):
    """
    Returns:
        [gb_id, accession, nuc_gi, taxon_id, prefix, loc, gb] or False
    """

    cur = connection.cursor()

    values = []
    where = []
    try:
        if gb_id is not None:
            where.append('gb_id = ?')
            values.append(gb_id)
            int(gb_id)
        if taxon_id is not None:
            where.append('taxon_id = ?')
            values.append(taxon_id)
            int(taxon_id)
        if prefix is not None:
            where.append('prefix = ?')
            values.append(prefix)
        if loc is not None:
            where.append('loc = ?')
            values.append(loc)
        if gb is not None:
            where.append('gb = ?')
            values.append(gb)

        assert(len(values) == len(where))
        if len(values) == 0:
            cmd = """
                SELECT
                    gb_id,
                    taxon_id,
                    prefix,
                    loc,
                    gb
                FROM gb
            """
            results = cur.execute(cmd).fetchall()
            return results
        else:
            where = ' AND '.join(where)
            values = tuple(values)
            cmd = """
                SELECT
                    gb_id,
                    taxon_id,
                    prefix,
                    loc,
                    gb
                FROM gb
            WHERE """ + where
            results = cur.execute(cmd, values).fetchall()
            if len(results) > 0:
                return results
            else:
                return []
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False
