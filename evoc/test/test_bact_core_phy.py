import os
from evoc import db, bact_core_phy

import unittest
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises


class Test_bact_core_phy:
    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls.dbname = 'testdb.sqlite3'
        cls.connection = db.init_db(cls.dbname)

        cls.test_dir = os.path.dirname(__file__)

        cls.model_list = bact_core_phy.HMMERmodel_list()

        cls.gbfile1 = os.path.join(cls.test_dir, '01_genome_A40926.gbk')
        cls.gbfile2 = os.path.join(cls.test_dir, '02_genome_A47934.gbk')
        cls.fafile1 = os.path.join(cls.test_dir, '01_genome_A40926.fa')
        cls.fafile2 = os.path.join(cls.test_dir, '02_genome_A47934.fa')

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        cls.connection.close()
        try:
            os.remove(cls.dbname)
        except Exception:
            pass

    def test_01_model_parsing(self):
        """test model parsing"""
        assert_not_equal(self.model_list, None)

    def test_02_genome_extraction(self):
        """parse genome as source"""
        self.source1 = bact_core_phy.HMMERsource(
            self.gbfile1, self.model_list[1:10]
        )
        assert_equal(
            self.source1.parsed_reference,
            ('file', os.path.abspath(self.gbfile1), None, None)
        )

    # def test_03(self):
    #     """test load gbk"""
    #     source1 = bact_core_phy.HMMERsource(
    #         self.gbfile1, self.model_list[1:10]
    #     )

