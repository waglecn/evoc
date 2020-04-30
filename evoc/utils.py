import sys
import os

from evoc import db
from evoc.utils_tree import *
from evoc.utils_reconciliation import *


def read_relationship_tsv(tsv_file, types=None, relationships=None):
    """open a relationship tsv file, return list of types and relationshps"""

    sections = ['# types', '# relationships']

    if types is None:
        types = []
    if relationships is None:
        relationships = []

    # print(types, relationships)
    with open(tsv_file, 'r') as infile:
        section = None
        lineno = 0
        for line in infile.readlines():
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


def translate_anchor(connection, type_anchor):
    """translate cvterm_id or name for a type anchor"""

    ob_id = None
    ob_name = None
    ob_result = db.check_type(connection, name=type_anchor)

    if ob_result:
        ob_id = ob_result[0][0]
        ob_name = ob_result[0][1]
    ob_result = db.check_type(connection, type_id=type_anchor)
    if ob_result:
        ob_id = ob_result[0][0]
        ob_name = ob_result[0][1]
    if ob_id is not None and ob_name is not None:
        return (ob_id, ob_name)
    else:
        return False


def get_mfa(dbname, type_anchor, stdout=False):

    connection = db.init_db(dbname)

    cur = connection.cursor()

    # ob_id = None
    # ob_name = None
    result = translate_anchor(connection, type_anchor)
    if result is not False:
        ob_id = result[0]
        # ob_name = result[1]
    else:
        return result

    # recursively check children
    ob_stack = [ob_id]
    ob_checked = []
    while len(ob_stack) > 0:
        new_ob_stack = []
        for ob in ob_stack:
            ob_checked.append(str(ob))
            rels = db.check_relationship(connection, object_id=ob)
            if rels is not False and len(rels) > 0:
                for r in rels:
                    if r[2] not in ob_checked:
                        new_ob_stack.append(r[2])
        ob_stack = new_ob_stack
        del(new_ob_stack)

    overall_results = []
    for object_id in ob_checked:
        # print('retrieving {0}'.format(object_id))
        cmd = """
            SELECT gene.uniquename,
                type.name,
                domain.domain_id,
                domain.start,
                domain.end,
                gene.seq
            FROM type_relationship
            JOIN type
                ON type.type_id = type_relationship.subject_id
            JOIN domain
                ON type.type_id = domain.type_id
            JOIN gene ON gene.gene_id = domain.source_gene_id
            WHERE type_relationship.object_id = ?
        """
        # cmd = """
        #     SELECT gene.uniquename,
        #         type.name,
        #         domain.domain_id,
        #         domain.start,
        #         domain.end,
        #         gene.seq
        #     FROM gene
        #     JOIN domain
        #         ON domain.source_gene_id = gene.gene_id
        #     JOIN type
        #         ON domain.type_id = type.type_id
        #     WHERE type.type_id = ?
        # """
        results = cur.execute(cmd, (object_id,)).fetchall()
        if len(results) > 0:
            for r in results:
                overall_results.append(r)

    out = ""
    sep = '|'
    for r in overall_results:
        # new coordinates
        uniquename = r[0]
        typename = r[1]
        start = r[3]
        end = r[4]
        seq = r[5]
        assert len(r[5]) > 0, exit('seq {0} MISSING!!!!'.format(uniquename))
        new = seq[r[3]:r[4]]
        temp = uniquename.split('-')
        head = '-'.join(temp[0:-1]) + sep + temp[-1][0:6]
        output = '>{0}{6}{1}-{2}{6}{3}{6}{4}\n{5}\n'.format(
            head,
            start,
            end,
            r[2],
            typename,
            new, sep
        )
        out += output

    if stdout:
        print(out)
    return out


def convert_afa_to_phy(infile, outfile=None):
    """utility to convert a fasta alignment to phylip format via Biopython"""
    from Bio import AlignIO

    try:
        alignment = AlignIO.read(infile, 'fasta')   # read the alignment
        in_time = os.path.getmtime(infile)  # get input file time
    except Exception as e:
        print('Caught: {0}'.format(str(e)))
        sys.exit()

    # under what conditions do we update the output file?
    if outfile is not None:  # file output is requested
        if os.path.exists(outfile):
            out_time = os.path.getmtime(outfile)
            if in_time < out_time:
                print(
                    'skipping fa2phylip conversion: output is older than input'
                )
                return alignment

    AlignIO.write(alignment, outfile, format='phylip-relaxed')
    print('Converted: {0} to {1}'.format(infile, outfile))

    return alignment


def make_gene_table(genbank_record, start=None, end=None, prefix=None):
    """make an editable gene_table from a genbank file for manual curation"""
    # get basic record information
    nuc_id = genbank_record.id.split('.')[0]

    fhead, ftail = os.path.split(genbank_record._original_filename)
    prefix = '.'.join(ftail.split('.')[0:-1])
    ftail = ftail.split('.')[0]

    r_start = 0
    r_end = len(genbank_record)
    if start is not None:
        r_start = start
    if end is not None:
        r_end = end

    nuc_gi = -1
    date = ''
    # organism = ''

    for annotation in genbank_record.annotations:
        if annotation == 'gi':
            nuc_gi = int(genbank_record.annotations['gi'])
        if annotation == 'date':
            date = genbank_record.annotations['date']

    # slicing the record can leave out features that don't occur entirely in
    # the slice
    features = [
        f for f in genbank_record.features if f.type == 'CDS' and
        ((f.location.start > r_start and f.location.start <= r_end) or
            (f.location.end >= r_start and f.location.end <= r_end))
    ]

    cds = []
    for feature in features:
        cds.append(process_cds(feature))
    for item in cds:
        item['uniquename'] = '{0}-{1}'.format(
            prefix,
            hashlib.md5(item['translation'].encode('utf-8')).hexdigest()
        )
    gene_table = {
        'nuc_id': nuc_id,
        'nuc_gi': nuc_gi,
        'record_start': r_start,
        'record_end': r_end,
        'cds': cds,
        'date': date
    }
    return gene_table


def process_taxon(connection, record, type_name=None):
    """
    The purpose of this function is to produce taxonomic information for later
    comparing and loading. Requiring the following:
        Organism name: can be found in the record annotations itself
        Organism Taxonomy: can be found the record annoations
        Strain name: for some reason, found in the feature qualifiers of the
            source feature of the record.


    For some reason, biopython only notices the taxonomy field when there are
    at least two items in the list.

    Example 1:
      ORGANISM  Paenibacillus apiarius
                Bacteria; Firmicutes; Bacilli; Bacillales; Paenibacillaceaea;
                Paenibacillus.

    Output:
        {organism: 'Paenibacillus apiarius', 'taxonomy': ['Bacteria',
            'Firmicutes', 'Bacilli', 'Bacillales', 'Paenibacillaceaea','
            'Paenibacillus']}

    Example 2:
      ORGANISM  Paenibacillus apiarius
                Bacteria.

    Output:
        {organism: 'Paenibacillus apiarius', 'taxonomy': []}

    """

    # setup Defaults
    organism = ''
    taxonomy = []
    strain = ['']

    # try:
    organism = record.annotations['source']
    taxonomy = record.annotations['taxonomy']
    for f in record.features:
        if (
            f.type == 'source' and
            hasattr(f, 'qualifiers') and
            'strain' in f.qualifiers
        ):
            strain = f.qualifiers['strain']
            break

    organism = (organism + ' ' + ' '.join(strain)).strip()

    # This catches aS gb files with no organism
    if organism == '':
        org_index = 0
        # propose organism name
        propose = 'unknown_org_{0}'.format(org_index)
        result = db.check_type(connection, name=propose)
        while not len(result) == 0:
            org_index += 1
            propose = 'unknown_org_{0}'.format(org_index)
            result = db.check_type(connection, name=propose)
        organism = propose

    if len(taxonomy) == 0:
        taxonomy = ['unknown_org']

    lineage = taxonomy + [organism]

    # step 3, get taxon types and relationships
    taxon_types = []
    for item in lineage:
        taxon_types.append((item, 'Unknown'))
    taxon_rels = []
    for step in range(1, len(taxon_types)):
        taxon_rels.append(
            (taxon_types[step][0], taxon_types[step - 1][0], 'is_a')
        )

    return organism, taxon_types, taxon_rels


def load_processed_taxon(connection, organism, taxon_types, taxon_rels):
    """load processed taxon data"""
    # base_organism = db.check_type(connection, name='organism')

    # add the basic organism to the base of the taxonomy branch
    taxon_rels = [(taxon_rels[0][1], 'organism', 'is_a')] + taxon_rels

    for t in taxon_types:
        result = db.check_type(connection, name=t[0])
        if len(result) == 0:
            db.add_type(connection, name=t[0], description=t[1])
    for r in taxon_rels:
        type_id = db.check_type(connection, name=r[2])[0][0]
        parent = db.check_type(connection, name=r[1])[0][0]
        child = db.check_type(connection, name=r[0])[0][0]
        if not db.check_relationship(
            connection, subject_id=child, object_id=parent, type_id=type_id
        ):
            assert db.add_relationship(
                connection, subject_id=child, object_id=parent, type_id=type_id
            )

    # need to add taxonomy item
    taxon_type = db.check_type(connection, name=organism)
    assert len(taxon_type) > 0
    taxon_item = db.check_taxon(
        connection, type_id=taxon_type[0][0]
    )
    if len(taxon_item) == 0:
        # add taxon
        result = db.add_taxon(
            connection,
            type_id=taxon_type[0][0],
        )
        assert result is True
        print('added taxon: {0}'.format(organism))
    else:
        print('known taxon: {0}'.format(organism))

    return True


def process_record_set(connection, filenames, infer_taxon=False, prefix=None):
    """process a set of gb filenames"""
    from Bio import SeqIO

    if len(filenames) == 0:
        exit('Need at least one record to process')

    records = []
    print('Processing:')
    for f in filenames:
        print("\t{0}".format(f))
        block = [r for r in SeqIO.parse(f, 'gb')]
        for b in block:
            # add original filename
            b._original_filename = f
        records += block

    fhead, ftail = os.path.split(filenames[0])
    if prefix is None:
        prefix = '.'.join(ftail.split('.')[0:-1])

    try:
        # basic taxon information
        organism_info, org_types, org_rels = process_taxon(
            connection, records[0]
        )
        print(organism_info, org_types, org_rels)
        assert load_processed_taxon(
            connection, organism_info, org_types, org_rels
        ), exit('Could not load taxon')

        # default parent cds type
        default_gene_item = db.check_type(connection, name='unknown_gene')
        assert len(default_gene_item) > 0, 'cannot find default gene type'

        # default is_a relationship
        isa_item = db.check_type(connection, name='is_a')
        assert len(isa_item) > 0, 'cannot find default is_a type'
        isa_type_id = isa_item[0][0]

        # default cluster type
        unknown_cluster_type = db.check_type(
            connection, name='unknown_cluster'
        )
        unknown_cluster_type_id = unknown_cluster_type[0][0]

        cluster_counter = 0
        proposed_cluster = 'unknown_cluster_{0}'.format(cluster_counter)

        while len(db.check_type(connection, name=proposed_cluster)) > 0:
            cluster_counter += 1
            proposed_cluster = 'unknown_cluster_{0}'.format(cluster_counter)
        result = db.add_type(
            connection, name=proposed_cluster, description=proposed_cluster
        )

        proposed_cluster_item = db.check_type(
            connection, name=proposed_cluster
        )
        prop_cluster_type_id = proposed_cluster_item[0][0]
        cluster_result = db.check_cluster(
            connection, type_id=prop_cluster_type_id
        )
        if cluster_result == []:
            db.add_cluster(
                connection,
                type_id=prop_cluster_type_id
            )
            cluster_result = db.check_cluster(
                connection, type_id=prop_cluster_type_id
            )
        new_cluster_id = cluster_result[0][0]

        rel_result = db.check_relationship(
            connection,
            subject_id=prop_cluster_type_id,
            object_id=unknown_cluster_type_id,
            type_id=isa_type_id
        )
        if len(rel_result) == 0:
            db.add_relationship(
                connection,
                subject_id=prop_cluster_type_id,
                object_id=unknown_cluster_type_id,
                type_id=isa_type_id
            )

        # process gb records
        for i, r_i in enumerate(records):
            gene_table = make_gene_table(r_i)

            # LOAD
            # step 1, to load gb need:
            #   taxon_id
            #   prefix - from filename?
            taxon_type = db.check_type(connection, name=organism_info)
            assert len(taxon_type) > 0, 'No taxon found for type: {0}'.format(
                organism_info
            )
            taxon_item = db.check_taxon(connection, type_id=taxon_type[0][0])
            taxon_id = taxon_item[0][0]

            gb_txt = open(r_i._original_filename, 'r').read()
            result = db.add_gb(
                connection, taxon_id=taxon_id, prefix=prefix, gb=gb_txt
            )
            assert result is True, 'adding gb failed'

            gb_result = db.check_gb(connection, gb=gb_txt)
            assert gb_result, 'cannot find gb'
            gb_id = gb_result[0][0]

            print('gb_id added is {0}'.format(gb_id))

            # load gene table and cds
            unknown_gene_count = 0

            unknown_gene_type = default_gene_item
            assert len(unknown_gene_type) > 0
            unknown_gene_type = unknown_gene_type[0]
            unknown_gene_type_id = unknown_gene_type[0]

            for g in gene_table['cds']:
                # propose new gene name
                proposed_gene_name = 'unknown_gene_{0}'.format(
                    unknown_gene_count
                )
                proposed_gene_type_item = db.check_type(
                    connection, name=proposed_gene_name
                )

                while len(proposed_gene_type_item) > 0:
                    unknown_gene_count += 1
                    proposed_gene_name = 'unknown_gene_{0}'.format(
                        unknown_gene_count
                    )
                    proposed_gene_type_item = db.check_type(
                        connection, name=proposed_gene_name
                    )
                assert len(proposed_gene_type_item) == 0
                result = db.add_type(
                    connection,
                    name=proposed_gene_name,
                    description=proposed_gene_name
                )
                assert result is True

                gene_type_item = db.check_type(
                    connection, name=proposed_gene_name
                )
                assert gene_type_item is not [], 'cannot find gene_type_id'
                gene_type_id = gene_type_item[0][0]

                # link gene type to basic gene_type
                cds_rel_item = db.check_relationship(
                    connection,
                    subject_id=gene_type_id,
                    object_id=unknown_gene_type_id,
                    type_id=isa_type_id
                )

                added_cds_rel_item = False
                if len(cds_rel_item) == 0:
                    # add rel
                    added_cds_rel_item = db.add_relationship(
                        connection,
                        subject_id=gene_type_id,
                        object_id=unknown_gene_type_id,
                        type_id=isa_type_id
                    )
                    assert added_cds_rel_item is not False, 'not added'
                else:
                    added_cds_rel_item = cds_rel_item
                assert added_cds_rel_item is not False, (
                    'no type added for item: {0}'.format(
                        (gene_type_id, unknown_gene_type_id, isa_type_id)
                    )
                )

                # load gene
                g['start'] = int(g['start'])
                g['end'] = int(g['end'])

                # if g['start'] > g['end']:
                #     strand = -1
                # else:
                #     strand = 1
                strand = g['strand']
                location = encode_gene_location(
                    [
                        strand,
                        min([g['start'], g['end']]),
                        max([g['start'], g['end']])
                    ]
                )
                gene_result = db.add_gene(
                    connection,
                    uniquename=g['uniquename'],
                    description='',
                    location=location,
                    pro_gi=g['pro_gi'],
                    pro_id=g['pro_id'],
                    nuc_gi=gene_table['nuc_gi'],
                    nuc_id=gene_table['nuc_id'],
                    seq=g['translation'],
                    start=g['start'],
                    end=g['end'],
                    gb_id=gb_id,
                    type_id=gene_type_id
                )
                assert gene_result is True, (
                    'adding gene failed'
                    ' {0} {1}'.format(g['nuc_gi'], type(g['nuc_gi']))
                )
                gene_object = db.check_gene(
                    connection, type_id=gene_type_id
                )
                # add cluster
                db.add_cluster_gene(
                    connection,
                    cluster_id=new_cluster_id,
                    gene_id=gene_object[0][0]
                )

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exit('failed: {0} {1} line {2}'.format(
            str(e),
            exc_tb.tb_frame.f_code.co_filename,
            exc_tb.tb_lineno
        ))


def process_cds(f):
    try:
        new_cds = {}
        new_cds['start'] = int(f.location.start)
        new_cds['end'] = int(f.location.end)
        new_cds['product'] = []
        new_cds['translation'] = ''
        new_cds['gene'] = ''
        new_cds['pro_gi'] = -1
        new_cds['pro_id'] = ''
        new_cds['strand'] = f.strand

        # print(f.qualifiers)

        for q in f.qualifiers:
            # product annotation, order is random! caused failing test
            if q == 'product' and len(f.qualifiers[q]) > 0:
                new_cds['product'].append(f.qualifiers['product'][0])
            # note annotation
            if q == 'note' and len(f.qualifiers[q]) > 0:
                new_cds['product'].append(f.qualifiers['note'][0])
            # protein sequence
            if q == 'translation' and len(f.qualifiers[q]) > 0:
                new_cds['translation'] = f.qualifiers['translation'][0]
            # gene annotation
            if q == 'gene' and len(f.qualifiers[q]) > 0:
                new_cds['gene'] = f.qualifiers['gene'][0]
            # protein gi
            if q == 'db_xref' and len(f.qualifiers[q]) > 0:
                new_cds['pro_gi'] = int(
                    f.qualifiers['db_xref'][0].split(':')[1]
                )
            # protein accession
            if q == 'protein_id' and len(f.qualifiers[q]) > 0:
                new_cds['pro_id'] = f.qualifiers['protein_id'][0]
        new_cds['product'] = ', '.join(sorted(new_cds['product']))
        return new_cds

    except Exception as e:
        exc_type, exc_object, tb = sys.exc_info()
        frame = tb.tb_frame
        print(repr(e), tb.tb_lineno, frame.f_code.co_filename)
        return False


def make_default_domains_from_gene_list(connection, gene_list):
    """create new whole domains using a gene list from db"""
    try:
        assert len(gene_list) > 0, 'gene list empty'

        for g in gene_list:
            # parent gb, prefix
            parent_gb = db.check_gb(connection, g[3])
            assert parent_gb is not False
            prefix = parent_gb[0][4]

            name = '{0}-{1}_whole'.format(prefix, g[0])
            description = '{0} domain'.format(name)
            # need type_id
            type_result = db.check_type(
                connection, name=name, description=description
            )
            if len(type_result) == 0:
                assert db.add_type(
                    connection, name=name, description=description
                ), 'cannot add new type "{0}"'.formate(name)
            type_item = db.check_type(
                connection, name=name, description=description
            )
            type_id = type_item[0][0]

            # need to add basic domain type
            basic_domain = 'unknown_domain'
            domain_result = db.check_type(connection, name=basic_domain)
            assert len(domain_result) > 0
            domain_type_id = domain_result[0][0]

            is_a_type = db.check_type(connection, name='is_a')
            assert len(domain_result) > 0
            is_a_type_id = is_a_type[0][0]

            void_result = db.add_relationship(
                connection,
                object_id=domain_type_id,
                subject_id=type_id,
                type_id=is_a_type_id
            )
            assert void_result is True

            # need domain info
            gene_len = len(g[10])
            domain_start = 0
            domain_end = gene_len

            # name
            # add a whole domain for each gene
            assert db.add_domain(
                connection,
                source_gene_id=g[0],
                type_id=type_id,
                description=description,
                start=domain_start,
                end=domain_end
            ), 'cannot add domain {0}:{1}-{2}'.format(
                g[0], domain_start, domain_end
            )
        return True

    except Exception as e:
        print('Error with Input: {0}'.format(str(e)))
        return False


def make_default_aS_domains_from_gb(connection, gb_id):
    """Function to build domain list from an antiSMASH gb file"""
    target_domains = {
        'Epimerization': 'E',
        'PCP': 'PCP',
        'AMP-binding': 'A',
        'Condensation': 'Cond',
        'Thioesterase': 'TE',
        'X': 'X',
        'NRPS-COM_Nterm': 'NRPS-COM_Nterm',
        'NRPS-COM_Cterm': 'NRPS-COM_Cterm',
        'ECH': 'ECH',
        'Fill_domain': 'Fill_domain'
    }
    # make aSDomain type
    aS_type_target = add_child_to_type(
        connection, 'domain', 'aSDomain', 'a domain from aS'
    )
    for t in target_domains:
        add_child_to_type(
            connection, 'aSDomain', t, 'an aSDomain {0}'.format(t)
        )
    try:
        gene_list = db.check_gene(connection, gb_id=gb_id)
        assert len(gene_list) > 0, 'emtpy gene list'

        # need to read domains from aS gb string
        from io import StringIO
        from Bio import SeqIO
        gb_text = db.check_gb(connection, gb_id=gb_id)[0][-1]
        gb_handle = StringIO(gb_text)
        record = SeqIO.read(gb_handle, 'genbank')
        # iterate through domains:
        features = [f for f in record.features if f.type == 'aSDomain']
        count = 1
        domains = {}
        for f in features:
            gtargets = [g for g in gene_list if (
                f.location.start >= g[-2] and f.location.end <= g[-1]
            )]
            print('found {0} targets'.format(len(gtargets)))
            assert len(gtargets) > 0, exit('big problem')
            target_g_id = gtargets[0][0]
            target_description = 'unknown domain in g_id {0}'.format(
                target_g_id
            )
            target_location = decode_gene_location(gtargets[0][-4])
            target_strand = target_location[0]
            if target_strand == -1:
                target_start = (gtargets[0][-1] - f.location.end) // 3
                target_end = (gtargets[0][-1] - f.location.start) // 3
                target_length = (gtargets[0][-1] - gtargets[0][-2]) // 3
            else:
                target_start = (f.location.start - gtargets[0][-2]) // 3
                target_end = (f.location.end - gtargets[0][-2]) // 3
                target_length = (gtargets[0][-1] - gtargets[0][-2]) // 3
            target_type = f.qualifiers['domain'][0]
            target_name = 'shit'
            if target_type == 'AMP-binding':
                for item in f.qualifiers['specificity']:
                    if item.startswith('consensus') or \
                        item.startswith('SANDPUMA ensemble'):
                        target_name = 'Item{0}-A_{1}'.format(
                            count,
                            item.split(':')[-1].strip()
                        )
                        count += 1
            else:
                # better way for this
                if target_type in target_domains:
                    target_name = 'Item{0}-{1}'.format(
                        count,
                        target_domains[target_type]
                    )
                    count += 1
                else:
                    target_domains[target_type] = target_type
                    target_name = '{0}'.format(target_type)
            assert target_name != 'shit', 'shitty'
            assert target_start >= 0 and target_start <= target_length
            assert target_end >= 0 and target_end <= target_length
            if target_g_id not in domains:
                domains[target_g_id] = []
            domains[target_g_id].append((
                target_start,
                target_end,
                target_length,
                target_type,
                target_name,
                target_description
            ))
        # backfill domains
        for g in domains:
            sorted_ds = sorted(domains[g], key=lambda d: d[0])
            new_ds = []
            for i, d in enumerate(sorted_ds):
                if i == 0:
                    if d[0] > 0:
                        # make NtermFill domain
                        new_ds.append((
                            0,
                            d[0] - 1,
                            d[2],
                            'NtermFill',
                            'NtermFill',
                            'NtermFill'
                        ))
                    new_ds.append(d)
                else:
                    # check for non-overlapping domains
                    prev_d = new_ds[-1]
                    # case 1: new d doesn't overlap with old d
                    if d[0] > prev_d[1]:
                        new_ds.append((
                            prev_d[1] + 1,
                            d[0] - 1,
                            d[2],
                            '{0}-{1}_Fill'.format(prev_d[3], d[3]),
                            '{0}-{1}_Fill'.format(prev_d[4], d[4]),
                            '{0}-{1}_Fill'.format(prev_d[4], d[4])
                        ))
                        new_ds.append(d)
                    # case 2: new d start < old d end
                    elif d[0] < prev_d[1] and d[0] > prev_d[0]:
                        new_ds.append((
                            prev_d[1] + 1,
                            d[0] - 1,
                            d[2],
                            '{0}-{1}_Fill'.format(prev_d[3], d[3]),
                            '{0}-{1}_Fill'.format(prev_d[4], d[4]),
                            '{0}-{1}_Fill'.format(prev_d[4], d[4])
                        ))
                        new_ds.append(d)
                    # case 3: old d fits entirely inside new d, shared start
                    elif d[0] == prev_d[0] and d[1] >= prev_d[1]:
                        new_ds[-1] = d
                        new_ds.append(d)
                    # case 4: new d fits entirely inside old d
                    elif d[0] == prev_d[0] and d[1] <= prev_d[1]:
                        # keep the old_d
                        pass

            # handle last domain
            prev_d = new_ds[-1]
            if prev_d[1] < prev_d[2]:
                new_ds.append((
                    prev_d[1] + 1,
                    prev_d[2],
                    prev_d[2],
                    'CtermFill',
                    'CtermFill',
                    'CtermFill'
                ))
            domains[g] = new_ds

        # add domains
        generic_domain_type_result = db.check_type(
            connection, name='unknown_domain'
        )
        assert generic_domain_type_result is not False
        generic_domain_type_id = generic_domain_type_result[0][0]
        is_a_item = db.check_type(connection, name='is_a')
        assert is_a_item is not False
        isa_id = is_a_item[0][0]

        for source_gene_id in domains:
            # get gb prefix
            gene_item = db.check_gene(connection, gene_id=source_gene_id)
            parent_gb = db.check_gb(connection, gb_id=gene_item[0][3])
            assert parent_gb is not False
            prefix = parent_gb[0][4]

            dlist = domains[source_gene_id]
            for domain in dlist:
                # check domain type
                # initialize
                count = 0
                proposed_name = '{0}-{1}-{2}_{3}'.format(
                    prefix, source_gene_id, domain[4], count
                )
                proposed_description = '{0} {1} {2}'.format(
                    domain[4], domain[5], count
                )
                dt_result = db.check_type(
                    connection,
                    name=proposed_name,
                    description=proposed_description
                )
                # check type
                # print('proposed name: {0}'.format(proposed_name))
                while len(dt_result) > 0:
                    # update proposal
                    count += 1
                    proposed_name = '{0}-{1}-{2}_{3}'.format(
                        prefix, source_gene_id, domain[4], count
                    )
                    proposed_description = '{0} {1} {2}'.format(
                        domain[4], domain[5], count
                    )
                    dt_result = db.check_type(
                        connection,
                        name=proposed_name,
                        description=proposed_description
                    )
                    # print('proposed name: {0}'.format(proposed_name))

                # add it?
                assert db.add_type(
                    connection,
                    name=proposed_name,
                    description=proposed_description
                )
                # get answer
                dt_result = db.check_type(
                    connection,
                    name=proposed_name,
                    description=proposed_description
                )
                # print(domain)
                print('added: {0} is_a {1}'.format(proposed_name, domain[3]))
                # add relationship
                parent_target = None
                parent_target_id = None
                parent_target = db.check_type(connection, name=domain[3])
                if len(parent_target) == 0:
                    target_domains[domain[3]] = domain[3]
                    if domain[3].endswith('Fill'):
                        parent_target_id = add_child_to_type(
                            connection,
                            'Fill_domain',
                            domain[3],
                            domain[3]
                        )
                    else:
                        parent_target_id = add_child_to_type(
                            connection,
                            'aSDomain',
                            domain[3],
                            domain[3]
                        )
                    parent_target = db.check_type(connection, name=domain[3])
                parent_target_id = parent_target[0][0]
                # print('YY', parent_target_id)
                db.add_relationship(
                    connection,
                    subject_id=dt_result[0][0],
                    object_id=parent_target_id,
                    type_id=isa_id
                )
                # print('{0} is_a unknown_domain'.format(proposed_name))
                # actually add the domain
                add_result = db.add_domain(
                    connection,
                    source_gene_id=source_gene_id,
                    type_id=dt_result[0][0],
                    description=proposed_description,
                    start=domain[0],
                    end=domain[1]
                )
                assert add_result is True

    except AssertionError as e:
        print('Error making aS domains: {0}'.format(repr(e)))
        return False
    except Exception as e:
        import inspect
        import linecache
        print('Unknown error making aS domains: {0}'.format(repr(e)))
        exc_type, exc_object, tb = sys.exc_info()
        argvalues = inspect.getargvalues(tb.tb_frame)
        linecache.checkcache(tb.tb_frame.f_code.co_filename)
        line = linecache.getline(
            tb.tb_frame.f_code.co_filename,
            tb.tb_lineno,
            tb.tb_frame.f_globals
        )
        print(
            line, 'X', line, tb.tb_frame.f_code.co_filename,
            inspect.formatargvalues(*argvalues)
        )
        return False

    return True


def add_child_to_type(connection, type, child_name, child_description):
    """a utility function that adds a child term to a parent_type"""
    parent = db.check_type(connection, name=type)
    if parent == []:
        parent = db.check_type(connection, type_id=type)
    assert parent is not [], 'cannot find parent: {0}'.foramt(type)

    result = db.check_type(
        connection, name=child_name, description=child_description
    )
    if len(result) == 0:
        assert db.add_type(
            connection, name=child_name, description=child_description
        ), 'could not add: {0}: {1}'.format(child_name, child_description)
    result = db.check_type(
        connection, name=child_name, description=child_description
    )

    default_rel_type = db.check_type(connection, name='is_a')
    assert len(default_rel_type) > 0, 'cannot find "is_a" type'
    rel = db.check_relationship(
        connection,
        object_id=parent[0][0],
        subject_id=result[0][0],
        type_id=default_rel_type[0][0]
    )
    if len(rel) == 0:
        assert db.add_relationship(
            connection,
            object_id=parent[0][0],
            subject_id=result[0][0],
            type_id=default_rel_type[0][0]
        ), 'could not add {0} {1} {2}'.format(
            result[0], 'is_a', parent[0]
        )
    return result[0][0]


def increment_child_to_type(connection, type):
    """a utility function to add incremental type as child of a parent type
    i.e. unknown_gene -> unknown_gene_0, unknown_gene_1, unknown_gene_2, etc
    """
    parent = db.check_type(connection, name=type)
    if parent == []:
        parent = db.check_type(connection, type_id=type)
    assert parent is not [], 'cannot find parent: {0}'.foramt(type)

    count = 0
    proposed_name = '{0}_{1}'.format(parent[0][1], count)
    result = db.check_type(
        connection, name=proposed_name, description=proposed_name
    )
    while len(result) > 0:
       # update proposal
        count += 1
        proposed_name = '{0}_{1}'.format(parent[0][1], count)
        result = db.check_type(
            connection,
            name=proposed_name,
            description=proposed_name
        )
        print(proposed_name)
    assert db.add_type(
        connection,
        name=proposed_name,
        description=proposed_name
    ), 'could not add: {0}: {1}'.format(proposed_name, proposed_name)
    result = db.check_type(
        connection,
        name=proposed_name,
        description=proposed_name
    )
    default_rel_type = db.check_type(connection, name='is_a')
    assert len(default_rel_type) > 0, 'cannot find "is_a" type'
    rel = db.check_relationship(
        connection,
        object_id=parent[0][0],
        subject_id=result[0][0],
        type_id=default_rel_type[0][0]
    )
    if len(rel) == 0:
        assert db.add_relationship(
            connection,
            object_id=parent[0][0],
            subject_id=result[0][0],
            type_id=default_rel_type[0][0]
        ), 'could not add {0} {1} {2}'.format(
            result[0], 'is_a', parent[0]
        )
    return result[0]


def aS_sort_domains(connection):
    """utility function for grouping domains"""
    return False

# def get_fa(dbfile, term):
#     """utility function for getting one or  more sequences from the db"""
#     from evoc import db

#     assert os.path.exists(dbfile), exit('cannot find dbfile {0}'.format(
#         dbfile)
#     )
#     try:
#         connection = db.init_db(dbfile)
#         cur = connection.cursor()
#     except Exception as e:
#         print(str(e))

#     if term.isnumeric():
#         # print('is numeric')
#         cmd = """
#         SELECT gene.gene_id, gene.uniquename, gene.seq, type.type_id, type.name
#         FROM gene
#             JOIN domain ON gene.gene_id = domain.source_gene_id
#             JOIN type ON domain.type_id = type.type_id
#         WHERE type.type_id = ?
#         """
#         result = cur.execute(cmd, (term,)).fetchall()
#     else:
#         # print('is not numeric')
#         cmd = """
#         SELECT gene.gene_id, gene.uniquename, gene.seq, type.type_id, type.name
#         FROM gene
#             JOIN domain ON gene.gene_id = domain.source_gene_id
#             JOIN type ON domain.type_id = type.type_id
#         WHERE type.name = ? OR gene.uniquename GLOB ?
#         """
#         result = cur.execute(cmd, (term, term + '*')).fetchall()

#     gene_id = result[0][0]
#     uniquename = result[0][1]
#     seq = result[0][2]
#     type_id = result[0][3]
#     type_name = result[0][4]

#     return (gene_id, uniquename, seq, type_id, type_name)


# def write_pro_fasta(gbfile, outfile):
#     """write a protein fasta starting with a gb filename"""
#     from Bio import SeqIO
#     import os
#     import hashlib

#     fhead, ftail = os.path.split(gbfile)
#     ftail = ftail.split('.')[0]

#     try:
#         assert(os.path.exists(gbfile))
#         records = SeqIO.parse(gbfile, format='gb')
#         with open(outfile, 'w') as outhandle:
#             for r in records:
#                 for f in r.features:
#                     if (
#                         f.type == 'CDS'
#                     ):
#                         assert hasattr(f, 'qualifiers'), 'no qualifiers attr'
#                         assert 'translation' in f.qualifiers, 'no translation'
#                         fseq_hash = hashlib.md5(
#                             f.qualifiers['translation'][0].encode('utf-8')
#                         ).hexdigest()
#                         outhandle.write('>{0}\n{1}\n'.format(
#                             (
#                                 ftail + '-' + fseq_hash
#                             ),
#                             f.qualifiers['translation'][0]
#                         ))

#         return True
#     except AssertionError as e:
#         print(str(e), e.message)
#         exc_type, exc_object, tb = sys.exc_info()
#         frame = tb.tb_frame
#         print(repr(e), tb.tb_lineno, frame.f_code.co_filename)
#         return False
#     except Exception as e:
#         exc_type, exc_object, tb = sys.exc_info()
#         frame = tb.tb_frame
#         print(repr(e), tb.tb_lineno, frame.f_code.co_filename)
#         return False

# def make_gb_template(connection, gb_id=None, gb_nuc_id=None, gbfile=None):
#     """Make a gb template"""
#     from evoc import db
#     import os

#     gene_table = False
#     gb_result = False
#     # make gb_template
#     try:
#         if gb_id is not None:  # gb_id from database
#             gb_result = db.check_gb(connection, gb_id=gb_id)
#             assert(gb_result is not False)  # this better not be false
#             gb_id = gb_result[0][0]
#             gb_nuc_id = gb_result[0][1]
#             assert(os.path.exists('./data/' + gb_nuc_id + '.gb'))
#             gbfile = './data/' + gb_nuc_id + '.gb'
#             gene_table = make_gene_table(gbfile)
#         elif gb_nuc_id is not None:
#             gb_result = db.check_gb(connection, nuc_id=gb_nuc_id)
#             assert(os.path.exists('./data/' + gb_nuc_id + '.gb'))
#             gbfile = './data/' + gb_nuc_id + '.gb'
#             gene_table = make_gene_table(gbfile)
#             if gb_result is not False:
#                 gb_id = '<gb_id>'
#         elif gbfile is not None:
#             assert(os.path.exists(gbfile))
#             gb_result = False
#             gb_id = '<gb_id>'
#             gene_table = make_gene_table(gbfile)
#             gb_nuc_id = gene_table['nuc_id']
#         else:
#             print('Missing critical information needed to generate template')
#             return False
#         assert(gene_table is not False)
#         assert(write_pro_fasta(gbfile, gbfile + '.fa') is True)

#         if gb_result is not False:
#             # gb in database, at least
#             gb = {
#                 'gb_id': gb_result[0],
#                 'nuc_id': gb_result[1],
#                 'nuc_gi': int(gb_result[2]),
#                 'taxon_id': gb_result[3],
#                 'gb': gb_result[4],
#                 'gbfile': gbfile,
#                 'gene_table': gene_table
#             }
#         else:
#             # build from gbfile, assuming in data
#             gb = {
#                 'gb_id': '<gb_id>',
#                 'nuc_id': gene_table['nuc_id'],
#                 'nuc_gi': gene_table['nuc_gi'],
#                 'taxon_id': '<taxon_id>',
#                 'gb': '',
#                 'gbfile': gbfile,
#                 'gene_table': gene_table

#             }
#         return gb
#     except Exception as e:
#         exc_type, exc_object, tb = sys.exc_info()
#         frame = tb.tb_frame
#         print(repr(e), tb.tb_lineno, frame.f_code.co_filename)
#         return False


# def generate_antismash_gbfile_prots(gbfile):
#     """make basic antismash output from gbfile"""
#     import os
#     from subprocess import call
#     # ugly, only my machine

#     output_path = os.path.dirname(gbfile)
#     file_suffix = os.path.split(gbfile)[-1]
#     output_folder = os.path.join(output_path, file_suffix)
#     try:
#         cmd = [
#             '/usr/bin/python',  # important to find correct python version
#             '/home/nick/Downloads/antismash-3.0.5/run_antismash.py',
#             '--input-type=prot',
#             '--outputfolder=' + os.path.join(
#                 output_path, file_suffix + '.out', ''
#             ),
#             os.path.join(output_path, file_suffix)
#         ]
#         result = call(cmd)
#         assert(result == 0)
#         aS_file = output_folder + '.fa.out/Protein_Input.final.gp'
#         assert(os.path.exists(aS_file))
#         return aS_file
#     except Exception as e:
#         exc_type, exc_object, tb = sys.exc_info()
#         frame = tb.tb_frame
#         print(repr(e), tb.tb_lineno, frame.f_code.co_filename)
#         return False



# # def process_antismash_aSfile(aSfile):
# #     """generate domain table from antismash output"""
# #     from Bio import SeqIO
# #     try:
# #         records = SeqIO.read(aSfile, format='gb')
# #         domain_table = []
# #         return domain_table
# #     except Exception as e:
# #         exc_type, exc_object, tb = sys.exc_info()
# #         frame = tb.tb_frame
# #         print(repr(e), tb.tb_lineno, frame.f_code.co_filename)
# #         return False
