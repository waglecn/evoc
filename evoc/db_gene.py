import sqlite3
from collections import namedtuple
from evoc.logger import logger

GeneRow = namedtuple(
    'GeneRow',
    'gene_id, uniquename, gb_id, type_id, pro_id, nuc_id, location, seq, '
    'start, end'
)


def gene_init():
    GENE_SQL = """
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
    return GENE_SQL


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
    try:
        assert connection is not None
        cur = connection.cursor()
    except (AssertionError, AttributeError):
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    fields = []
    values = []
    where = []

    try:
        if uniquename is not None:
            fields.append('uniquename')
            where.append(uniquename)
        if gb_id is not None:
            fields.append('gb_id')
            gb_id = int(gb_id)
            where.append(gb_id)
        if type_id is not None:
            fields.append('type_id')
            type_id = int(type_id)
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
            start = int(start)
            where.append(start)
        if end is not None:
            fields.append('end')
            end = int(end)
            where.append(end)
    except ValueError:
        logger.exception('Invalid parameter specified')
        raise SystemExit('Exiting.')

    assert len(where) == len(fields)
    try:
        assert len(where) > 0
    except AssertionError:
        logger.exception('Not enough paramters supplied')
        raise SystemExit('Exiting.')

    for i in range(len(where)):
        values.append('?')
    fields = ', '.join(fields)
    values = ', '.join(values)
    where = tuple(where)

    cmd = """
        INSERT INTO gene (""" + fields + """) VALUES (""" + values + """)
    """
    try:
        cur.execute(cmd, where)
        return GeneRow(*cur.execute(
            """SELECT gene_id, uniquename, gb_id, type_id, pro_id, nuc_id,
            location, seq, start, end FROM gene WHERE gene_id = ? LIMIT 1""",
            (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught gene: {0}'.format(
            str(e), gb_id, type_id, uniquename, location)
        )


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

    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    fields = []
    where = []

    try:
        if gene_id is not None:
            where.append('gene_id = ?')
            gene_id = int(gene_id)
            fields.append(gene_id)
        if uniquename is not None:
            where.append('uniquename = ?')
            fields.append(uniquename)
        if gb_id is not None:
            where.append('gb_id = ?')
            gb_id = int(gb_id)
            fields.append(gb_id)
        if type_id is not None:
            where.append('type_id = ?')
            type_id = int(type_id)
            fields.append(type_id)
        if pro_id is not None:
            where.append('pro_id = ?')
            fields.append(pro_id)
        if nuc_id is not None:
            where.append('nuc_id = ?')
            fields.append(nuc_id)
        if start is not None:
            where.append('start = ?')
            start = int(start)
            fields.append(start)
        if end is not None:
            where.append('end = ?')
            end = int(end)
            fields.append(end)
        assert(len(fields) == len(where))
    except ValueError:
        logger.exception('Invalid paramter supplied')
        raise SystemExit('Exiting.')
    except AssertionError:
        logger.exception('Not enough paramters supplied')
        raise SystemExit('Exiting.')

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
    """
    try:
        if len(fields) > 0:
            cmd += """ WHERE """ + where
            results = connection.execute(cmd, fields)
        else:
            results = connection.execute(cmd)
        return [GeneRow(*r) for r in results]
    except AttributeError:
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught: {0}'.format(str(e)))
