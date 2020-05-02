def taxa_init():
    """taxa table init string"""

    taxa_init_statement = """
        CREATE TABLE IF NOT EXISTS taxon(
            taxon_id INTEGER UNIQUE PRIMARY KEY NOT NULL,
            type_id INTEGER NOT NULL,
            NCBI_tax_id INTEGER,
            FOREIGN KEY (type_id) REFERENCES type(type_id)
        )
    """

    return taxa_init_statement


def add_taxon(
    connection,
    NCBI_tax_id=None,
    type_id=None
):

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

        assert(len(fields) == len(items))
        assert len(fields) > 0

        for x in range(len(fields)):
            values.append('?')

        fields = ', '.join(fields)
        values = ', '.join(values)
        items = tuple(items)

        cmd = """
            INSERT INTO taxon (""" + fields + """)
            VALUES (""" + values + """)
        """
        cur = connection.cursor()
        cur.execute(cmd, items)
        return True
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def check_taxon(
    connection,
    taxon_id=None,
    NCBI_tax_id=None,
    type_id=None
):
    """ Returns taxon list, or False"""
    cur = connection.cursor()

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

        results = cur.execute(cmd, values).fetchall()
        return results
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False
