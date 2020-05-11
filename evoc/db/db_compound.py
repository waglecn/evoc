from collections import namedtuple
import sqlite3
from evoc.logger import logger

CompoundRow = namedtuple(
    'CompoundRow', 'compound_id, type_id, cluster_id'
)


def compound_init():
    """init statement for compounds"""
    COMPOUND_SQL = """
        CREATE TABLE IF NOT EXISTS compound(
            compound_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER NOT NULL,
            cluster_id INTEGER NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
            FOREIGN KEY (cluster_id) REFERENCES cluster(cluster_id)
        )
    """
    return COMPOUND_SQL


def add_compound(
    connection,
    type_id=None,
    cluster_id=None
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
        if type_id is not None:
            fields.append('type_id')
            type_id = int(type_id)
            where.append(type_id)
        if cluster_id is not None:
            fields.append('cluster_id')
            cluster_id = int(cluster_id)
            where.append(cluster_id)
    except ValueError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')

    assert len(where) == len(fields)
    try:
        assert len(where) > 0
    except AssertionError:
        logger.exception('Not enough parameters supplied')
        raise SystemExit('Exiting.')

    for x in range(len(fields)):
        values.append('?')
    values = ','.join(values)
    fields = ','.join(fields)
    where = tuple(where)
    cmd = """
        INSERT INTO compound (""" + fields + """)
        VALUES (""" + values + """)
    """
    try:
        cur.execute(cmd, where)
        return CompoundRow(*cur.execute(
            "SELECT compound_id, type_id, cluster_id FROM compound "
            "WHERE compound_id = ?", (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Invalid id supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exceiption('Caught: {0}'.format(str(e)))
        raise SystemExit('Exiting.')


def check_compound(
    connection,
    compound_id=None,
    type_id=None,
    cluster_id=None
):
    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')

    fields = []
    where = []

    try:
        if compound_id is not None:
            where.append('compound_id = ?')
            compound_id = int(compound_id)
            fields.append(compound_id)
        if type_id is not None:
            where.append('type_id = ?')
            type_id = int(type_id)
            fields.append(type_id)
        if cluster_id is not None:
            where.append('cluster_id = ?')
            cluster_id = int(cluster_id)
            fields.append(cluster_id)
    except ValueError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')

    assert(len(fields) == len(where))

    cmd = "SELECT compound_id, type_id, cluster_id FROM compound"
    try:
        if len(fields) > 0:
            fields = tuple(fields)
            where = ' AND '.join(where)
            cmd += " WHERE " + where
            result = connection.execute(cmd, fields)
        else:
            result = connection.execute(cmd)
        return [CompoundRow(*r) for r in result]
    except AttributeError:
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught: {0}'.format(str(e)))
        raise SystemExit('Exiting.')
