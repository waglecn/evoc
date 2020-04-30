import os
from evoc import utils
from evoc import db
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from unittest import mock


class Test_utils:

    test_dir_name = 'testdir'
    test_dir = os.path.join('.', test_dir_name)

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        cls.test_db_file = './testdb.sqlite3'
        cls.connection = db.init_db(cls.test_db_file)
        cls.test_dir = os.path.dirname(__file__)
        cls.type_tsv_file = os.path.join(cls.test_dir, 'test_types.tsv')
        cls.species_tree_file = os.path.join(cls.test_dir, 'test.stree.tree')
        cls.gene_tree_file = os.path.join(cls.test_dir, 'test.gtree.tree')

        cls.dummy_nex_file = os.path.join(cls.test_dir, 'dummy.nex')
        cls.dummy_new_file = os.path.join(cls.test_dir, 'dummy.new')
        cls.dummy_file = os.path.join(cls.test_dir, 'dummy')

        # make test dir
        if not os.path.exists(cls.test_dir):
            os.mkdir(cls.test_dir)

        # make dummy file
        with open(cls.dummy_nex_file, 'w') as outh:
            outh.write(
                ""
                "#nexus\n"
                "begin trees;\n"
                "\ttree one = [&U] (1,2,(3,(4,5)));\n"
                "end;\n"
                ""
            )
        outh.close()
        with open(cls.dummy_new_file, 'w') as outh:
            outh.write("(1,2,(3,(4,5)));\n")
        outh.close()

        with open(cls.dummy_file, 'w') as outh:
            outh.write("(1,2,(3,(4,5)));\n")
        outh.close()

        num_species = 6  # less than sixteen
        connection = cls.connection

        # load test types
        type_tsv_file = cls.type_tsv_file
        types, relationships = utils.read_relationship_tsv(type_tsv_file)
        result = db.load_relationships(connection, types, relationships)
        assert_equal(result, True)

        cls.fake_sequence_names = []
        # add fake domain heirarchy
        cls.parent_domain_name = 'org-domain_whole'
        db.add_type(
            connection,
            name=cls.parent_domain_name,
            description='org domain whole'
        )
        # retreive parent and is_a ids
        parent_result = db.check_type(connection, name=cls.parent_domain_name)
        cls.parent_id = parent_result[0][0]
        rel_result = db.check_type(connection, name='is_a')
        cls.is_a_id = rel_result[0][0]

        for i in range(1, num_species):
            # add taxon types
            name = 'org{0}'.format(str(i))
            desc = 'org_{0}'.format(str(i))
            if not db.check_type(connection, name=name, description=desc):
                db.add_type(connection, name=name, description=desc)
            taxon_type_result = db.check_type(connection, name=name)
            # add domain type
            domain_name = 'org{0}-domain_whole'.format(str(i))
            domain_desc = 'org{0} domain whole'.format(str(i))
            if not db.check_type(
                connection, name=domain_name, description=domain_desc
            ):
                db.add_type(
                    connection,
                    name=domain_name,
                    description=domain_desc
                )
            # add fake relationship
            domain_type_result = db.check_type(connection, name=domain_name)
            db.add_relationship(
                connection,
                object_id=cls.parent_id,
                subject_id=domain_type_result[0][0],
                type_id=cls.is_a_id
            )
            # add taxon
            if not db.check_taxon(
                connection,
                type_id=taxon_type_result[0][0]
            ):
                db.add_taxon(
                    connection,
                    type_id=taxon_type_result[0][0]
                )
            taxon_result = db.check_taxon(
                connection,
                type_id=taxon_type_result[0][0]
            )
            # add gb
            if not db.check_gb(connection, taxon_id=taxon_result[0][0]):
                db.add_gb(
                    connection,
                    taxon_id=taxon_result[0][0],
                    prefix='prefix{0}'.format(str(i))

                )
            gb_result = db.check_gb(connection, taxon_id=taxon_result[0][0])
            # add gene
            dummy_seq = ''
            # bases = ['A', 'C', 'G', 'T']
            residues = [
                'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L',
                'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y'
            ]
            import random
            random.seed(12345)
            for k in range(0, 102):
                dummy_seq += random.choice(residues)
            if not db.check_gene(
                connection,
                type_id=domain_type_result[0][0]
            ):
                db.add_gene(
                    connection,
                    uniquename=str(i) * 32,
                    gb_id=gb_result[0][0],
                    type_id=domain_type_result[0][0],
                    location='[[1, 0, 100]]',
                    start=0,
                    end=100,
                    seq=dummy_seq
                )
            gene_result = db.check_gene(
                connection,
                type_id=domain_type_result[0][0]
            )
            # add domain
            if not db.check_domain(
                connection,
                source_gene_id=gene_result[0][0],
                type_id=domain_type_result[0][0]
            ):
                db.add_domain(
                    connection,
                    source_gene_id=gene_result[0][0],
                    type_id=domain_type_result[0][0],
                    start=1,
                    end=100
                )
            domain_result = db.check_domain(
                connection,
                source_gene_id=gene_result[0][0],
                type_id=domain_type_result[0][0]
            )
            fake_name = '{0}|{1}|{2}-{3}|{4}|{5}'.format(
                gb_result[0][-2],  # prefix
                gene_result[0][1][:6],  # uniquename hexamer
                1,  # start
                100,  # end
                domain_result[0][0],  # domain type id
                domain_name,  # domain name
            )
            cls.fake_sequence_names.append(fake_name)

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        cls.connection.close()
        os.remove(cls.test_db_file)

        os.remove(cls.dummy_nex_file)
        os.remove(cls.dummy_new_file)
        os.remove(cls.dummy_file)

        os.remove(os.path.join(
            cls.test_dir,
            'need_label_stree.tree'
        ))
        import shutil
        try:
            shutil.rmtree(
                os.path.join('.', cls.test_dir_name)
            )
            pass
        except Exception:
            pass

    def test_01_intersect(self):
        """make a random s_tree and a random g_tree"""
        import ete3

        # define ranges for dummy trees
        upper_range = 5
        upper_upper_range = 2 * upper_range

        # make fake species names
        snames_list = [str(i) for i in range(1, upper_range)]
        stree = ete3.Tree()
        # generate a random tree with these names and write it out
        stree.populate(len(snames_list), snames_list)
        stree.write(outfile=self.species_tree_file)

        import random
        # make fake genes, offset by 100, from an expanded set of species
        g_species = [i for i in range(1, upper_upper_range)]
        g_names = [100 + i for i in range(1, upper_upper_range)]
        # randomize so species 1 doesn't go with gene 101, 2 with 202 etc
        # probably not necessary
        random.shuffle(g_names)
        gnames_list = [
            '{0}_{1}'.format(i[0], i[1])
            for i in zip(g_species, g_names)
        ]
        # make the fake tree and write it
        gtree = ete3.Tree()
        gtree.populate(len(gnames_list), gnames_list)
        gtree.write(outfile=self.gene_tree_file)

        # attempt to intersect the tree
        result = utils.intersect(self.species_tree_file, self.gene_tree_file)
        itree = ete3.Tree(result, format=1)
        itree_names = [n.name.split('_')[0] for n in itree]
        # the species from the intersected tree must be the same as the
        # original species list
        assert_equal(set(itree_names), set(snames_list))

    def test_02_relabel_map(self):
        """test the relabelling function"""
        first_name = self.fake_sequence_names[0]
        first_name = first_name.split('|')
        test_domain_id = int(first_name[-2])
        test_domain_name = first_name[-1]
        test_hash = first_name[1]
        result = utils.get_relabel_map(
            self.connection,
            test_domain_id,
            test_domain_name,
            test_hash
        )
        assert_not_equal(result, False)
        assert_equal(
            (result[0], result[1], result[3]),
            (test_domain_id, test_domain_id, test_domain_name)
        )

    def test_03_relabel_species(self):
        """relabel a species tree with info from a database"""
        dbfile = self.test_db_file

        # create a dummy tree file
        need_label_stree_file = os.path.join(
            self.test_dir,
            'need_label_stree.tree'
        )
        leaf_names = [
            int(n.split('|')[-1].split('-')[0].lstrip('org')) for n in
            self.fake_sequence_names
        ]

        # make a fake species tree that needs relabelling and save it
        import ete3
        fake_tree = ete3.Tree()
        fake_tree.populate(
            len(self.fake_sequence_names),
            self.fake_sequence_names
        )
        fake_tree.write(outfile=need_label_stree_file, format=1)

        relabeled_newick_tree = utils.relabel(
            dbfile,
            need_label_stree_file,
            species=True
        )

        test_tree = ete3.Tree(relabeled_newick_tree, format=1)
        test_tree_ids = [int(n.name) for n in test_tree]
        # make sure all organism ids are correct
        for n in test_tree_ids:
            assert_equal(n in leaf_names, True)

    def test_04_relabel_gene(self):
        """relabel a gene tree with info from a database"""
        dbfile = self.test_db_file

        # create a dummy tree file
        need_label_stree_file = os.path.join(
            self.test_dir,
            'need_label_stree.tree'
        )
        leaf_names = [
            '{0}_{0}'.format(n.split('|')[-2]) for n in
            self.fake_sequence_names
        ]

        # make a fake species tree that needs relabelling and save it
        import ete3
        fake_tree = ete3.Tree()
        fake_tree.populate(
            len(self.fake_sequence_names),
            self.fake_sequence_names
        )
        fake_tree.write(outfile=need_label_stree_file, format=1)
        relabeled_newick_tree = utils.relabel(
            dbfile,
            need_label_stree_file,
            species=False
        )
        test_tree = ete3.Tree(relabeled_newick_tree, format=1)
        test_tree_ids = [n.name for n in test_tree]
        for n in test_tree_ids:
            assert_equal(n in leaf_names, True)

    def test_05_prepare_alignment(self):
        """get sequences from db using an anchor"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        assert_equal(os.path.exists(base_name), True)

    def test_06a_align_muscle(self):
        """build an alignment using muscle"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_path, base_file = os.path.split(base_name)
        base = base_file.split('.')[0]
        utils.align(base_name, method='muscle')
        for i in range(6):
            assert_equal(os.path.exists(
                os.path.join(
                    base_path, base + '.muscle.{0}'.format(i)
                )
            ), True)

    def test_07a_build_fasttree(self):
        """test the build function with muscle and fasttree"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        tree_method = 'fasttree'
        ali_method = 'muscle'
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_alignment = utils.align(base_name, method=ali_method)
        # check that return is true
        assert_equal(
            utils.make_tree(base_alignment, tree_method=tree_method, t=1),
            True
        )
        # check for production of the output tree
        assert_equal(
            os.path.exists(
                os.path.join(
                    '.',
                    self.test_dir_name,
                    domain_arg,
                    tree_method,
                    domain_arg + '.{0}.ft.tree'.format(ali_method)
                )
            ),
            True
        )

    def test_07b_build_phyml(self):
        """test the build function with muscle and phyml"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        tree_method = 'phyml'
        ali_method = 'muscle'
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_alignment = utils.align(base_name, method=ali_method)
        # check that return is true
        assert_equal(
            utils.make_tree(base_alignment, tree_method=tree_method),
            True
        )
        # check that correct files are created
        for suffix in [
            '_phyml_boot_stats',
            '_phyml_boot_trees',
            '_phyml_stats',
            '_phyml_tree'
        ]:
            expected_file = '{0}.{1}.phy{2}'.format(
                domain_arg, ali_method, suffix
            )
            assert_equal(
                os.path.exists(
                    os.path.join(
                        '.',
                        self.test_dir_name,
                        domain_arg,
                        tree_method,
                        expected_file
                    )
                ),
                True
            )
            print('found: {0}'.format(expected_file))

    def test_07c_build_raxml(self):
        """test the build function with muscle and raxml"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        tree_method = 'raxml'
        ali_method = 'muscle'
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_alignment = utils.align(base_name, method=ali_method)
        # check that return is true
        assert_equal(
            utils.make_tree(
                base_alignment, tree_method=tree_method, number=2, t=1
            ),
            True
        )
        # check that correct files are created
        for expected_file in [
            'RAxML_bestTree.{0}.{1}.raxml'.format(domain_arg, ali_method),
            'RAxML_bipartitionsBranchLabels.{0}.{1}.consensus.raxml'.format(
                domain_arg, ali_method
            ),
            'RAxML_bipartitions.{0}.{1}.consensus.raxml'.format(
                domain_arg, ali_method
            ),
            'RAxML_bootstrap.{0}.{1}.boot.raxml'.format(
                domain_arg, ali_method
            ),
            'RAxML_info.{0}.{1}.boot.raxml'.format(domain_arg, ali_method),
            'RAxML_info.{0}.{1}.raxml'.format(domain_arg, ali_method),
        ]:
            assert_equal(
                os.path.exists(
                    os.path.join(
                        '.',
                        self.test_dir_name,
                        domain_arg,
                        tree_method,
                        expected_file
                    )
                ),
                True,
                msg=expected_file
            )
            print('found: {0}'.format(expected_file))

    def test_08_relabel_other_trees(self):
        """Relabel other tree filenames"""

        with assert_raises(SystemExit):
            utils.relabel(
                self.test_db_file,
                self.dummy_nex_file,
            )

        with assert_raises(SystemExit):
            utils.relabel(
                self.test_db_file,
                self.dummy_file,
            )

    def test_09_test_relabel_new(self):
        """Relabel a new tree filename"""

        dbfile = self.test_db_file

        # create a dummy tree file
        need_label_stree_file = os.path.join(
            self.test_dir,
            'need_label_stree.new'
        )
        leaf_names = [
            '{0}_{0}'.format(n.split('|')[-2]) for n in
            self.fake_sequence_names
        ]

        # make a fake species tree that needs relabelling and save it
        import ete3
        fake_tree = ete3.Tree()
        fake_tree.populate(
            len(self.fake_sequence_names),
            self.fake_sequence_names
        )
        fake_tree.write(outfile=need_label_stree_file, format=1)
        relabeled_newick_tree = utils.relabel(
            dbfile,
            need_label_stree_file,
            species=False
        )
        test_tree = ete3.Tree(relabeled_newick_tree, format=1)
        test_tree_ids = [n.name for n in test_tree]
        for n in test_tree_ids:
            assert_equal(n in leaf_names, True)

    def test_10_test_afaprepare_alternate(self):
        """test preparing an afa using another term"""
        dbfile = self.test_db_file
        domain_arg = 'child'
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        assert_equal(os.path.exists(base_name), True)

    def test_11_test_bad_tree_method(self):
        """Try making a tree with a bad method"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_alignment = utils.align(base_name, method='muscle')
        with assert_raises(SystemExit):
            utils.make_tree(base_alignment, tree_method='abadtreemethod')

    def test_12_test_tree_forcing(self):
        """Test forcing tree building"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        tree_method = 'fasttree'
        ali_method = 'muscle'
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_alignment = utils.align(base_name, method=ali_method)

        # check that return is true
        assert_equal(
            utils.make_tree(
                base_alignment, tree_method=tree_method, force=True
            ),
            True
        )
        # check for production of the output tree
        assert_equal(
            os.path.exists(
                os.path.join(
                    '.',
                    self.test_dir_name,
                    domain_arg,
                    tree_method,
                    domain_arg + '.{0}.ft.tree'.format(ali_method)
                )
            ),
            True
        )

    def test_13_test_tree_timing(self):
        """Test building an identical tree"""
        dbfile = self.test_db_file
        domain_arg = self.parent_domain_name
        tree_method = 'fasttree'
        ali_method = 'muscle'
        base_name = utils.afaprepare(
            dbfile, domain_arg, location=self.test_dir_name
        )
        base_alignment = utils.align(base_name, method=ali_method)

        # check that return is true
        assert_equal(
            utils.make_tree(base_alignment, tree_method=tree_method),
            True
        )

    def test_14_test_build_command(self):
        """Try the build command"""
        assert_equal(
            utils.build(
                self.test_db_file,
                'org-domain_whole',
                location=self.test_dir_name
            ),
            True
        )

    def test_15_test_phy_conversion(self):
        """Test the afa to phy conversion explicitly"""
        # prepare basic alignment
        base_name = utils.afaprepare(
            self.test_db_file,
            'org-domain_whole',
            location=self.test_dir_name
        )
        # initial conversion
        utils.convert_afa_to_phy(
            base_name,
            outfile=base_name + '_phylip_converted'
        )
        # second conversion to prevent updating
        utils.convert_afa_to_phy(
            base_name,
            outfile=base_name + '_phylip_converted'
        )
        # conversion of of a bad alignment filename
        with assert_raises(SystemExit):
            utils.convert_afa_to_phy(
                'bogusBadBadName',
            )
