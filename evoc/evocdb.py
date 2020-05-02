import os
from evoc import db, utils
from evoc.evocdbitem import *
from evoc.evoclogger import logger


class EvocDb:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        try:
            self.connection = db.init_db(dbfile)
        except Exception as error:
            logger.info('error: {0}'.format(str(error)))
        else:
            logger.info('connection to: {0}'.format(self.dbfile))

        # Load default types from included file
        base_dir = os.path.dirname(__file__)
        basic_types_tsv_file = os.path.join(base_dir, 'basic_types.tsv')
        types, rels = utils.read_relationship_tsv(basic_types_tsv_file)
        assert db.load_relationships(self.connection, types, rels) is True
        # 'is_a' is special, needed as basic relationship type
        self.is_a = EvocType(origin=self, name='is_a')

        # Load the default taxon if not present
        # Unidentified microorganism - this should match type.name
        # https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=81726
        self.default_taxon = EvocTaxon(
            origin=self, type_id=EvocType(
                origin=self, name='unidentified'
            ).type_id
        )
        if self.default_taxon.taxon_id is None:
            logger.info('loading default taxon...')
            db.add_taxon(
                self.connection,
                type_id=self.default_taxon.type_id,
                NCBI_tax_id=32644  # 'unidentiied'
            )
        self.default_taxon._update()

        # Load the default cluster
        self.default_cluster_type = EvocType(
            origin=self, name='unknown_cluster'
        )
        self.default_cluster = EvocCluster(
            origin=self, type_id=self.default_cluster_type.type_id
        )
        if self.default_cluster.cluster_id is None:
            logger.info('loading default cluster...')
            self.default_cluster.add()

        # default gene type
        self.default_gene_type = EvocType(origin=self, name='unknown_gene')
        assert self.default_gene_type.type_id is not None

        # default domain_type
        self.default_domain_type = EvocType(origin=self, name='unknown_domain')
        assert self.default_domain_type.type_id is not None
        domain_parent = self.default_domain_type.parents()[0]

        self.default_whole_domain_type = EvocType(
            origin=self, name='whole_domain', description='a whole_domain'
        )
        if self.default_whole_domain_type.type_id is None:
            self.default_whole_domain_type.add()
        domain_parent.add_child(self.default_whole_domain_type)

        self.default_aS_domain_type = EvocType(
            origin=self, name='aS_domain', description='an aS_domain'
        )
        if self.default_aS_domain_type.type_id is None:
            self.default_aS_domain_type.add()
        domain_parent.add_child(self.default_aS_domain_type)

        self.basic_fill_type = EvocType(
            origin=self, name='Fill_domain',
            description='A domain between two known domains'
        )
        if self.basic_fill_type.type_id is None:
            self.default_domain_type.add_child(
                self.basic_fill_type
            )
        assert self.basic_fill_type.type_id is not None

        # default molecule_type
        self.default_molecule_type = EvocType(
            origin=self,
            name='unknown_molecule'
        )
        assert self.default_molecule_type.type_id is not None

        # build the the checkable items
        self.types = EvocTypeRows(self.connection, 'type')
        self.rels = EvocRelRows(self.connection, 'type_relationship')
        self.taxa = EvocTaxaRows(self.connection, 'taxon')

    # allows use of class as context
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info('closing connection to: {0}'.format(self.dbfile))
        self.connection.close()

    # my methods to wrap the functions in the db object
    def backup_db(self, dumpfile):
        with open(dumpfile, 'w') as outhandle:
            for line in self.connection.iterdump():
                outhandle.write('{0}\n'.format(line))
            return True


class EvocDbRows:
    def __init__(self, db_connection, table):
        self.connection = db_connection
        self.table = table

    def __call__(self, **items):
        pass


class EvocTypeRows(EvocDbRows):
    def __call__(self, **items):
        return db.check_type(self.connection, **items)

    def __contains__(self, item):
        if isinstance(item, dict):
            if len(db.check_type(self.connection, **item)) > 0:
                return True
        if isinstance(item, EvocType):
            if len(db.check_type(self.connection, **item._toDict())) > 0:
                return True
        return False

    def add(self, *args, **kwargs):
        for item in args:
            if isinstance(item, tuple):
                pass


class EvocRelRows(EvocDbRows):
    def __call__(self, **items):
        return db.check_relationship(self.connection, **items)

    def __contains__(self, item):
        if len(db.check_relationship(self.connection, **item._toDict())) > 0:
            return True
        return False


class EvocTaxaRows(EvocDbRows):
    def __call__(self, **items):
        return db.check_taxon(self.connection, **items)

    def __contains__(self, item):
        if isinstance(item, dict):
            if len(db.check_taxon(self.connection, **item)) > 0:
                return True
        if isinstance(item, EvocTaxon):
            if len(db.check_taxon(self.connection, **item._toDict())):
                return True
        return False

