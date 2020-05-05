"""One line summary

Abstract summary

Exports (classes, exceptions, functions)
"""

import os
import sqlite3

try:
    import importlib.resources as importlib_resources
except ImportError:
    # Python <3.7 backported `importlib_resources`
    import importlib_resources

from evoc.db_type_rel import *
from evoc.db_gb import *
from evoc.db_cluster import *
from evoc.db_gene import *
from evoc.db_cluster_gene import *
from evoc.db_domain import *
from evoc.db_taxon import *
from evoc.db_compound import *

from evoc.logger import logger


def init_db(dbfile):
    if os.path.exists(dbfile):
        logger.debug('Found existing file {}'.format(os.path.abspath(dbfile)))
    else:
        logger.debug('Creating new file {}'.format(os.path.abspath(dbfile)))
    connection = sqlite3.connect(dbfile)
    connection.isolation_level = None

    TYPES_SQL = type_init()
    connection.execute(TYPES_SQL)

    REL_SQL = rel_init()
    connection.execute(REL_SQL)

    TAXON_SQL = taxon_init()
    connection.execute(TAXON_SQL)

    GB_SQL = gb_init()
    connection.execute(GB_SQL)

    CLUSTER_SQL = cluster_init()
    connection.execute(CLUSTER_SQL)

    GENE_SQL = gene_init()
    connection.execute(GENE_SQL)

    CLUSTER_GENE_SQL = cluster_gene_init()
    connection.execute(CLUSTER_GENE_SQL)

    COMPOUND_SQL = compound_init()
    connection.execute(COMPOUND_SQL)

    DOMAIN_SQL = domain_init()
    connection.execute(DOMAIN_SQL)

    with importlib_resources.path('evoc', 'basic_types.tsv') as path:
        basic_types_file = path
    types, rels = parse_relationship_tsv(basic_types_file)
    load_relationships(connection, types, rels)
    connection.commit()

    return connection


def dump_backup(dbfile, dumpfile):
    connection = init_db(dbfile)
    with open(dumpfile, 'w') as outhandle:
        for line in connection.iterdump():
            outhandle.write('{0}\n'.format(line))
    logger.debug('dumped database to {}'.format(os.path.abspath(dumpfile)))


def load_backup(dumpfile, newdb):
    # need a new, empty connection
    logger.debug('attempting to import {} into {}'.format(
        os.path.abspath(dumpfile), os.path.abspath(newdb)
    ))
    connection = sqlite3.connect(newdb)
    try:
        with open(dumpfile, 'r') as inh:
            dump = inh.read()
            connection.executescript(dump)
            connection.commit()
        logger.debug('complete')
    except Exception as e:
        logger.debug('failed: {}'.format(e))
        raise e


def parse_relationship_tsv(tsv_file, types=None, relationships=None):
    """open a relationship tsv file, return tuple (types, relationshps)"""

    sections = ['# types', '# relationships']

    if types is None:
        types = []
    if relationships is None:
        relationships = []

    with open(tsv_file, 'r') as infile:
        section = None
        lineno = 0
        for line in infile:
            lineno += 1
            line = line.rstrip()
            if len(line) == 0:
                continue
            elif line[0] == '#':
                if not line[1] == '#':
                    section = line
                    assert section in sections, '{1} {0} not a section'.format(
                        section,
                        lineno
                    )
            elif len(line) > 0 and section == '# types':
                line = tuple(line.split('\t'))
                assert len(line) == 2, 'bad line:{1} {0}'.format(line, lineno)
                if line not in types:
                    types.append(line)
                    typenames = [t[0] for t in types]
            elif len(line) > 0 and section == '# relationships':
                line = line.split('\t')
                assert len(line) == 3, 'bad line: {1} {0}'.format(line, lineno)
                # (object, subject, relationship)
                tobject = line[2]
                assert tobject in typenames, (
                    typenames,
                    '{1} {0} not in types'.format(
                        tobject,
                        lineno
                    )
                )
                tsubject = line[0]
                assert tsubject in typenames, '{1} {0} not in types'.format(
                    tsubject,
                    lineno
                )
                trel = line[1]
                assert tobject in typenames, '{1} {0} not in types'.format(
                    trel,
                    lineno
                )
                new_item = (tobject, tsubject, trel)
                if new_item not in relationships:
                    relationships.append(new_item)
    return (types, relationships)


def load_relationships(connection, types, relationships):
    """
    Add a set of types and relationships. This will not add duplicates.

    arguments:
        types: from utils.read_relationship_tsv
        relationships: from utils.read_relationship_tsv

    return:
        Boolean success/failure
    """

    type_map = {}
    rels_to_add = []

    try:
        base_types = check_type(connection)
        for base in base_types:
            if base[1] not in type_map:
                type_map[base[1]] = base[0]

        for item in types:
            temp = check_type(connection, name=item[0])
            if not temp:
                assert add_type(
                    connection, name=item[0], description=item[1]
                ), 'could not add type'
                temp = check_type(
                    connection, name=item[0], description=item[1]
                )
            type_key = temp[0][1]
            type_id = temp[0][0]
            if type_key not in type_map:
                type_map[type_key] = type_id

        for rel in relationships:
            object_id = type_map[rel[0]]
            subject_id = type_map[rel[1]]
            type_id = type_map[rel[2]]
            new_item = (object_id, subject_id, type_id)
            if (
                new_item not in rels_to_add
                and not check_relationship(
                    connection,
                    object_id=new_item[0],
                    subject_id=new_item[1],
                    type_id=new_item[2]
                )
            ):
                rels_to_add.append(new_item)

        cmd = """
            INSERT OR IGNORE INTO type_relationship
                (object_id, subject_id, type_id) VALUES (?, ?, ?)
        """
        cur = connection.cursor()
        cur.executemany(cmd, rels_to_add)
        return True
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def encode_gene_location(location):
    """given a gene location, return json encoded location"""
    import json
    try:
        item = json.dumps(location)
        if item == 'null':
            raise Exception
        return item
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False


def decode_gene_location(encoded_location):
    """given a json-encoded gene location, return decoded location"""
    import json
    try:
        item = json.loads(encoded_location)
        return item
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        return False
