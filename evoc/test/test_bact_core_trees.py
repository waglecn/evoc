import os
from evoc import utils
from evoc import db
from evoc import bact_core_trees

import unittest
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises


class Test_bact_core_trees:
    dbname = 'testdb.sqlite3'

    def __init__(self):
        import os
        self.test_dir = os.path.dirname(__file__)
        self.mod_dir = os.path.dirname(utils.__file__)
        self.bact_core_hmm_dir = os.path.join(
            self.mod_dir, 'bact_core_tree_building', 'core_hmm'
        )

        self.gbfile1 = os.path.join(self.test_dir, '01_genome_A40926.gbk')
        self.gbfile2 = os.path.join(self.test_dir, '02_genome_A47934.gbk')
        self.fafile1 = os.path.join(self.test_dir, '01_genome_A40926.fa')
        self.fafile2 = os.path.join(self.test_dir, '02_genome_A47934.fa')

    @classmethod
    def setup_class(cls):
        cls.connection = db.init_db(cls.dbname)

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        cls.connection.close()
        try:
            os.remove(cls.dbname)
        except Exception:
            pass

    def test_01_filename_parsing(self):
        """test the name parsing functions"""
        name = bact_core_trees.parse_num_type_name(self.gbfile1)
        print(name)
        assert_equal(name[0], '01')
        assert_equal(name[1], 'genome')
        assert_equal(name[2], 'A40926')

        name = bact_core_trees.parse_default_name(self.gbfile1)
        assert_equal(name, '01_genome_A40926')

    def test_02_genome_extraction(self):
        """test the genome extraction function"""
        filelist = [self.gbfile1, self.gbfile2]
        result = bact_core_trees.extract_proteins(
            filelist,
            output_dir=self.test_dir
        )

        from Bio import SeqIO
        records = SeqIO.parse(self.gbfile1, 'gb')
        features = []
        for r in records:
            features += ([f for f in r.features if f.type == 'CDS'])

        assert_equal(len(filelist), len(result))
        pro_records = SeqIO.parse(result[0], 'fasta')
        proteins = [p for p in pro_records]
        assert_equal(len(features), len(proteins))
        for r in result:
            assert_equal(
                os.path.exists(r), True
            )

    def test_03_hmm_aln(self):
        """hmm alignment of a list(query gbk) against a database of hmms"""
        query_list = [
            '.'.join(self.gbfile1.split('.')[:-1]) + '.fa',
            '.'.join(self.gbfile2.split('.')[:-1]) + '.fa'
        ]

        hmm_list = [
            os.path.join(self.bact_core_hmm_dir, hmm) for hmm in os.listdir(
                self.bact_core_hmm_dir
            ) if hmm.endswith('.hmm')
        ]
        aligned_object = bact_core_trees.hmm_alignments(
            query_list, hmm_list[:15]
        )
        aligned_records = bact_core_trees.concat_alignments(aligned_object)
        # # build alignment
        import io
        from Bio import SeqIO
        aligned_records = SeqIO.parse(io.StringIO(aligned_records), 'fasta')
        aligned_records = [a for a in aligned_records]
        assert_equal(len(aligned_records), len(query_list))
        alignment_length = len(aligned_records[0])
        for a in aligned_records:
            assert_equal(len(a), alignment_length)


    def test_04_test_hmm_exlusion(self):
        """test excluding certain models from concatenated hmm familieis"""
        query_list = [
            '.'.join(self.gbfile1.split('.')[:-1]) + '.fa',
            '.'.join(self.gbfile2.split('.')[:-1]) + '.fa'
        ]

        hmm_list = [
            os.path.join(self.bact_core_hmm_dir, hmm) for hmm in os.listdir(
                self.bact_core_hmm_dir
            ) if hmm.endswith('.hmm')
        ]

        aligned_object = bact_core_trees.hmm_alignments(
            query_list, hmm_list[:15]
        )
        processed_models = [m for m in list(aligned_object.keys())]

        aligned_records_1 = bact_core_trees.concat_alignments(aligned_object)
        aligned_records_2 = bact_core_trees.concat_alignments(
            aligned_object, excluded_models=processed_models[0]
        )
        import io
        from Bio import SeqIO
        ar1 = [a for a in SeqIO.parse(io.StringIO(aligned_records_1), 'fasta')]
        ar2 = [a for a in SeqIO.parse(io.StringIO(aligned_records_2), 'fasta')]
        # the concatenated alignment with one less model ought to be shorter
        assert_equal(len(ar1[0]) > len(ar2[0]), True)

        for q in query_list:
            os.remove(q)
