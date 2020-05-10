import sqlite3
from collections import namedtuple
from evoc.logger import logger

logger.setLevel(5)


ClusterRow = namedtuple('ClusterRow', 'cluster_id, type_id')


def cluster_init():
    """cluster table init string"""

    CLUSTER_SQL = """
        CREATE TABLE IF NOT EXISTS cluster(
            cluster_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER UNIQUE NOT NULL,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
        )
    """
    return CLUSTER_SQL


def add_cluster(
    connection,
    type_id=None
):
    """Add single cluster to cluster table

    Retur: Boolean success/failure
    """
    try:
        cur = connection.cursor()
    except AttributeError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    insert = []
    values = []
    where = []

    try:
        assert type_id is not None
        if type_id is not None:
            insert.append('type_id')
            values.append('?')
            where.append(int(type_id))
        assert(len(values) == len(where) == len(insert))
        if len(values) > 0:
            insert = ', '.join(insert)
            values = ', '.join(values)
            where = tuple(where)
    except (ValueError, AssertionError):
        logger.exception('Invalid type_id specified')
        raise SystemExit('Exiting.')

    cmd = """
        INSERT INTO cluster (type_id) VALUES (""" + values + """)
    """
    try:
        cur.execute(cmd, where)
        return ClusterRow(*cur.execute(
            "SELECT cluster_id, type_id FROM cluster WHERE cluster_id = ?",
            (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Tried to add unknown type_id')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught: {0}'.format(e))
        raise SystemExit('Exiting.')


def check_cluster(
    connection,
    cluster_id=None,
    type_id=None
):
    """"Check for a cluster entry by id or type id. If none provided, return
        all cluster entries

    Return: result list, or []
    """

    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid Connection')
        raise SystemExit('Exiting.')

    values = []
    where = []

    try:
        if cluster_id is not None:
            where.append('cluster_id = ?')
            values.append(int(cluster_id))
        if type_id is not None:
            where.append('type_id = ?')
            values.append(int(type_id))
    except ValueError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')

    assert(len(values) == len(where))

    cmd = """SELECT cluster_id, type_id FROM cluster"""
    try:
        if len(values) == 0:
            result = connection.execute(cmd).fetchall()
        else:
            where = ' AND '.join(where)
            values = tuple(values)
            cmd += " WHERE " + where
            result = connection.execute(cmd, values).fetchall()
        return [ClusterRow(*r) for r in result]
    except Exception as e:
        logger.exception('Caught: {0}'.format(e))
        raise SystemExit('Exiting.')
