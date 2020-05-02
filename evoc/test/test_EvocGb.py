import os
import evoc
import pickle
from evoc.evocdb import EvocDb
from evoc.evocdbitem import EvocGB, WrappedGB
from nose.tools import assert_equal, assert_raises


class Test_EvocGB:
    # dbname = 'testdb.sqlite3'
    dbname = ':memory:'

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """ Create a test db for this suite of tests"""
        cls.evocdb = EvocDb(cls.dbname)
        cls.mod_path = os.path.dirname(evoc.__file__)
        cls.test_path = os.path.join(cls.mod_path, 'test')
        cls.test_file = os.path.join(cls.test_path, '03_test.gbk.gz')
        cls.test_file2 = os.path.join(cls.test_path, '01_genome_A47934.gbk')

    @classmethod
    def teardown_class(cls):
        """ Remove tempdb file when test suite is completed"""
        if os.path.exists(cls.dbname):
            os.remove(cls.dbname)

    def test_01_wrapped_gb(self):

        # blank
        WrappedGB('')
        # also blank
        WrappedGB()

        # bad string
        text = b'ABCDEFG'
        assert_raises(OSError, WrappedGB, text)

    def test_01_blank_EvocGB(self):
        """ Creating blank EvocGB"""
        EvocGB()

    def test_02_new_EvocGB_from_MIBIG14(self):
        """ gb from MIBIG 1.4 - unkown antismash, assume v4.?
            Note the accession number from the filename is different from the
            accession in the gbfile
        """
        test_file = os.path.join(
            self.test_path, "test_mibig_BGC0001789.1.gbk.gz"
        )
        test_gb = EvocGB(
            origin=self.evocdb,
            filename=test_file
        )
        assert_equal(test_gb.assembly, 'BGC0001790.1')  # note the number
        # check taxon
        assert_equal(test_gb.lname, 'Pseudomonas acidophila')
        assert_equal(test_gb.strain, 'ATCC 31363')
        # check annotation information
        assert_equal(test_gb.refseq, False)
        assert_equal(test_gb.genbank, False)
        assert_equal(test_gb.aSver, '4.?.?')

        test_gb.add()
        assert_equal(test_gb.gb_id, 1)

    def test_03_new_EvocGB_from_MIBIG20(self):
        """ gb from MIBIG 2.0 - antismash v5"""
        test_file = os.path.join(self.test_path, "test_BGC0001317.1.gbk.gz")
        test_gb = EvocGB(
            origin=self.evocdb,
            filename=test_file
        )
        assert_equal(test_gb.assembly, 'BGC0001317.1')
        # check taxon
        assert_equal(test_gb.lname, 'Lotus japonicus')
        assert_equal(test_gb.strain, 'unknown_strain')
        # check annotation information
        assert_equal(test_gb.refseq, False)
        assert_equal(test_gb.genbank, False)
        assert_equal(test_gb.aSver, '5.1.0-0c1c90d(changed)')

        test_gb.add()
        assert_equal(test_gb.gb_id, 2)

    def test_04_new_EvocGB_from_asdb(self):
        """ gb from file - antismash v4"""
        test_file = os.path.join(
            self.test_path, "test_asdb_GCF_000331185.1.gbk.gz"
        )
        test_gb = EvocGB(
            origin=self.evocdb,
            filename=test_file
        )
        assert_equal(test_gb.assembly, 'GCF_000331185.1')
        # check taxon
        assert_equal(test_gb.lname, 'Streptomyces rimosus subsp. rimosus')
        assert_equal(test_gb.strain, 'ATCC 10970')
        # check annotation information
        assert_equal(test_gb.refseq, False)
        assert_equal(test_gb.genbank, True)
        assert_equal(test_gb.aSver, '4.?.?')

        test_gb.add()
        assert_equal(test_gb.gb_id, 3)

    def test_05_new_EvocGB_from_WAC(self):
        """ gb from WAC antismash 5"""
        test_file = os.path.join(self.test_path, "test_WAC-AA000297.gbk.gz")
        test_gb = EvocGB(
            origin=self.evocdb,
            filename=test_file
        )
        assert_equal(test_gb.assembly, 'AA000297')
        # check taxon
        assert_equal(test_gb.lname, 'unidentified')
        assert_equal(test_gb.strain, 'unknown_strain')
        # check annotation information
        assert_equal(test_gb.refseq, False)
        assert_equal(test_gb.genbank, False)
        assert_equal(test_gb.aSver, '5.0.0')        

        test_gb.add()
        assert_equal(test_gb.gb_id, 4)

    def test_06_from_gbz(self):
        test_file = os.path.join(self.test_path, "03_test.gbk.gz")
        test_gbz = WrappedGB(test_file)
        test_gb = EvocGB(
            origin=self.evocdb,
            gbz=test_gbz.dumpz
        )
        assert_equal(test_gb.assembly, 'GCF_900312975.1')
        test_gb.add()

    # def test_07(self):
    #     self.evocdb.backup_db('dump.sql')
