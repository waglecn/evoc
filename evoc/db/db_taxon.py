from collections import namedtuple
import sqlite3
from evoc.logger import logger

TaxonRow = namedtuple('TaxonRow', 'taxon_id, type_id, NCBI_tax_id')


def taxon_init():
    """Taxon table init string"""

    TAXON_SQL = """
        CREATE TABLE IF NOT EXISTS taxon(
            taxon_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER NOT NULL,
            NCBI_tax_id INTEGER,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
        )
    """
    return TAXON_SQL


def add_taxon(
    connection,
    NCBI_tax_id=None,
    type_id=None
):

    try:
        assert connection is not None
        cur = connection.cursor()
    except (AssertionError, AttributeError):
        logger.exception('Invalid connection supplied')
        raise SystemExit('Exiting.')

    fields = []
    values = []
    items = []

    try:
        if NCBI_tax_id is not None:
            fields.append('NCBI_tax_id')
            int(NCBI_tax_id)
            items.append(NCBI_tax_id)
        if type_id is not None:
            fields.append('type_id')
            int(type_id)
            items.append(type_id)
    except ValueError:
        logger.exception('Invalid paramters supplied')
        raise SystemExit('Exiting.')

    assert(len(fields) == len(items))

    try:
        assert len(fields) > 0
    except AssertionError:
        logger.exception('Incorrect number of paramters supplied')
        raise SystemExit('Exiting.')

    for x in range(len(fields)):
        values.append('?')

    fields = ', '.join(fields)
    values = ', '.join(values)
    items = tuple(items)

    cmd = """
        INSERT INTO taxon (""" + fields + """)
        VALUES (""" + values + """)
    """

    try:
        cur.execute(cmd, items)
        return TaxonRow(*connection.execute(
            'SELECT taxon_id, type_id, NCBI_tax_id FROM taxon '
            'WHERE taxon_id = ?', (cur.lastrowid,)
        ).fetchone())
    except sqlite3.IntegrityError:
        logger.exception('Supplied invalid taxon_id')
        raise SystemExit('Exiting.')
    except Exception as e:
        print('Caught: {0}'.format(str(e)))


def check_taxon(
    connection,
    taxon_id=None,
    NCBI_tax_id=None,
    type_id=None
):
    """ Returns taxon list, or False"""

    try:
        assert connection is not None
    except AssertionError:
        logger.exception('Invalid connection')
        raise SystemExit('Exiting.')

    fields = []
    values = []

    try:
        if taxon_id is not None:
            fields.append('taxon_id = ?')
            int(taxon_id)
            values.append(taxon_id)
        if NCBI_tax_id is not None:
            fields.append('NCBI_tax_id = ?')
            int(NCBI_tax_id)
            values.append(NCBI_tax_id)
        if type_id is not None:
            fields.append('type_id = ?')
            int(type_id)
            values.append(type_id)
    except ValueError:
        logger.exception('Invalid parameter supplied')
        raise SystemExit('Exiting.')

    assert (len(fields) == len(values))
    if len(fields) == 0:
        cmd = """
            SELECT
                taxon_id,
                type_id,
                NCBI_tax_id
            FROM taxon
        """
    else:
        fields = ' AND '.join(fields)
        values = tuple(values)

        cmd = """
            SELECT
                taxon_id,
                type_id,
                NCBI_tax_id
            FROM taxon
            WHERE """ + fields
    try:
        results = connection.execute(cmd, values).fetchall()
        return [TaxonRow(*r) for r in results]
    except Exception as e:
        logger.exception('Caught: {0}'.format(str(e)))
        raise SystemExit('Exiting.')
