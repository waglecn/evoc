def gene_init():
    gene = """
        CREATE TABLE IF NOT EXISTS gene(
            gene_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            uniquename TEXT UNIQUE NOT NULL,
            gb_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            pro_id TEXT,
            nuc_id TEXT,
            location TEXT NOT NULL,
            seq TEXT,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id),
            FOREIGN KEY (gb_id) REFERENCES gb(gb_id)
        )
    """
    return gene


def add_gene(
    connection,
    gene_id=None,
    uniquename=None,
    gb_id=None,
    type_id=None,
    pro_id=None,
    nuc_id=None,
    location=None,
    seq=None,
    start=None,
    end=None
):
    cur = connection.cursor()

    fields = []
    values = []
    where = []

    try:
        if uniquename is not None:
            fields.append('uniquename')
            where.append(uniquename)
        if gb_id is not None:
            fields.append('gb_id')
            int(gb_id)
            where.append(gb_id)
        if type_id is not None:
            fields.append('type_id')
            int(type_id)
            where.append(type_id)
        if pro_id is not None:
            fields.append('pro_id')
            where.append(pro_id)
        if nuc_id is not None:
            fields.append('nuc_id')
            where.append(nuc_id)
        if location is not None:
            fields.append('location')
            where.append(location)
        if seq is not None:
            fields.append('seq')
            where.append(seq)
        if start is not None:
            fields.append('start')
            int(start)
            where.append(start)
        if end is not None:
            fields.append('end')
            int(end)
            where.append(end)

        assert len(where) == len(fields)
        assert len(where) > 0

        for i in range(len(where)):
            values.append('?')
        fields = ', '.join(fields)
        values = ', '.join(values)
        where = tuple(where)

        cmd = """
            INSERT INTO gene (""" + fields + """) VALUES (""" + values + """)
        """
        cur.execute(cmd, where)
        return True

    except Exception as e:
        print('Caught gene: {0}'.format(
            str(e), gb_id, type_id, uniquename, location)
        )
        return False


def check_gene(
    connection,
    gene_id=None,
    uniquename=None,
    gb_id=None,
    type_id=None,
    pro_id=None,
    nuc_id=None,
    location=None,
    seq=None,
    start=None,
    end=None
):
    """
    Returns:
        gene_id, uniquename, gb_id, type_id,
        pro_id, nuc_id,
        location, seq, start, end

    """

    cur = connection.cursor()

    fields = []
    where = []

    try:
        if gene_id is not None:
            where.append('gene_id = ?')
            int(gene_id)
            fields.append(gene_id)
        if uniquename is not None:
            where.append('uniquename = ?')
            fields.append(uniquename)
        if gb_id is not None:
            where.append('gb_id = ?')
            int(gb_id)
            fields.append(gb_id)
        if type_id is not None:
            where.append('type_id = ?')
            int(type_id)
            fields.append(type_id)
        if pro_id is not None:
            where.append('pro_id = ?')
            fields.append(pro_id)
        if nuc_id is not None:
            where.append('nuc_id = ?')
            fields.append(nuc_id)
        if start is not None:
            where.append('start = ?')
            int(start)
            fields.append(start)
        if end is not None:
            where.append('end = ?')
            int(end)
            fields.append(end)

        assert(len(fields) == len(where))

        if len(fields) == 0:
            cmd = """
                SELECT
                    gene_id,
                    uniquename,
                    gb_id,
                    type_id,
                    pro_id,
                    nuc_id,
                    location,
                    seq,
                    start,
                    end
                FROM gene
            """
            results = cur.execute(cmd).fetchall()
        else:
            where = ' AND '.join(where)
            fields = tuple(fields)
            cmd = """
                SELECT
                    gene_id,
                    uniquename,
                    gb_id,
                    type_id,
                    pro_id,
                    nuc_id,
                    location,
                    seq,
                    start,
                    end
                FROM gene
            WHERE """ + where
            results = cur.execute(cmd, fields).fetchall()
        return results

    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False
