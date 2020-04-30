import sqlite3

from evoc.db_types_rels import *
from evoc.db_gb import *
from evoc.db_clusters import *
from evoc.db_gene import *
from evoc.db_cluster_gene import *
from evoc.db_domain import *
from evoc.db_taxa import *
from evoc.db_molecules import *


def init_db(dbfile):
    connection = sqlite3.connect(dbfile)
    connection.isolation_level = None
    cur = connection.cursor()

    types = types_init()
    cur.execute(types)

    type_relationships = rels_init()
    cur.execute(type_relationships)

    taxa = taxa_init()
    cur.execute(taxa)

    gb = gb_init()
    cur.execute(gb)

    clusters = cluster_init()
    cur.execute(clusters)

    gene = gene_init()
    cur.execute(gene)

    cluster_gene = cluster_gene_init()
    cur.execute(cluster_gene)

    molecules = molecules_init()
    cur.execute(molecules)

    domain = domain_init()
    cur.execute(domain)

    connection.commit()

    return connection


def backup_db(dbfile, dumpfile):
    connection = init_db(dbfile)
    with open(dumpfile, 'w') as outhandle:
        for line in connection.iterdump():
            outhandle.write('{0}\n'.format(line))
        return True


def load_backup(dumpfile, newdb):
    # need a new, empty connection
    connection = sqlite3.connect(newdb)
    try:
        with open(dumpfile, 'r') as inh:
            dump = inh.read()
            connection.executescript(dump)
            connection.commit()
        return True
    except Exception:
        return False
