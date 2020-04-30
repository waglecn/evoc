import os
import timeit
import io
import gzip
import pickle
from ete3 import NCBITaxa
from Bio import SeqIO, SeqFeature
from evoc.db_types_rels import check_type, add_type, \
    check_relationship, add_relationship
from evoc.db_gb import check_gb, add_gb
from evoc.db_taxa import add_taxon, check_taxon
from evoc.db_clusters import check_cluster, add_cluster
from evoc.db_gene import check_gene, add_gene
from evoc.db_cluster_gene import add_cluster_gene
from evoc.db_domain import check_domain, add_domain
from evoc.db_molecules import check_molecule, add_molecule
from evoc.utils import encode_gene_location, decode_gene_location
from evoc.evoclogger import logger


class EvocType:
    type_id = None
    name = None
    description = None
    origin = None
    children = None
    parents = None

    def __init__(self, **items):
        # pass anything to constructor, store only relevant
        if 'name' in items:
            self.name = items['name']
        if 'description' in items:
            self.description = items['description']
        if 'type_id' in items:
            self.type_id = items['type_id']
        if 'origin' in items:
            self.origin = items['origin']
        self._update()

    def __repr__(self):
        return "({0}) {1}".format(self.type_id, self.name)

    def __str__(self):
        if self.origin is None:
            dbfile = None
        else:
            dbfile = self.origin.dbfile
        return "\norigin: {0}\ntype_id: {1}\nname: {2}" \
            "\ndescription: {3}\n".format(
                dbfile,
                self.type_id,
                self.name,
                self.description
            )

    def __eq__(self, other):
        if isinstance(other, EvocType):
            return self.name == other.name \
                and self.type_id == other.type_id
        return False

    def _update(self):
        if self.origin is not None:
            result = check_type(
                self.origin.connection, name=self.name,
                type_id=self.type_id, description=self.description
            )
            if result is not None and len(result) > 0:
                if self.type_id != result[0][0]:
                    self.type_id = result[0][0]
                if self.name != result[0][1]:
                    self.name = result[0][1]
                if self.description != result[0][2]:
                    self.description = result[0][2]
            else:
                self.type_id = None

    def _inc_child(self, description=None, rel=None):
        assert self.origin is not None
        if rel is None:
            rel = self.origin.is_a
        if description is not None:
            description = description
        else:
            description = 'no description'
        # instead of 1, be smarter about initial value
        inc_id = len(self.children()) + 1
        proposed = EvocType(origin=self.origin, name="{0}_{1}".format(
            self.name, inc_id
        ))
        while proposed.type_id is not None:
            inc_id += 1
            proposed.name = "{0}_{1}".format(self.name, inc_id)
            proposed.type_id = None
            proposed.description = None
            proposed._update()
        proposed.description = description
        proposed.add()
        assert add_relationship(
            connection=self.origin.connection,
            subject_id=proposed.type_id, object_id=self.type_id,
            type_id=rel.type_id
        )
        return proposed

    def _toDict(self):
        item = {}
        if self.name is not None:
            item['name'] = self.name
        if self.description is not None:
            item['description'] = self.description
        if self.type_id is not None:
            item['type_id'] = self.type_id
        return item

    def _fromTuple(self, row):
        return EvocType(
            origin=self.origin, type_id=row[0], name=row[1], description=row[2]
        )

    def children(self):
        if self.origin is not None:
            self._update()
            if self.type_id is not None:
                result = check_relationship(
                    self.origin.connection, object_id=self.type_id
                )
                return [
                    EvocType(origin=self.origin, type_id=r[2]) for r in result
                ]
        return None

    def parents(self):
        if self.origin is not None:
            self._update()
            if self.type_id is not None:
                result = check_relationship(
                    self.origin.connection, subject_id=self.type_id
                )
                return [
                    EvocType(origin=self.origin, type_id=r[1]) for r in result
                ]
        return None

    def all_parents(self):
        all_parent_list = []
        if self.origin is not None:
            to_check = self.parents()
            while len(to_check) > 0:
                p = to_check.pop()
                all_parent_list.append(p)
                for parent in p.parents():
                    to_check.append(parent)
            return all_parent_list

    def all_children(self):
        all_children_list = []
        if self.origin is not None:
            to_check = self.children()
            while len(to_check) > 0:
                c = to_check.pop()
                all_children_list.append(c)
                for child in c.children():
                    to_check.append(child)
            return all_children_list
        return []

    def add(self, origin=None):
        if origin is not None:
            self.origin = origin
        assert self.origin is not None
        assert self.description is not None
        if self.type_id is None:
            add_type(
                self.origin.connection,
                name=self.name,
                description=self.description
            )
            self._update()

    def add_child(self, child_type, rel_type=None):
        assert self.origin is not None
        if child_type.type_id is None:
            child_type.add(origin=self.origin)
        if rel_type is None:
            rel_type = self.origin.is_a
        assert rel_type.type_id is not None
        result = check_relationship(
            connection=self.origin.connection,
            subject_id=child_type.type_id, object_id=self.type_id,
            type_id=self.origin.is_a.type_id
        )
        if result is None or len(result) == 0:
            assert add_relationship(
                connection=self.origin.connection,
                subject_id=child_type.type_id, object_id=self.type_id,
                type_id=rel_type.type_id
            )


class EvocRel:
    object_id = None
    subject_id = None
    type_id = None
    origin = None

    def __init__(self, **items):
        if 'object_id' in items:
            self.object_id = items['object_id']
        if 'subject_id' in items:
            self.subject_id = items['subject_id']
        if 'type_id' in items:
            self.subject_id = items['type_id']
        if 'origin' in items:
            self.origin = items['origin']

    def _toDict(self):
        item = {}
        if self.object_id is not None:
            item['object_id'] = self.object_id
        if self.subject_id is not None:
            item['subject_id'] = self.subject_id
        if self.type_id is not None:
            item['type_id'] = self.type_id
        return item


class EvocTaxon:
    NCBI_tax_id = None
    taxon_id = None
    type_id = None
    origin = None
    type_item = EvocType()

    def __init__(self, taxonomy_items=None, **items):
        if 'origin' in items:
            self.origin = items['origin']
        if taxonomy_items is not None:
            assert self.origin is not None
            self._create_taxon(taxonomy_items)
        else:
            if 'NCBI_tax_id' in items:
                self.NCBI_tax_id = items['NCBI_tax_id']
            if 'taxon_id' in items:
                self.taxon_id = items['taxon_id']
            if 'type_id' in items:
                self.type_id = items['type_id']
            self._update()

    def __repr__(self):
        return "(tax {0}) - {1}\tNCBI TAXID:{2}".format(
            self.taxon_id, self.type_item.name, self.NCBI_tax_id
        )

    def __eq__(self, other):
        return self.NCBI_tax_id == other.NCBI_tax_id and \
            self.type_id == other.type_id

    def _update(self):
        if self.origin is not None:
            result = check_taxon(
                self.origin.connection, NCBI_tax_id=self.NCBI_tax_id,
                type_id=self.type_id, taxon_id=self.taxon_id
            )
            if result is not None and len(result) > 0:
                if self.taxon_id != result[0][0]:
                    self.taxon_id = result[0][0]
                if self.type_id != result[0][1]:
                    self.type_id = result[0][1]
                if self.NCBI_tax_id != result[0][2]:
                    self.NCBI_tax_id = result[0][2]
                self.type_item = EvocType(
                    origin=self.origin, type_id=self.type_id
                )

    def _create_taxon(self, taxon_items):
        # taxon_items are derived from the originating genbank file
        t_start = timeit.default_timer()
        assert isinstance(taxon_items[0], str)
        assert isinstance(taxon_items[1], list)
        assert isinstance(taxon_items[2], list)
        # ugly unpacking here
        _organism = taxon_items[0]
        _taxonomy = taxon_items[1]

        # build the taxonomy stuff
        if _organism == '':
            # this shoulnd't happen anymore with the new wrapped class
            self.taxon_id = self.origin.default_taxon.taxon_id
            self._update()
            assert self == self.origin.default_taxon
        else:
            # build up type_items and rels
            # default tax_type = unidentified
            # parent of the default tax_type is:
            # unidentified->organism
            parent_tax_type = self.origin.default_taxon.type_item.parents()[0]
            pname = parent_tax_type.name
            types_to_add = []
            rels_to_add = []
            types_to_add.append((pname, ''))
            types_to_add.append(('is_a', ''))
            # taxonomy = [A, B, C, D, ... etc]
            # A is_a B, B is_a C, C is_a D ... is_a organism
            for item in _taxonomy + [_organism]:
                types_to_add.append((item, 'taxon {0}'.format(item)))
                rels_to_add.append((item, pname, 'is_a'))
                pname = item
            type_cmd = """
                INSERT OR IGNORE INTO type (name, description) VALUES(?, ?)
            """
            self.origin.connection.executemany(type_cmd, types_to_add)
            tdict = {}
            for t in types_to_add:
                tresult = check_type(
                    connection=self.origin.connection, name=t[0]
                )
                tdict[t[0]] = tresult[0][0]
            rels_to_add = [
                (tdict[r[0]], tdict[r[1]], tdict[r[2]]) for r in rels_to_add
            ]
            rels_cmd = """
                INSERT OR IGNORE INTO type_relationship
                    (subject_id, object_id, type_id)
                VALUES(?, ?, ?)
            """
            self.origin.connection.executemany(rels_cmd, rels_to_add)
            self.type_id = tdict[pname]
            self.NCBI_tax_id = 0
            self.add()
        t_end = timeit.default_timer()
        logger.info('taxon {0:.2f}'.format(t_end - t_start))

    def _toDict(self):
        item = {}
        if self.taxon_id is not None:
            item['taxon_id'] = self.taxon_id
        if self.NCBI_tax_id is not None:
            item['NCBI_tax_id'] = self.NCBI_tax_id
        if self.type_id is not None:
            item['type_id'] = self.type_id
        return item

    def add(self, origin=None):
        if origin is not None:
            self.origin = origin
        assert self.origin is not None
        if self.taxon_id is None:
            assert add_taxon(
                connection=self.origin.connection,
                type_id=self.type_id,
                NCBI_tax_id=self.NCBI_tax_id
            )
            self._update()


class WrappedGB:
    filename = None
    records = None
    taxid = 32644  # unidentified
    lname = 'unidentified'
    strain = None
    refseq = None
    genbank = None
    aSver = None
    gbz = None
    assembly = None

    _filesize = None
    _packedsize = None

    def __init__(self, data=None, **items):
        self._data = data
        if 'filename' in items:
            self.filename = items['filename']
            logger.info('filename provided: {}'.format(self.filename))
        if 'gbz' in items:
            self.gbz = items['gbz']
            logger.info('gbz provided: {}'.format(self.gbz))
        if 'records' in items:
            self.records = items['records']
            logger.info('records provided; {}'.format(self.records))
        self._process()

    def __str__(self):
        return '{0}\nAssembly:{1}\n{2}\t{3}\t{4}\nrefseq:{5}\tgenbank{6}\t' \
            'aSver{6}\n'.format(
                self.filename, self.assembly,
                self.taxid, self.lname, self.strain,
                self.refseq, self.genbank, self.aSver
            )

    def _process(self):
        # try to guess _instring - overwrite kwargs
        if isinstance(self._data, list):
            self.records = self._data
            logger.info('data paramter provided as list')
        elif isinstance(self._data, str):
            self.filename = self._data
            logger.info('data paramter provided as str')
        elif isinstance(self._data, bytes):
            self.gbz = self._data
            logger.info('data paramter provided as bytes')

        if self.gbz is not None:
            self.records = pickle.loads(gzip.decompress(self.gbz))
            logger.info('records loaded from compressed bytes')
        elif self.filename is not None:
            logger.info('loading from filename...')
            try:
                if self.filename.endswith('.gz'):
                    logger.info('  .gz file')
                    contents = io.StringIO(
                        gzip.open(self.filename, 'rb').read().decode(
                            'utf-8', errors='ignore'
                        )
                    )
                else:
                    logger.info('  gb file')
                    contents = open(self.filename, 'r')
                self.records = [r for r in SeqIO.parse(contents, 'gb')]
            except FileNotFoundError:
                pass

        if self.records is not None:
            self._get_assembly_info()
            self._get_tax_info()
            self._get_anno_info()

    def _stats(self):
        try:
            self._filesize = os.stat(self.filename).st_size
        except Exception:
            self._filesize = 'N/A'
        self._packedsize = len(self.dumpz)
        print('filesize: {0}\tpackedsize: {1}'.format(
            self._filesize, self._packedsize
        ))

    @property
    def dumpz(self):
        if self.gbz is not None:
            return self.gbz
        else:
            return gzip.compress(pickle.dumps(self.records), compresslevel=9)

    def _get_assembly_info(self):
        # extracting assembly info
        logger.info('checking assembly info')
        if len(self.records) > 0:
            if hasattr(self.records[0], 'filename'):
                self.filename = self.records[0].filename
                logger.info(
                    '  filename found in records: {}'.format(self.filename)
                )
            self.records[0].filename = self.filename
            logger.info(
                '  adding filename "{}" to records'.format(self.filename)
            )

        if self.filename is not None:
            head, tail = os.path.split(self.filename)
            self.assembly = '.'.join(tail.split('.')[:2])
            i = self.assembly.find('GCF_')
            if i > 0:
                # hack for asdb file with no assembly id anywhere inside
                self.assembly = self.assembly[i:]
            logger.info('  assembly name from file: {}'.format(self.assembly))

        if hasattr(self.records[0], 'dbxrefs'):
            for a in self.records[0].dbxrefs:
                if a.startswith('Assembly'):
                    self.assembly = a.split(':')[-1]
                    logger.info(
                        '  assembly name from dbxrefs annotaion: {}'.format(
                            self.assembly
                        )
                    )

        if (
            'comment' in self.records[0].annotations and
            self.records[0].annotations['comment'].startswith('MIBiG')
        ):
            self.assembly = self.records[0].id
            logger.info('  MiBIG found, setting assembly from id: {}'.format(
                self.assembly
            ))
        subregions = [
            f for f in self.records[0].features if f.type == 'subregion'
        ]
        if (
            len(subregions) > 0 and hasattr(subregions[0], 'qualifiers') and
            'aStool' in subregions[0].qualifiers
        ):
            self.assembly = self.records[0].id
            logger.info('  MiBIG found, setting assembly from id: {}'.format(
                self.assembly
            ))

        if (
            hasattr(self.records[0], 'annotations') and
            'sequence_version' in self.records[0].annotations
        ):
            assembly_version = self.records[0].annotations['sequence_version']
            logger.info(
                '  accession version: {}'.format(assembly_version)
            )
        if '.' not in self.assembly and assembly_version is not None:
            self.assembly = '{0}.{1}'.format(self.assembly, assembly_version)
            logger.info('  Adding version to assembly name: {}'.format(
                self.assembly
            ))

        # This is ugly and prone to break
        if 'AA' in self.assembly and self.taxid == 32644:
            self.assembly = self.assembly[self.assembly.find('AA'):]
            parts = self.assembly.split('.')[0].split('-')
            try:
                self.strain = parts[1]
            except IndexError:
                pass
            self.assembly = parts[0]
            logger.info('  WAC assembly without tax info: {}'.format(
                self.assembly
            ))

    def _get_tax_info(self):
        # requires self.record
        # TAXID, NAME, STRAIN
        ncbi = NCBITaxa()
        source_feature = [
            source for source in self.records[0].features if
            source.type == 'source'
        ]
        if (
            len(source_feature) == 1 and
            hasattr(source_feature[0], 'qualifiers')
        ):
            logger.info('examining source feature on first record...')

            if 'db_xref' in source_feature[0].qualifiers:
                taxid = [
                    d for d in source_feature[0].qualifiers['db_xref'] if
                    d.startswith('taxon')
                ]
                if len(taxid) > 0:
                    self.taxid = int(taxid[0].split(':')[1])
                    logger.info(
                        '  found taxid in dbxrefs {}'.format(self.taxid)
                    )

            if 'organism' in source_feature[0].qualifiers:
                lname = [l for l in source_feature[0].qualifiers['organism']]
                if len(lname) > 0:
                    self.lname = lname[0]
                    logger.info(
                        '  found organism name in qualifiers: {}'.format(
                            self.lname
                        )
                    )

            if (
                'strain' in source_feature[0].qualifiers and
                self.strain is None
            ):
                strain = [s for s in source_feature[0].qualifiers['strain']]
                if len(strain) > 0:
                    self.strain = strain[0]
                    logger.info(
                        '  found strain name in qualifiers: {}'.format(
                            self.strain
                        )
                    )

            if (
                'isolate' in source_feature[0].qualifiers and
                self.strain is None
            ):
                isolate = [i for i in source_feature[0].qualifiers['isolate']]
                if len(isolate) > 0:
                    self.strain = isolate[0]
                    logger.info(
                        '  found strain(isolate) name in qualifiers: {}'
                        ''.format(
                            self.strain
                        )
                    )

        if (
            hasattr(self.records[0], 'annotations') and
            'organism' in self.records[0].annotations
        ):
            self.lname = self.records[0].annotations['organism']
            logger.info(
                '  found organism in r0 annotations: {}. Look for taxid'
                ''.format(
                    self.lname
                )
            )
            temp = ncbi.get_name_translator([self.lname])
            if len(temp.keys()) > 0:
                self.taxid = temp[self.lname][0]
                if self.strain is None:
                    self.strain = 'unknown_strain'
                logger.info('  found taxid: {}, strain: {}'.format(
                    self.taxid, self.strain
                ))

        if self.lname == '.':
            logger.info('  No taxon name in GB - trying to match taxid')
            temp = ncbi.get_taxid_translator([self.taxid])
            if len(temp.keys()) > 0:
                self.lname = temp[self.taxid]
                logger.info('    taxon name found: {}'.format(self.lname))

        if self.strain is not None:
            logger.info('  stripping strain {} from {}'.format(
                self.strain, self.lname
            ))
            self.lname = self.lname.replace(self.strain, '').strip()
        else:
            self.strain = 'unknown_strain'
            logger.info('  no strain, setting to "unknown_strain"')

    def _get_anno_info(self):
        # REFSEQ or GENBANK annotations?
        self.refseq = False
        self.genbank = False
        self.aSver = '0.0'
        logger.info('examining annotations present...')
        if hasattr(self.records[0], 'annotations'):
            if (
                'keywords' in self.records[0].annotations and
                'WGS' in self.records[0].annotations['keywords']
            ):
                self.genbank = True
                logger.info('  Genbank annotations present (WGS)')
            if (
                'keywords' in self.records[0].annotations and
                'RefSeq' in self.records[0].annotations['keywords']
            ):
                self.refseq = True
                logger.info('  Refseq annotations present')

            self._scan_for_aS_info()

    def _scan_for_aS_info(self):
        original_tag = self.aSver
        for r in self.records:
            # ANTISMASH VERSION annotation present?
            if (
                'structured_comment' in r.annotations and
                'antiSMASH-Data' in r.annotations[
                    'structured_comment'
                ] and
                'Version' in r.annotations['structured_comment'][
                    'antiSMASH-Data'
                ]
            ):
                self.aSver = r.annotations['structured_comment'][
                    'antiSMASH-Data'
                ]['Version']
                logger.info(' aS marker in structured comment aS v{}'.format(
                    self.aSver
                ))
            # MiBiG
            if (
                'comment' in r.annotations and
                r.annotations['comment'].startswith('MIBiG')
            ):
                self.aSver = '4.?.?'
                logger.info(
                    ' MiBIG marker, assuming aS v{}'.format(self.aSver)
                )
            if self.aSver != original_tag:
                return

            # last ditch detection of antismash, scan features for traces
            # of aS annotation
            for f in r.features:
                if hasattr(f, 'qualifiers') and 'aSTool' in f.qualifiers:
                    self.aSver = '4.?.?'
                    logger.info('  aSTool marker, assuming aS  v{}'.format(
                        self.aSver
                    ))
                    break
                if self.aSver != original_tag:
                    return


class EvocGB(WrappedGB):
    # evocdb specific fields
    origin = None
    gb_id = None
    taxon_id = None
    taxon = EvocTaxon()

    # taxonomy
    _organism = None
    _taxonomy = None
    _clusters = None
    _cds = None
    _domains = None

    # hack for MiBIG - where molecule is known, and one cluser per gb file
    _molecule_name = None

    def __init__(self, **items):
        super().__init__(**items)
        t_start = timeit.default_timer()
        if 'filename' in items:
            self.filename = items['filename']
        if 'gb_id' in items:
            self.gb_id = items['gb_id']
        if 'taxon_id' in items:
            self.taxon_id = items['taxon_id']
        if 'prefix' in items:
            self.prefix = items['prefix']
        if 'origin' in items:
            self.origin = items['origin']
        self._update()  # evocdb specific
        t_end = timeit.default_timer()
        logger.info('EvocGB loaded: {0:.2f} s'.format(t_end - t_start))

    def __str__(self):
        return '(gb: {0})\t(tax_id: {1})\t(prefix: {2})\n'.format(
            self.gb_id, self.taxon_id, self.prefix,
        ) + '=' * 80 + '\n' + '{0}'.format(
            '\n'  # .join(self._gb_text.split('\n')[:8])
        )

    def _update(self):
        # _update is responsible for filling out the gb object using
        # potentially incomplete data provided in the constructor
        #   1) if the database connection and an id is available, retreive from
        #      the db
        #   2) if a filename is available, make it new from the filename
        #   3) if only a compressed string is available, unpack it and build
        logger.info('updating GB...')
        if self.origin is not None and self.gb_id is not None:
            # only update for known gb_id since prefix is non-unique
            result = check_gb(
                self.origin.connection, gb_id=self.gb_id,
            )
            logger.info('from db {}'.format(self.origin))
            if result is not None and len(result) > 0:
                if self.gb_id != result[0][0]:
                    self.gb_id = result[0][0]
                    logger.info('  found gb_id {}'.format(self.gb_id))
                if self.taxon_id != result[0][1]:
                    self.taxon_id = result[0][1]
                    logger.info('  found taxon_id {}'.format(self.taxon_id))
                if self.prefix != result[0][2]:
                    self.prefix = result[0][2]
                    logger.info('  found prefix {}'.format(self.prefix_id))
                if self.gbz != result[0][3]:
                    self.gbz = result[0][3]
                    self.records = pickle.loads(gzip.decompress(self.gbz))
                    logger.info('found previously stored gbz {} bytes'.format(
                        len(self.gbz)
                    ))
            else:
                logger.info('gb_id {} not found'.format(self.gb_id))
                self.gb_id = None
        else:
            self.prefix = self.assembly

    def _load_records(self):
        t_start = timeit.default_timer()
        assert self.gbz is not None
        self.records = pickle.loads(gzip.decompress(self.gbz))
        t_end = timeit.default_timer()
        logger.info('load records {0:.2f} s'.format(t_end - t_start))

    def _load_taxonomy(self, add=True):
        t_start = timeit.default_timer()
        if (
            self._organism is None or self._taxonomy is None or
            self.strain is None
        ):
            logger.info('  adding taxonomy from gb...')

            taxonomy = []
            if (
                hasattr(self.records[0], 'annotations') and
                'taxonomy' in self.records[0].annotations
            ):
                taxonomy = self.records[0].annotations['taxonomy']
            self._taxonomy = taxonomy
            self._organism = '{} {}'.format(self.lname, self.strain)

        self.taxon = EvocTaxon(
            origin=self.origin,
            taxonomy_items=(self._organism, self._taxonomy, list(self.strain))
        )
        t_end = timeit.default_timer()
        logger.info('completed in {0:.2f} s'.format(t_end - t_start))
        buff = ""
        for i, t in enumerate(self._taxonomy + [self._organism]):
            buff += '{0}{1}\n'.format(i * "  ", t)
        logger.info(buff)

    def _derive_clusters_genes(self):
        if self.records is None:
            self._load_records()

        t_start = timeit.default_timer()
        self._clusters = []
        self._cds = []

        for i, r in enumerate(self.records):
            # hack for getting molecule
            if self.prefix.startswith('BGC'):
                self._molecule_name = r.description.replace(
                    'biosynthetic', ''
                ).replace('gene', '').replace('cluster', '').strip()
                logger.info(
                    'record codes for production of {}'.format(
                        self._molecule_name
                    )
                )

            if self.aSver.startswith('4'):
                BGC_set = [f for f in r.features if f.type == 'cluster']
            elif self.aSver.startswith('5'):
                BGC_set = [f for f in r.features if f.type == 'region']

            for j, c in enumerate(BGC_set):
                cloc = c.location
                c.makes = None
                if self._molecule_name is not None:
                    c.makes = self._molecule_name
                else:
                    c.makes = 'unknown_molecule'
                if cloc.strand == '-':
                    exit('holy shit, cluster on reverse strand')
                if c not in self._clusters:
                    self._clusters.append(c)

                cluster_features = [
                    f for f in r.features if f.type == 'CDS' if (
                        cloc.start <= f.location.start <= cloc.end or
                        cloc.start <= f.location.end <= cloc.end
                    )
                ]
                for f in cluster_features:
                    f.gb_index = i
                    if not hasattr(f, 'clusters'):
                        f.clusters = []
                    # Strange, some MiBIG genbank format files contain more
                    # than one cluster, and a CDS may be part of more than one
                    # cluster. Tracking this
                    # revision - all cds features should be considered part of
                    # a single cluster
                    if self._clusters.index(c) not in f.clusters:
                        f.clusters.append(self._clusters.index(c))
                    if self.prefix.startswith('BGC'):
                        f.clusters = [0]
                    # This is primarily to deal with inconsistent annotation
                    # between our in-house genomes and MiBIG or files from
                    # antismashDB. Cannot proceed without an identifier
                    # locus_tag > gene > protein_id > product
                    f.identifier = None
                    if 'product' in f.qualifiers:
                        f.product = f.qualifiers['product'][0]
                        f.identifier = f.product
                    if 'protein_id' in f.qualifiers:
                        f.protein_id = f.qualifiers['protein_id'][0]
                        f.identifier = f.protein_id
                    if 'gene' in f.qualifiers:
                        f.gene = f.qualifiers['gene'][0]
                        f.identifier = f.gene
                    if 'function' in f.qualifiers:
                        f.function = f.qualifiers['function'][0]
                    if 'locus_tag' in f.qualifiers:
                        f.locus_tag = f.qualifiers['locus_tag'][0]
                        f.identifier = f.locus_tag
                    assert f.identifier is not None, str(f)
                    if f not in self._cds:
                        self._cds.append(f)
        if self.prefix.startswith('BGC'):
            self._clusters = self._clusters[:1]
        t_end = timeit.default_timer()
        logger.info(
            '  Scanned {0} records \t{1} clusters \t{2} cds in {3:.2f} s'
            ''.format(
                len(self.records), len(self._clusters),
                len(self._cds), (t_end - t_start)
            )
        )

    def _derive_gene_domains(self):
        t_start = timeit.default_timer()
        assert (
            self.origin is not None and self._cds is not None
        )
        self._domains = []
        for i, cds_feature in enumerate(self._cds):
            self._domains.append({
                'cds_i': i,
                'start': 0,
                'end': len(cds_feature.qualifiers['translation'][0]),
                'type': ('{0}_{1}'.format(
                    self.prefix, cds_feature.identifier
                ), 'the whole domain')
            })
            sm_domain_list = []
            if self.aSver.startswith('4'):
                if 'sec_met' in cds_feature.qualifiers:
                    for q in cds_feature.qualifiers['sec_met']:
                        if q.startswith('NRPS/PKS Domain:'):
                            items = q.split(' ')
                            sm_name = items[2]
                            site = items[3].strip('.()').split('-')
                            sm_start = int(site[0])
                            sm_end = int(site[1])
                            sm_domain_list.append(
                                (sm_name, sm_start, sm_end, q)
                            )
            elif self.aSver.startswith('5'):
                if 'NRPS_PKS' in cds_feature.qualifiers:
                    for q in cds_feature.qualifiers['NRPS_PKS']:
                        if 'aSDomain' in q:
                            items = q.split(' ')
                            sm_name = items[1]
                            site = items[2].strip('.()').split('-')
                            sm_start = int(site[0])
                            sm_end = int(site[1])
                            sm_domain_list.append(
                                (sm_name, sm_start, sm_end, q)
                            )
            sm_domain_list = sorted(sm_domain_list, key=lambda x: x[1])
            d_start = 0
            d_end = len(cds_feature.qualifiers['translation'][0])
            if len(sm_domain_list) > 0:
                dlist = [(d_start, d_end, None, None)]
                for d in sm_domain_list:
                    if (dlist[-1][0] < d[1] <= dlist[-1][1]):
                        dlist[-1] = (
                            dlist[-1][0], d[1], dlist[-1][2], dlist[-1][3]
                        )
                        dlist.append((d[1], d[2], d[0], d[3]))
                    elif d[1] > dlist[-1][1]:
                        dlist.append((dlist[-1][1], d[1], None, None))
                        dlist.append((d[1], d[2], d[0], d[3]))
                if dlist[-1][1] < d_end:
                    if d_end - dlist[-1][1] > 0:
                        dlist.append((dlist[-1][1], d_end, None, None))
                assert len(dlist) >= len(sm_domain_list), (
                    dlist, sm_domain_list, str(self)
                )
            else:
                dlist = []
            self._cds[i]._domains = dlist
        t_end = timeit.default_timer()
        logger.info('domains {0:.2f}s'.format(t_end - t_start))

    def _add_clusters_genes_domains(self):
        if self._clusters is None or self._cds is None:
            self._derive_clusters_genes()
        if self._domains is None:
            self._derive_gene_domains()
        count = 0
        for c in self._cds:
            count += len(c._domains)
        logger.info('domain count: {}'.format(count))
        t_start = timeit.default_timer()

        assert self.origin is not None

        types_to_add = []
        rels_to_add = []
        clusters_to_add = []
        clusters_genes = []
        molecules_to_add = []
        genes_to_add = []
        domains_to_add = []

        for i, c in enumerate(self._clusters):
            cluster_type = 'unknown'
            if 'product' in c.qualifiers:
                cluster_type = c.qualifiers['product'][0]
            cluster_name = "{0}_c{1}".format(self.prefix, i)
            cluster_description = '{0} from {1}'.format(
                cluster_type, self.prefix
            )
            self._clusters[i].name = cluster_name
            types_to_add.append((cluster_name, cluster_description))
            clusters_to_add.append((cluster_name,))
            if c.makes is not 'unknown_molecule':
                types_to_add.append((c.makes, 'from MIBiG'))
                rels_to_add.append((c.makes, 'molecule', 'is_a'))
            molecules_to_add.append((cluster_name, c.makes))

        # genes
        for cds_i, cds in enumerate(self._cds):
            cds.nuc_id = self.records[cds.gb_index].id
            temp_location = []
            if isinstance(cds.location, SeqFeature.FeatureLocation):
                temp_location.append(
                    (cds.location.strand, cds.location.start, cds.location.end)
                )
            elif isinstance(cds.location, SeqFeature.CompoundLocation):
                for part in cds.location.parts:
                    temp_location.append((part.strand, part.start, part.end))
            cds.uniquename = '{0}-{1}_{2}'.format(
                self.gb_id, cds_i, cds.identifier
            )
            cds._seq = cds.qualifiers['translation'][0]
            genes_to_add.append((
                cds.uniquename, self.gb_id, cds.uniquename, cds.identifier,
                cds.nuc_id, encode_gene_location(temp_location),
                cds._seq, int(cds.location.start), int(cds.location.end)
            ))
            for c_i in cds.clusters:
                clusters_genes.append((
                    self._clusters[c_i].name, cds.uniquename
                ))
            types_to_add.append((cds.uniquename, 'no description'))
            rels_to_add.append((
                cds.uniquename, self.origin.default_gene_type.name, 'is_a'
            ))

            # domains - whole domain
            domain_name = '{0}_{1}_whole_domain'.format(
                self.gb_id, cds.identifier
            )
            types_to_add.append((domain_name, 'the whole domain'))

            SMCOG_type = None
            if self.aSver.startswith('4'):
                if 'note' in cds.qualifiers:
                    for item in cds.qualifiers['note']:
                        if item.startswith('smCOG:'):
                            item = item.split(' ')[1].split(':')
                            SMCOG_type = (item[0], item[1])
                            break
            elif self.aSver.startswith('5'):
                if 'gene_functions' in cds.qualifiers:
                    for item in cds.qualifiers['gene_functions']:
                        if 'SMCOG' in item:
                            smcog_i = item.find('SMCOG')
                            smcog_j = item.find('(Score:')
                            item = item[smcog_i:smcog_j].split(':')
                            SMCOG_type = (
                                item[0],
                                ' '.join(item[1].strip().split(' '))
                            )
                            break
            if SMCOG_type is not None:
                types_to_add.append(SMCOG_type)
                rels_to_add.append((
                    SMCOG_type[0],
                    self.origin.default_whole_domain_type.name, 'is_a'
                ))
                rels_to_add.append((domain_name, SMCOG_type[0], 'is_a'))
            else:
                rels_to_add.append((
                    domain_name, self.origin.default_whole_domain_type.name,
                    'is_a'
                ))
            domains_to_add.append((
                cds.uniquename, domain_name, 0, len(cds._seq)
            ))
            # # Part 2) sub_domains
            basic_fill_type = self.origin.basic_fill_type
            asdt = self.origin.default_aS_domain_type
            for d_i, d in enumerate(cds._domains):
                # make the type
                description = 'no description'
                if d[2] is None:
                    if d_i == 0:
                        type_name = 'NtermFill'
                    elif d_i + 1 == len(cds._domains):
                        type_name = 'CtermFill'
                    else:
                        type_name = '{0}_{1}_Fill'.format(
                            cds._domains[d_i - 1][2], cds._domains[d_i + 1][2]
                        )
                    parent_type_name = basic_fill_type.name
                else:
                    type_name = d[2]
                    parent_type_name = asdt.name
                    if type_name == 'AMP-binding':
                        prediction = 'no_call (unknown)'
                        if self.aSver.startswith('4'):
                            for item in d[3].split(';'):
                                if 'specificity' in item:
                                    for m in item.split(':')[-1].split(','):
                                        if 'SANDPUMA' in m:
                                            prediction = m.strip()
                                            break
                        elif self.aSver.startswith('5'):
                            # massive kludge ugly as sin
                            asd_parts = d[3].split(' ')
                            for p in d[3].split(' '):
                                if 'nrpspksdomains' in p:
                                    target_d = p
                                    break
                            aSDomains = [
                                f for f in self.records[cds.gb_index].features if
                                f.type == 'aSDomain'
                            ]
                            for f in aSDomains:
                                if (
                                    'domain_id' in f.qualifiers and
                                    f.qualifiers['domain_id'][0] == target_d and
                                    'specificity' in f.qualifiers
                                ):
                                    prediction = f.qualifiers['specificity'][0].split(':')[1]
                        description = prediction
                types_to_add.append((
                    type_name, description
                ))
                rels_to_add.append((type_name, parent_type_name, 'is_a'))
                domain_type_name = '{0}_{1}-{2}'.format(
                    cds.uniquename, d_i, type_name
                )
                types_to_add.append((
                    domain_type_name,
                    description
                ))
                rels_to_add.append((domain_type_name, type_name, 'is_a'))
                domains_to_add.append((
                    cds.uniquename, domain_type_name, d[0], d[1]
                ))

        cur = self.origin.connection.cursor()
        add_type_cmd = """
            INSERT OR IGNORE INTO type (name, description) VALUES(?, ?)
        """
        cur.executemany(add_type_cmd, types_to_add)
        types_to_add.append(('unknown_gene', ''))
        types_to_add.append(('is_a', ''))
        types_to_add.append(('whole_domain', ''))
        types_to_add.append(('Fill_domain', ''))
        types_to_add.append(('aS_domain', ''))
        types_to_add.append(('unknown_molecule', ''))
        types_to_add.append(('molecule', ''))
        tdict = {}
        for t in types_to_add:
            tresult = check_type(self.origin.connection, name=t[0])
            if t[0] not in tdict:
                tdict[t[0]] = tresult[0][0]
        t_end = timeit.default_timer()
        logger.info('--types ({0:.2f} s)'.format(t_end - t_start))

        rels_to_add = [
            (tdict[r[0]], tdict[r[1]], tdict[r[2]]) for r in rels_to_add
        ]
        rels_cmd = """
            INSERT OR IGNORE INTO type_relationship
                (subject_id, object_id ,type_id) VALUES (?, ?, ?)
        """
        cur.executemany(rels_cmd, (rels_to_add))
        t_end = timeit.default_timer()
        logger.info('--rels ({0:.2f} s)'.format(t_end - t_start))

        cluster_cmd = """
            INSERT INTO cluster (type_id) SELECT type.type_id FROM type
            WHERE type.name = ?
        """
        clusters_to_add = [(tdict[r[0]],) for r in clusters_to_add]
        cluster_cmd = """ INSERT OR IGNORE INTO cluster (type_id) VALUES(?)"""
        cur.executemany(cluster_cmd, clusters_to_add)

        cluster_rel_cmd = """
            INSERT OR IGNORE INTO type_relationship
                (subject_id, object_id, type_id) VALUES (?, ?, ?)
        """
        cluster_rels_to_add = [
            (
                r[0],
                self.origin.default_cluster.type_id,
                self.origin.is_a.type_id
            ) for r in clusters_to_add
        ]
        cur.executemany(cluster_rel_cmd, cluster_rels_to_add)
        t_end = timeit.default_timer()
        logger.info('--clusters ({0:.2f} s)'.format(t_end - t_start))

        # print(cur.rowcount)
        cdict = {}
        for c in clusters_to_add:
            result = check_cluster(
                connection=self.origin.connection, type_id=c[0]
            )
            cdict[c[0]] = result[0][0]

        molecules_to_add = [
            (cdict[tdict[r[0]]], tdict[r[1]]) for r in molecules_to_add
        ]
        molecule_cmd = """
            INSERT INTO molecule (cluster_id , type_id) VALUES (?, ?)
        """
        cur.executemany(molecule_cmd, molecules_to_add)
        t_end = timeit.default_timer()
        logger.info('--molecules ({0:.2f} s)'.format(t_end - t_start))

        genes_to_add = [
            (tdict[r[0]], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8])
            for r in genes_to_add
        ]
        genes_cmd = """
            INSERT INTO gene (type_id, gb_id, uniquename, pro_id, nuc_id,
                location, seq, start, end) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.executemany(genes_cmd, genes_to_add)
        t_end = timeit.default_timer()
        logger.info('--genes ({0:.2} s)'.format(t_end - t_start))

        # last_gene = check_gene(
        #     connection=self.origin.connection, type_id=genes_to_add[-1][0]
        # )
        last_gene = cur.execute("SELECT count(*) FROM gene").fetchone()[0]
        first_gene = last_gene - len(genes_to_add)
        gdict = {}
        new_clusters_genes = []
        for i, g in enumerate(clusters_genes):
            new_clusters_genes.append(
                (cdict[tdict[g[0]]], i + first_gene + 1)
            )
            gdict[tdict[g[1]]] = i + first_gene + 1
        # result = check_gene(
        #     connection=self.origin.connection, gb_id=self.gb_id
        # )
        # for r in result:
        #     gdict[r[3]] = r[0]
        # clusters_genes = [
        #     (cdict[tdict[r[0]]], gdict[tdict[r[1]]]) for r in clusters_genes
        # ]
        # for i in range(len(clusters_genes)):
        #     print(clusters_genes[i], new_clusters_genes[i])
        clusters_genes_cmd = """
            INSERT INTO cluster_gene (cluster_id, gene_id) VALUES(?, ?)
        """
        cur.executemany(clusters_genes_cmd, new_clusters_genes)
        t_end = timeit.default_timer()
        logger.info('--cluster_gene ({0:.2f} s)'.format(t_end - t_start))

        domains_to_add = [
            (gdict[tdict[r[0]]], tdict[r[1]], r[2], r[3])
            for r in domains_to_add
        ]
        domains_cmd = """
            INSERT INTO domain (source_gene_id, type_id, start, end)
            VALUES(?, ?, ?, ?)
        """
        cur.connection.executemany(domains_cmd, domains_to_add)
        t_end = timeit.default_timer()
        logger.info('--domains ({0:.2f} s)'.format(t_end - t_start))

        total_rows = len(
            types_to_add + rels_to_add + domains_to_add + clusters_to_add +
            molecules_to_add + genes_to_add + clusters_genes
        )

        t_end = timeit.default_timer()
        elapsed = t_end - t_start
        if len(self._cds) > 0:
            logger.info('completed in {0:.2f}s ({1:.2f} rows/s)'.format(
                elapsed, (total_rows / elapsed)
            ))

    def add(self, origin=None):
        """Attempt to add the records
            -requires a taxonomy item to be available
            -then derive the stuff from the records (genes, domains, clusters)
        """

        t_start = timeit.default_timer()
        logger.info('Adding gb with prefix {0}'.format(self.prefix))
        if origin is not None:
            self.origin = origin

        # taxonomy
        assert self.records is not None
        if self.taxon_id is None:
            self._load_taxonomy()
        assert self.taxon is not None

        if self.gb_id is None:
            lastid = add_gb(
                connection=self.origin.connection,
                taxon_id=self.taxon.taxon_id,
                prefix=self.prefix,
                loc=self.filename,
                # gb=self.gbz
            )
            assert lastid
            self.gb_id = lastid  # ugly because prefix is non-unique now

            logger.info('added gb_id {}'.format(self.gb_id))

            self._add_clusters_genes_domains()
        t_end = timeit.default_timer()
        logger.info('add: {0:.2f} s\n\n'.format(t_end - t_start))


class EvocCluster:
    origin = None
    cluster_id = None
    type_id = None
    type_item = EvocType()

    def __init__(self, **items):
        if 'origin' in items:
            self.origin = items['origin']
        if 'cluster_id' in items:
            self.cluster_id = items['cluster_id']
        if 'type_id' in items:
            self.type_id = items['type_id']
        self._update()

    def __str__(self):
        return "C{0} - {1}".format(
            self.cluster_id, self.type_item.name
        )

    def _update(self):
        if self.origin is not None:
            result = check_cluster(
                connection=self.origin.connection,
                cluster_id=self.cluster_id,
                type_id=self.type_id
            )
            if len(result) > 0:
                self.cluster_id = result[0][0]
                self.type_id = result[0][1]
            self.type_item = EvocType(
                origin=self.origin, type_id=self.type_id
            )

    def add(self, origin=None):
        if origin is not None:
            self.origin = origin
        assert self.origin is not None
        assert self.type_id is not None
        if self.cluster_id is None:
            assert add_cluster(
                connection=self.origin.connection,
                type_id=self.type_id
            )
            self._update()

    def add_child(self, origin=None, description=None):
        if origin is not None:
            self.origin = origin
        assert self.origin is not None
        assert self.type_id is not None
        assert self.cluster_id is not None

        new_cluster_type = self.type_item._inc_child(description=description)
        assert new_cluster_type.type_id is not None
        new_cluster = EvocCluster(
            origin=self.origin, type_id=new_cluster_type.type_id
        )
        if new_cluster.cluster_id is None:
            new_cluster.add()
        return new_cluster


class EvocGene:
    origin = None
    gene_id = None
    uniquename = None
    gb_id = None
    type_id = None
    pro_id = None
    nuc_id = None
    location = None
    seq = None
    start = None
    end = None
    type_item = EvocType()
    _f = None
    _aSDomains = None

    def __init__(self, **items):
        if 'origin' in items:
            self.origin = items['origin']
        if 'gene_id' in items:
            self.gene_id = items['gene_id']
        if 'uniquename' in items:
            self.uniquename = items['uniquename']
        if 'gb_id' in items:
            self.gb_id = items['gb_id']
        if 'type_id' in items:
            self.type_id = items['type_id']
        if 'pro_id' in items:
            self.pro_id = items['pro_id']
        if 'nuc_id' in items:
            self.nuc_id = items['nuc_id']
        if 'location' in items:
            self.location = items['location']
        if 'seq' in items:
            self.seq = items['seq']
        if 'start' in items:
            self.start = items['start']
        if 'end' in items:
            self.end = items['end']
        self._derive_uniquename()
        self._update()

    def __str__(self):
        return "From: {0}\tgb_id:{1}\nGene: {2}\t\tuniquename: {3}\n".format(
            self.origin.dbfile, self.gb_id, self.gene_id, self.uniquename
        ) + "type: ({0}) {1}\n".format(self.type_id, self.type_item.name) +\
            "pro_id: {0}\tnuc_id:{1}\t".format(self.pro_id, self.nuc_id) +\
            "location:{0}\t{1}-{2}\n{3}\n".format(
                self.location, self.start, self.end, self.seq
        )

    def _update(self):
        if self.origin is not None:
            result = check_gene(
                connection=self.origin.connection,
                gene_id=self.gene_id,
                uniquename=self.uniquename,
                gb_id=self.gb_id,
                type_id=self.type_id,
                pro_id=self.pro_id,
                nuc_id=self.nuc_id,
                location=self.location,
                seq=self.seq,
                start=self.start,
                end=self.end
            )
            if len(result) > 0:
                if result[0][0] != self.gene_id:
                    self.gene_id = result[0][0]
                if result[0][1] != self.uniquename:
                    self.uniquename = result[0][1]
                if result[0][2] != self.gb_id:
                    self.gb_id = result[0][2]
                if result[0][3] != self.type_id:
                    self.type_id = result[0][3]
                if result[0][4] != self.pro_id:
                    self.pro_id = result[0][4]
                if result[0][5] != self.nuc_id:
                    self.nuc_id = result[0][5]
                if result[0][6] != self.location:
                    self.location = result[0][6]
                if result[0][7] != self.seq:
                    self.seq = result[0][7]
                if result[0][8] != self.start:
                    self.start = result[0][8]
                if result[0][9] != self.end:
                    self.end = result[0][9]
            else:
                self.gene_id = None
            self._derive_uniquename()
            if self.type_id is not None:
                self.type_item = EvocType(
                    origin=self.origin, type_id=self.type_id
                )

    def _derive_uniquename(self):
        if (self.origin is not None and self.gb_id is not None):
            gb = EvocGB(origin=self.origin, gb_id=self.gb_id)
            self.uniquename = '{0}-{1}'.format(
                gb.gb_id, self.pro_id
            )

    def add(self, origin=None):
        if origin is not None:
            self.origin = origin
        assert self.gb_id is not None
        if self.uniquename is None:
            self._derive_uniquename()
        assert self.type_id is not None
        if self.gene_id is None:
            assert add_gene(
                connection=self.origin.connection,
                uniquename=self.uniquename,
                gb_id=self.gb_id,
                type_id=self.type_id,
                pro_id=self.pro_id,
                nuc_id=self.nuc_id,
                location=self.location,
                seq=self.seq,
                start=self.start,
                end=self.end
            ), str(self)
            self._update()


class EvocDomain:
    origin = None
    domain_id = None
    source_gene_id = None
    type_id = None
    start = None
    end = None
    _subseq = None

    def __init__(self, **items):
        if 'origin' in items:
            self.origin = items['origin']
        if 'domain_id' in items:
            self.domain_id = items['domain_id']
        if 'source_gene_id' in items:
            self.source_gene_id = items['source_gene_id']
        if 'type_id' in items:
            self.type_id = items['type_id']
        if 'start' in items:
            self.start = items['start']
        if 'end' in items:
            self.end = items['end']
        self._update()

    def _update(self):
        if self.origin is not None:
            result = check_domain(
                connection=self.origin.connection,
                domain_id=self.domain_id,
                source_gene_id=self.source_gene_id,
                type_id=self.type_id,
                start=self.start,
                end=self.end
            )
            if len(result) > 0:
                if result[0][0] != self.domain_id:
                    self.domain_id = result[0][0]
                if result[0][1] != self.source_gene_id:
                    self.source_gene_id = result[0][1]
                if result[0][2] != self.type_id:
                    self.type_id = result[0][2]
                if result[0][3] != self.start:
                    self.start = result[0][3]
                if result[0][4] != self.end:
                    self.end = result[0][4]
            else:
                self.domain_id = None

    def add(self, origin=None):
        if origin is not None:
            self.origin = origin
        assert self.source_gene_id is not None
        assert self.type_id is not None
        if self.domain_id is None:
            assert add_domain(
                connection=self.origin.connection,
                source_gene_id=self.source_gene_id,
                type_id=self.type_id,
                start=self.start,
                end=self.end
            )
        self._update()


class EvocMolecule:
    origin = None
    molecule_id = None
    type_id = None
    cluster_id = None
    type_item = None

    def __init__(self, **items):
        if 'origin' in items:
            self.origin = items['origin']
        if 'molecule_id' in items:
            self.molecule_id = items['molecule_id']
        if 'type_id' in items:
            self.type_id = items['type_id']
        if 'cluster_id' in items:
            self.cluster_id = items['cluster_id']
        self._update()

    def __str__(self):
        return "mol ({0}) - {1} made by cluster {2}".format(
            self.molecule_id, self.type_id, self.cluster_id
        )

    def _update(self):
        if self.origin is not None:
            result = check_molecule(
                connection=self.origin.connection,
                molecule_id=self.molecule_id,
                type_id=self.type_id,
                cluster_id=self.cluster_id
            )
            if len(result) > 0:
                if result[0][0] != self.molecule_id:
                    self.molecule_id = result[0][0]
                if result[0][1] != self.type_id:
                    self.type_id = result[0][1]
                if result[0][2] != self.cluster_id:
                    self.cluster_id = result[0][2]
            else:
                self.molecule_id = None

    def add(self, origin=None):
        if origin is not None:
            self.origin = origin
        assert self.origin is not None
        assert self.cluster_id is not None
        assert self.type_id is not None
        if self.molecule_id is None:
            assert add_molecule(
                connection=self.origin.connection,
                type_id=self.type_id,
                cluster_id=self.cluster_id
            )
        self._update()
