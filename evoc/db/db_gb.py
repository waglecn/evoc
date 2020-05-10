import sqlite3
from collections import namedtuple
from evoc.logger import logger

GbRow = namedtuple('GbRow', 'gb_id, prefix, taxon_id, loc, gb')


def gb_init():
    """gb table init string"""

    gb = """
        CREATE TABLE IF NOT EXISTS gb(
            gb_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            prefix TEXT NOT NULL,
            taxon_id INTEGER NOT NULL,
            loc TEXT UNIQUE NOT NULL,
            gb TEXT,
            FOREIGN KEY (taxon_id) REFERENCES taxon(taxon_id)
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

    try:
        assert connection is not None
        cur = connection.cursor()
    except (AssertionError, AttributeError):
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

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
    except ValueError:
        logger.exception('Invalid taxon_id supplied')
        raise SystemExit('Exiting.')

    try:
        assert(
            len(values) == len(where) == len(insert) and len(values) > 0
        )
    except AssertionError:
        logger.exception('Invalid number of parameters supplied')
        raise SystemExit('Exiting.')

    insert = ', '.join(insert)
    values = ', '.join(values)
    where = tuple(where)

    cmd = """
        INSERT INTO gb (""" + insert + """) VALUES (""" + values + """)
    """
    try:
        cur.execute(cmd, where)
        return GbRow(*cur.execute(
            'SELECT gb_id, prefix, taxon_id, loc, gb FROM gb '
            'WHERE gb_id = ?', (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Invalid taxon_id supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        raise SystemExit('Exiting.')


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

    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

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
    except ValueError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')

    assert(len(values) == len(where))

    cmd = "SELECT gb_id, taxon_id, prefix, loc, gb FROM gb"""

    try:
        if len(values) > 0:
            where = ' AND '.join(where)
            values = tuple(values)
            cmd += " WHERE """ + where
            result = connection.execute(cmd, values)
        else:
            result = connection.execute(cmd)
        return [GbRow(*r) for r in result]
    except Exception as e:
        logger.exception('Caught: {0}'.format(str(e)))
        raise SystemExit('Exiting.')
