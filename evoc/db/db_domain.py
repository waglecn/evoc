import sqlite3
from collections import namedtuple
from evoc.logger import logger

DomainRow = namedtuple(
    'DomainRow', 'domain_id, source_gene_id, type_id, start, end'
)


def domain_init():
    DOMAIN_SQL = """
        CREATE TABLE IF NOT EXISTS domain(
            domain_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            source_gene_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
            FOREIGN KEY (source_gene_id) REFERENCES gene(gene_id)
        )
    """
    return DOMAIN_SQL


def add_domain(
    connection,
    source_gene_id=None,
    type_id=None,
    start=None,
    end=None
):
    try:
        assert connection is not None
        cur = connection.cursor()
    except (AssertionError, AttributeError):
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')

    fields = []
    values = []
    where = []

    try:
        if source_gene_id is not None:
            fields.append('source_gene_id')
            where.append(int(source_gene_id))
        if type_id is not None:
            fields.append('type_id')
            where.append(int(type_id))
        if start is not None:
            fields.append('start')
            where.append(int(start))
        if end is not None:
            fields.append('end')
            where.append(int(end))
    except ValueError:
        logger.exception('Invalid type supplied')
        raise SystemExit('Exiting.')

    try:
        assert(len(fields) == len(where))
        assert(len(fields) > 0)
    except AssertionError:
        logger.exception('Insufficient number of arguments supplied')
        raise SystemExit('Exiting.')

    for x in range(len(fields)):
        values.append('?')
    values = ','.join(values)
    fields = ','.join(fields)
    where = tuple(where)

    cmd = "INSERT INTO domain ({}) VALUES ({})".format(fields, values)
    try:
        cur.execute(cmd, where)
        return DomainRow(*cur.execute(
            "SELECT domain_id, source_gene_id, type_id, start, end "
            "FROM domain WHERE domain_id = ?", (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Invalid domain to be added')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught: {}'.format(e))
        raise SystemExit('Exiting.')


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
        domain_id, source_gene_id, type_id, start, end
    """
    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection supplied')

    fields = []
    where = []

    try:
        if domain_id is not None:
            where.append('domain_id = ?')
            fields.append(int(domain_id))
        if start is not None:
            where.append('start = ?')
            fields.append(int(start))
        if end is not None:
            where.append('end = ?')
            fields.append(int(end))
        if source_gene_id is not None:
            where.append('source_gene_id = ?')
            fields.append(int(source_gene_id))
        if type_id is not None:
            where.append('type_id = ?')
            fields.append(int(type_id))
    except ValueError:
        logger.exception('Invalid int arugment passed')
        raise SystemExit('Exiting.')
    assert(len(fields) == len(where))

    cmd = "SELECT domain_id, source_gene_id, type_id, start, end FROM domain"

    try:
        if len(fields) > 0:
            where = ' AND '.join(where)
            fields = tuple(fields)
            cmd += " WHERE " + where
            result = connection.execute(cmd, fields)
        else:
            result = connection.execute(cmd)
        return [DomainRow(*r) for r in result]
    except AttributeError:
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught: {}'.format(e))
        raise SystemExit('Exiting.')
