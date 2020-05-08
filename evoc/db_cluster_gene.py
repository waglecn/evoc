import sqlite3
from collections import namedtuple
from evoc.logger import logger

ClusterGeneRow = namedtuple(
    'ClusterGeneRow', 'cluster_gene_id, cluster_id, gene_id'
)


def cluster_gene_init():
    """cluster_gene table init string"""

    CLUSTER_GENE_SQL = """
        CREATE TABLE IF NOT EXISTS cluster_gene(
            cluster_gene_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            cluster_id INTEGER NOT NULL,
            gene_id INTEGER NOT NULL,
            FOREIGN KEY (cluster_id) REFERENCES cluster(cluster_id),
            FOREIGN KEY (gene_id) REFERENCES gene(gene_id)
        )
    """
    return CLUSTER_GENE_SQL


def add_cluster_gene(connection, cluster_id=None, gene_id=None):
    """Add a single entry to the cluster_gene table"""
    try:
        assert connection is not None
        cur = connection.cursor()
    except (AssertionError, AttributeError):
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')

    insert = []
    values = []
    where = []

    try:
        if cluster_id is not None:
            insert.append('cluster_id')
            values.append('?')
            where.append(int(cluster_id))
        if gene_id is not None:
            insert.append('gene_id')
            values.append('?')
            where.append(int(gene_id))
    except ValueError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')

    assert len(values) == len(where) == len(insert)
    if len(values) > 0:
        insert = ', '.join(insert)
        values = ', '.join(values)
        where = tuple(where)

    try:
        cmd = "INSERT INTO cluster_gene ({}) VALUES({})".format(
            insert, values
        )
        cur.execute(cmd, where)
        return ClusterGeneRow(*cur.execute(
            "SELECT cluster_gene_id, cluster_id, gene_id FROM cluster_gene "
            "WHERE cluster_gene_id = ?", (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Invalid id paramter supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Error trying to add cluster_gene: {}'.format(e))
        raise SystemExit('Exiting.')


def check_cluster_gene(
    connection,
    cluster_gene_id=None,
    cluster_id=None,
    gene_id=None
):
    """Check for a single entry in the cluster_gene table by id, gene_id,
        cluster_id. If none provided, will return all entries in the table"""

    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalind connection supplied')
        raise SystemExit('Exiting.')

    values = []
    where = []

    try:
        if cluster_gene_id is not None:
            where.append('cluster_gene_id = ?')
            values.append(int(cluster_gene_id))
        if gene_id is not None:
            where.append('gene_id = ?')
            values.append(int(gene_id))
        if cluster_id is not None:
            where.append('cluster_id = ?')
            values.append(int(cluster_id))
    except ValueError:
        logger.exception('Invalid id parameter supplied')
        raise SystemExit('Exiting.')

    assert(len(values) == len(where))

    cmd = """ SELECT cluster_gene_id, cluster_id, gene_id
        FROM cluster_gene"""
    try:
        if len(values) > 0:
            where = ' AND '.join(where)
            values = tuple(values)
            cmd += " WHERE " + where
            result = connection.execute(cmd, values)
        else:
            result = connection.execute(cmd)
        return [ClusterGeneRow(*r) for r in result]
    except AttributeError:
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')
    except Exception as e:
        logger.exception('Caught: {0}'.format(e))
        raise SystemExit('Exiting.')
