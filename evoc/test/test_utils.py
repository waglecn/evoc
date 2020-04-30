from evoc import utils
from evoc import db

import unittest
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.plugins.skip import SkipTest


@SkipTest
class Test_utils:
    dbname = 'testdb.sqlite3'
    fasta = expected_result = (
        '>|unique|1-50|1|child\n'
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n'
        '>|unique|51-100|2|child\n'
        'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG\n'
    )

    def __init__(self):
        import os
        self.test_dir = os.path.dirname(__file__)
        self.rel_tsv_file = os.path.join(self.test_dir, 'test_types.tsv')
        self.basic_types_tsv_file = os.path.join(
            self.test_dir, '..', '..', 'basic_types.tsv'
        )
        self.test_gb_file = os.path.join(self.test_dir, 'test.gb')

        self.gbfile1 = os.path.join(self.test_dir, 'test.gb')
        self.gbfile2 = os.path.join(self.test_dir, 'test.gb')

        self.multi_gb1 = os.path.join(self.test_dir, 'test.m1.gb')
        self.multi_gb2 = os.path.join(self.test_dir, 'test.m2.gb')

        self.test_aSgb_file = os.path.join(self.test_dir, 'test.aS.gb')
        self.test_pro_fasta_file = os.path.join(
            self.test_dir, 'test.pro.fasta'
        )

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(cls.dbname)

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        cls.connection.close()
        import os
        try:
            os.remove(cls.dbname)
        except Exception:
            pass

    def test_01_read_relationship_tsv(self):
        """Load the example /tests/test_types.tsv"""
        rel_tsv_file = self.rel_tsv_file
        types, relationships = utils.read_relationship_tsv(rel_tsv_file)
        assert_equal(len(types), 6)
        assert_equal(len(relationships), 1)

        connection = self.connection
        types_tsv_file = self.rel_tsv_file
        types, relationships = utils.read_relationship_tsv(types_tsv_file)
        db.load_relationships(connection, types, relationships)

        basic_types_tsv_file = self.basic_types_tsv_file
        types, relationships = utils.read_relationship_tsv(
            basic_types_tsv_file
        )
        db.load_relationships(connection, types, relationships)

    def test_02a_gene_location(self):
        """test encoding good location"""
        location = [0, 0, 100]
        good_result = utils.encode_gene_location(location)
        assert_not_equal(good_result, False)

    def test_02b_gene_location(self):
        """test encoding bad location"""
        null_location = None
        bad_result = utils.encode_gene_location(null_location)
        assert_equal(bad_result, False)

    def test_02c_gene_location(self):
        """test decoding good location"""
        location = [0, 0, 100]
        good_result = utils.encode_gene_location(location)
        decoded = utils.decode_gene_location(good_result)
        assert_equal(decoded, location)

    def test_02d_gene_location(self):
        """test decoding bad location"""
        bad_decoded = utils.decode_gene_location('None')
        assert_equal(bad_decoded, False)

    def test_03_test_translate_anchor(self):
        """test the translate anchor function with anchor name and id"""
        result = utils.translate_anchor(self.connection, 'none')  # 1, none
        assert_equal(result, (1, 'none'))

        result = utils.translate_anchor(self.connection, 1)  # 1, none
        assert_equal(result, (1, 'none'))

    def test_04_test_mfa_bad_anchor(self):
        """test get_mfa with a bad anchor description"""
        result = utils.get_mfa(self.dbname, 'garbage')
        assert_equal(result, False)

    def test_05_test_mfa_stdout(self):
        """Check for fasta output from get_mfa"""
        connection = self.connection
        # prep, hacky add gene
        gresult = db.add_gene(
            connection,
            description='None',
            uniquename='uniquenameA',
            gb_id=1,
            type_id=1,
            location=utils.encode_gene_location([[1, 1, 300]]),
            seq='{0}{1}'.format(50 * 'A', 50 * 'G'),
            start=1,
            end=300
        )
        assert_equal(gresult, True)

        dresult1 = db.add_domain(
            connection,
            source_gene_id=1,
            type_id=3,
            description='',
            start=1,
            end=50
        )
        assert_equal(dresult1, True)

        dresult2 = db.add_domain(
            connection,
            source_gene_id=1,
            type_id=3,
            description='',
            start=51,
            end=100
        )
        assert_equal(dresult2, True)

        # reassign stdout
        import sys
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        except Exception as e:
            print('Caught: {0}'.format(str(e)))
        original_stdout = sys.stdout
        sys.stdout = StringIO()

        # execute the test
        result = utils.get_mfa(self.dbname, 2)
        stdout_result = utils.get_mfa(self.dbname, 2, stdout=True)

        assert_equal(result, self.fasta)
        assert_equal(stdout_result, self.fasta)

        # recover original stdout
        sys.stdout = original_stdout

    def test_06_test_process_taxon(self):
        """test taxon processing"""
        from Bio import SeqIO
        connection = self.connection

        record = SeqIO.read(self.test_gb_file, format='gb')
        o1, t1, r1 = utils.process_taxon(connection, record)
        assert_equal(o1, 'Paenibacillus apiarius PA-B2B')
        assert_equal(len(t1), 7)
        assert_equal(len(r1), 6)

        result = utils.load_processed_taxon(connection, o1, t1, r1)
        assert_equal(result, True)

        record = SeqIO.read(self.test_aSgb_file, format='gb')
        o2, t2, r2 = utils.process_taxon(connection, record)
        assert_equal(o2, 'unknown_org_0')

        result = utils.load_processed_taxon(connection, o1, t1, r1)
        assert_equal(result, True)

        result = utils.load_processed_taxon(connection, o2, t2, r2)
        assert_equal(result, True)

        record = SeqIO.read(self.test_aSgb_file, format='gb')
        o3, t3, r3 = utils.process_taxon(connection, record)
        assert_equal(o3, 'unknown_org_1')

        result = utils.load_processed_taxon(connection, o3, t3, r3)
        assert_equal(result, True)

    def test_07_new_record_set(self):
        """Test processing record set"""
        connection = self.connection
        base_gb = self.test_gb_file
        gb1_filename = self.multi_gb1
        gb2_filename = self.multi_gb2

        # alter the base gb file
        from Bio import SeqIO
        base = [r for r in SeqIO.parse(base_gb, format='gb')]
        # set strain
        for f in base[0].features:
            if f.type == 'source':
                f.qualifiers['strain'] = ['Unknown_strain']
        # set source and taxonomy
        base[0].annotations['source'] = 'test_organism1'
        base[0].annotations['taxonomy'] = ['Bacteria', 'unknown_org']
        base[0].annotations['original_filename'] = gb1_filename
        SeqIO.write(base[0], gb1_filename, format='gb')

        # repeat for second file
        base[0].annotations['source'] = 'test_organism2'
        base[0].annotations['taxonomy'] = ['Bacteria', 'unknown_org']
        base[0].annotations['original_filename'] = gb2_filename
        SeqIO.write(base[0], gb2_filename, format='gb')

        # define the record set
        record_set = [
            [gb1_filename],
            [gb2_filename]
        ]
        for records in record_set:
            utils.process_record_set(connection, records)

        # now to test
        genes = db.check_gene(connection)
        # 1 gene already loaded, an 2x9 gene gb files just loaded
        assert_equal(len(genes), 19)

    def test_08_record_process_partial(self):
        """Test processing a record with partial coordinates"""
        test_gb_file = self.test_gb_file
        gb3_filename = 'test.m3.gb'
        from Bio import SeqIO
        base = [r for r in SeqIO.parse(test_gb_file, format='gb')]
        for f in base[0].features:
            if f.type == 'source':
                f.qualifiers['strain'] = ['Unknown_strain']
        base[0].annotations['original_filename'] = gb3_filename
        base[0]._original_filename = gb3_filename

        gene_table = utils.make_gene_table(base[0], start=1, end=len(base[0]))
        assert_equal(len(gene_table), 6)

    def test_09_process_filename_set_error(self):
        """Test processing an empty filename set"""
        record_set = []
        with assert_raises(SystemExit):
            utils.process_record_set(self.connection, record_set)

    def test_10_populate_whole_domains(self):
        """Iterate through genes for a gb_id and add whole domains"""
        connection = self.connection
        gb_result = db.check_gb(connection)
        # print([g[0:-1] for g in gb_result])

        assert_not_equal(gb_result, [])
        target_gb_id = gb_result[0][0]

        genes = db.check_gene(connection, gb_id=target_gb_id)
        assert_not_equal(genes, False)
        result = utils.make_default_domains_from_gene_list(
            connection, genes
        )
        assert result

        domains = db.check_domain(connection)

        gene_ids = [g[0] for g in genes]
        domains = [d for d in domains if d[1] in gene_ids]
        assert_equal(len(domains), len(genes) + 2)

    def test_11_check_empty_gene_list(self):
        """Test making domains with an empty gene list"""
        connection = self.connection
        genes = []
        result = utils.make_default_domains_from_gene_list(
            connection, genes
        )
        assert not result

    def test_12_check_bad_gene_in_list(self):
        """Test making domains with an bad gene"""
        connection = self.connection
        target_gb_id = 2
        genes = db.check_gene(connection, gb_id=target_gb_id)
        # make the bad gene
        bad_gene = (
            'NULL',  # set source_gene_id to NULL, should be int
            genes[1][1],
            genes[1][2],
            genes[1][3],
            genes[1][4],
            genes[1][5],
            genes[1][6],
            genes[1][7],
            genes[1][8],
            genes[1][9],
            genes[1][10],
            genes[1][11],
            genes[1][12]
        )
        genes[1] = bad_gene
        result = utils.make_default_domains_from_gene_list(
            connection, genes
        )
        assert_equal(result, False)

    def test_13_test_process_aS_record(self):
        """Test processing an aS genbank record"""
        connection = self.connection
        gbfile = self.test_aSgb_file

        record_set = [
            [gbfile],
        ]
        for record in record_set:
            utils.process_record_set(connection, record)

        gb_items = db.check_gb(connection)
        gb_text = open(gbfile, 'r').read()
        for i, g in enumerate(gb_items):
            if gb_text == g[-1]:
                index_id = i

        gb_id = gb_items[index_id][0]

        genes = db.check_gene(connection, gb_id=gb_id)
        assert len(genes) > 0, 'no genes found for gb_id: {0}'.format(gb_id)

        result = utils.make_default_domains_from_gene_list(connection, genes)
        assert result, 'could not make domains'

        # now make aS domains
        result = utils.make_default_aS_domains_from_gb(connection, gb_id)
        assert_equal(result, True)

    # def test_07_write_pro_fasta(self):
    #     """Write a protein fasta file"""
    #     from Bio import SeqIO
    #     import os
    #     test_gb_file = self.test_gb_file
    #     outfile = self.test_pro_fasta_file
    #     result = utils.write_pro_fasta(test_gb_file, outfile)
    #     assert_not_equal(result, False)
    #     assert_equal(os.path.exists(self.test_pro_fasta_file), True)
    #     records = [record for record in SeqIO.parse(outfile, format='fasta')]
    #     assert_equal(len(records), 9)
    #     os.remove(outfile)

    # # def test_05a_gb_template_NCBI(self):
    # #     """Make a gb template from an NCBI gbfile"""
    # #     connection = self.connection
    # #     test_gb_file = self.test_gb_file
    # #     result_gb = utils.make_gb_template(connection, gbfile=test_gb_file)
    # #     # gb: gene_table, gbfile, nuc_id, gb_id, gb, nuc_gi, taxon_id
    # #     assert_equal(result_gb['gbfile'], test_gb_file)
    # #     assert_equal(result_gb['taxon_id'], '<taxon_id>')
    # #     assert_equal(result_gb['gb_id'], '<gb_id>')

    # # def test_05b_gb_template_aS(self):
    # #     """Make a gb template from an antismash gbfile"""
    # #     connection = self.connection
    # #     test_aSgb_file = self.test_aSgb_file
    # #     result_gb = utils.make_gb_template(connection, gbfile=test_aSgb_file)
    # #     # gb: gene_table, gbfile, nuc_id, gb_id, gb, nuc_gi, taxon_id
    # #     assert_equal(result_gb['gbfile'], test_aSgb_file)
    # #     assert_equal(result_gb['taxon_id'], '<taxon_id>')
    # #     assert_equal(result_gb['gb_id'], '<gb_id>')

    # # def test_06_taxon_template(self):
    # #     """Make a taxon template from gb_template"""
    # #     connection = self.connection
    # #     types_tsv_file = './data/types.tsv'
    # #     types_tsv_file = self.rel_tsv_file
    # #     types, relationships = utils.read_relationship_tsv(types_tsv_file)
    # #     db.load_relationships(connection, types, relationships)
    # #     test_gb_file = self.test_gb_file
    # #     result_gb = utils.make_gb_template(connection, gbfile=test_gb_file)
    # #     result_taxon = utils.make_taxon_template(connection, result_gb)
    # #     assert_equal(result_taxon['taxon_id'], '<taxon_id>')
    # #     assert_not_equal(result_taxon['type_id'], '<type_id>')

    # # @unittest.skip("Skipping Long Running Test")
    # # def test_07_test_aS(self):
    # #     """Generate basic aS on gbfile"""
    # #     test_gb_file = self.test_gb_file
    # #     outfile = self.test_pro_fasta_file
    # #     result = utils.write_pro_fasta(test_gb_file, outfile)
    # #     result = utils.generate_antismash_gbfile_prots(test_gb_file)
    # #     assert_not_equal(result, False)


    # # def test_10_process_record(self):
    # #     """test process_record function"""
    # #     connection = self.connection
    # #     gbfile1 = self.gbfile1
    # #     gbfile2 = self.gbfile2

    # #     record1 = utils.process_record(connection, gbfile1)
    # #     result = record1.store()
    # #     assert_equal(result, True)
