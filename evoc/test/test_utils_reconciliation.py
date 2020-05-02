import shutil
import os
import ete3

from evoc import utils
from evoc import db

import unittest
from nose.tools import assert_equal
from nose.tools import assert_raises


class Test_utils_reconciliation:
    dbname = 'testdb.sqlite3'
    test_dir = os.path.dirname(__file__)
    test_dir_new = os.path.join(test_dir, 'new')
    randomized_trees = os.path.join(
        test_dir, 'test.randomized.tree'
    )
    test_tree = os.path.join(test_dir, 'test.stree.tree')
    stree = os.path.join(test_dir, 'test.stree.tree')
    gtree = os.path.join(test_dir, 'test.gtree.tree')
    ultrametric_stree = os.path.join(test_dir, 'test.um.tree')

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        # cls.connection = db.init_db(cls.dbname)
        pass

    @classmethod
    def teardown_class(cls):
        """close database connection"""
        os.remove(cls.randomized_trees)
        os.remove(cls.ultrametric_stree)
        shutil.rmtree(os.path.join(cls.test_dir_new))
        shutil.rmtree(os.path.join(cls.test_dir, 'test.gtree.testing'))
        
    def test_01_test_tree_randomization(self):
        """Test tree randomization"""
        utils.randomize(
            'both', self.test_tree, 10, outfile=self.randomized_trees
        )
        with open(self.randomized_trees, 'r') as inh:
            trees = [t.strip() for t in inh if len(t.strip()) > 0]
        assert_equal(len(trees), 10)

    def test_02_test_tree_non_randomization(self):
        """Test tree non-randomization"""
        utils.randomize(
            '', self.test_tree, 10, outfile=self.randomized_trees
        )
        with open(self.randomized_trees, 'r') as inh:
            trees = [t.strip() for t in inh if len(t.strip()) > 0]
        assert_equal(len(trees), 10)

    def test_03_test_recon(self):
        """Test recon"""
        # make ultrametric stree
        try:
            stree = ete3.Tree(self.stree)
            stree.convert_to_ultrametric(tree_length=100.0)
            stree.write(format=1, outfile=self.ultrametric_stree)
        except Exception as e:
            print('skipping: {0}'.format(str(e)))
            unittest.skip('Could not write ultrametric tree')

        utils.do_rec(
            self.ultrametric_stree,
            self.gtree,
            self.test_dir,
            suffix='.testing'
        )

        # test naming
        new_gtree = os.path.join(self.test_dir, 'test_whole.gtree.tree')
        shutil.copyfile(self.ultrametric_stree, new_gtree)

        utils.do_rec(
            self.ultrametric_stree,
            new_gtree,
            self.test_dir_new,
        )

        # test bad gtree leaf names
        gtree = ete3.Tree(self.gtree, format=1)
        count = 0
        for l in gtree:
            l.name = '{0}{1}{0}'.format(count, l.name)
            count += 1
        bad_gtree = os.path.join(self.test_dir, 'bad_gtree.tree')
        gtree.write(format=1, outfile=bad_gtree)

        with assert_raises(SystemExit):
            utils.do_rec(
                self.ultrametric_stree,
                bad_gtree,
                self.test_dir_new
            )
            os.remove(bad_gtree)

    def test_04_test_grid_points(self):
        """Check grid point generation"""
        points = utils.grid_points(0.1, 0.1, 0.1)
        assert_equal(len(points) > 0, True)

    def test_05_test_subdivide_tree(self):
        """Check for the subdivision of tree object"""
        um_tree = ete3.Tree(self.ultrametric_stree)
        sprime_pseudo_root = utils.subdivide_tree(um_tree)
        assert_equal(len(sprime_pseudo_root.children), 2)

    def test_06_pseudo_root_on_invalid_tree(self):
        """Check for pseudo root to fail on an improper tree"""
        um_tree = ete3.Tree(self.ultrametric_stree)
        bad_tree = utils.subdivide_tree(um_tree)
        for t in bad_tree:
            if t.name != '-1':
                bad_tree = t
                bad_tree.del_feature('ttimes')
                break
        with assert_raises(SystemExit):
            utils.compute_pseudo_root(bad_tree)
