import os
from evoc import utils
from evoc import db

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.plugins.skip import SkipTest


# @SkipTest
class Test_aS_example:
    dbname = './examples/exampledb.sqlite3'

    def __init__(self):
        import os
        self.test_dir = os.path.dirname(__file__)
        self.example_dir = os.path.join(
            self.test_dir, '..', '..', 'examples'
        )
        self.basic_types_tsv_file = os.path.join(
            os.path.dirname(db.__file__), 'basic_types.tsv'
        )

        self.gb_records_dir = os.path.join(
            self.example_dir, 'gb_files'
        )

    @classmethod
    def setup_class(cls):
        if os.path.exists(cls.dbname):  # fresh each time
            os.remove(cls.dbname)
        cls.connection = db.init_db(
            cls.dbname
        )

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        cls.connection.close()

    def test_01_prep_db(self):
        """prepare the database"""
        connection = self.connection
        # dbfilename = self.dbname

        types, rels = utils.read_relationship_tsv(
            self.basic_types_tsv_file
        )
        result = db.load_relationships(connection, types, rels)
        assert_equal(result, True)

    @SkipTest
    def test_02_load_gb(self):
        """loads the example gb files from ./examples/gb_files folder"""
        gb_list = [
            ['AF386507.1.cluster001.gbk'],
            ['AJ632270.1.cluster001.gbk'],
            ['EU874253.1.cluster001.gbk'],
            ['KF192710.1.cluster001.gbk'],
            ['U82965.2.cluster001.gbk'],
            ['CP008953.1.cluster001.gbk'],
            ['HQ679900.1.cluster001.gbk'],
            ['KF882511.1.cluster001.gbk'],
            ['Y16952.3.cluster001.gbk'],
            ['AJ223998.1.cluster001.gbk', 'AJ223999.1.cluster001.gbk'],
            ['DQ403252.1.cluster001.gbk'],
            ['JX576190.1.cluster001.gbk'],
            ['KJ364518.1.cluster001.gbk'],
            ['AJ561198.1.cluster001.gbk'],
            ['EU874252.1.cluster001.gbk'],
            ['KC688274.1.cluster001.gbk'],
            ['KT809366.1.cluster001.gbk']

        ]
        # gb_list = gb_list[:2]
        for i, s in enumerate(gb_list):
            for j, f in enumerate(s):
                gb_list[i][j] = os.path.join(self.gb_records_dir, f)

        # print(gb_list)

        for record_set in gb_list:
            utils.process_record_set(self.connection, record_set)

    def test_03_process_gb(self):
        """derive types from basic info"""
        connection = self.connection
        gb_ids = [gb[0] for gb in db.check_gb(connection)]
        for gb_id in gb_ids:
            genes = db.check_gene(connection, gb_id=gb_id)
            result = utils.make_default_domains_from_gene_list(
                connection, genes
            )
            print('aS domains')
            result = utils.make_default_aS_domains_from_gb(connection, gb_id)
            domains = db.check_domain(connection)
            print("domains: {0}".format(len(domains)))
            assert_equal(result, True)

    @SkipTest
    def test_04_cluster_types(self):
        """cluster added types"""

        # dump out the sequences
        connection = self.connection
        result = utils.aS_sort_domains(connection)
        default_domain_name = 'unknown_domain'
        default_item = db.check_type(connection, name=default_domain_name)
        assert len(default_item) > 0
        default_domain_type_id = default_item[0][0]

        return result

        # cluster them

        # process the clusters

        # save it in database

