"""One line summary

Abstract summary

Exports (classes, exceptions, functions)
"""

import os
import sqlite3
from collections import namedtuple

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

    try:
        connection = sqlite3.connect(dbfile)
        connection.execute('PRAGMA foreign_keys = 1')
    except Exception as e:
        logger.error('Could not open: {}'.format(e))
        raise SystemExit('Exiting.')

    TYPE_SQL = type_init()
    connection.execute(TYPE_SQL)

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
    load_types_rels(connection, types, rels)
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
    try:
        connection = sqlite3.connect(newdb)
    except Exception as e:
        logger.exception('Could not open new file {}\n{}'.format(newdb, e))
        raise SystemExit('Exiting.')

    try:
        with open(dumpfile, 'r') as inh:
            buff = ""
            for dump in inh:
                dump = dump.replace('COMMIT', '')
                buff += dump
                if ';' in buff:
                    connection.executescript(buff)
                    connection.commit()
                    buff = ""
        logger.debug('complete')
    except Exception as e:
        logger.exception('failed: {}'.format(e))
        raise SystemExit('Exiting.')


def parse_relationship_tsv(tsv_file, types=set(), relationships=set()):
    """Open a tsv file, return tuple of sets (types, relationshps)"""

    Type = namedtuple('Type', "name, description")
    Rel = namedtuple('Rel', "subject, rel, object")

    try:
        infile = [
            line.strip().split('\t') for line in open(tsv_file, 'r') if
            not line.startswith('#')
        ]
    except FileNotFoundError:
        logger.error(
            'tsv File not found: {}'.format(os.path.abspath(tsv_file))
        )
        raise SystemExit('Exiting.')

    types = {Type(*line) for line in infile if len(line) == 2}
    relationships = {Rel(*line) for line in infile if len(line) == 3}

    known_names = {t.name for t in types}
    for rel in relationships:
        for name in rel:
            if name not in known_names:
                logger.warn('unmatched type name {}'.format(name))
                types.add(Type(name, 'no description'))
                known_names.add(name)

    return (types, relationships)


def load_types_rels(connection, types, relationships):
    """
    Add a set of types and relationships. This will not add duplicates.

    arguments:
        types: from utils.read_relationship_tsv
        relationships: from utils.read_relationship_tsv

    return:
        Boolean success/failure
    """

    rels_to_add = []

    known = set()
    for t in types:
        t_result = add_type(
            connection=connection,
            name=t.name,
            description=t.description
        )
        known.add(t_result)

    known_names = {t.name: t.type_id for t in known}
    for rel in relationships:
        new_rel = (
            known_names[rel.object],
            known_names[rel.subject],
            known_names[rel.rel]
        )
        rels_to_add.append(new_rel)

        cmd = """
            INSERT OR IGNORE INTO type_relationship
                (object_id, subject_id, type_id) VALUES (?, ?, ?)
        """
    connection.executemany(cmd, rels_to_add)


def encode_gene_location(location):
    """given a gene location, return json encoded location"""
    import json
    try:
        item = json.dumps(location)
        if item == 'null':
            raise ValueError('null returned')
        return item
    except Exception:
        logger.exception('Problem converting location')
        raise SystemExit('Exiting.')


def decode_gene_location(encoded_location):
    """given a json-encoded gene location, return decoded location"""
    import json
    try:
        item = json.loads(encoded_location)
        return item
    except Exception:
        logger.exception('Problem decoding location')
        raise SystemExit('Exiting.')
