"""Utilities for producing trees"""
import os
import subprocess

import ete3
import hashlib

from evoc import db


def intersect(stree_file, gtree_file):
    """utility for intersecting the nodes of a gene tree with nodes in a
       species tree"""

    # load species tree
    stree = ete3.Tree(stree_file, format=1)
    s_leaves = [node.name for node in stree]
    # print(s_leaves)

    # load gene tree
    gtree = ete3.Tree(gtree_file, format=1)
    # gtree must be rooted!
    copy = gtree.copy()

    to_prune = [
        node.name for node in gtree if node.name.split('_')[0] in s_leaves
    ]
    # print('to_prune', to_prune)

    copy.prune(to_prune)
    # print(copy, '\n')
    # print(copy.write())
    return copy.write()


def get_relabel_map(connection, domain_id, type_name, seq_hash):
    """translate a (domain_id, type_name, seq_hash) query into a
        (taxon_id, domain_id, type_id, type_name) resuilt """

    cursor = connection.cursor()
    cmd = """SELECT taxon.taxon_id, domain.domain_id,
                    type.type_id, type.name
        FROM type
        JOIN domain ON
            domain.type_id = type.type_id
        JOIN gene ON
            domain.source_gene_id = gene.gene_id
        JOIN gb ON
            gene.gb_id = gb.gb_id
        JOIN taxon ON
            gb.taxon_id = taxon.taxon_id
        WHERE type.name = ? AND
            gene.uniquename GLOB ?
            OR
            domain.domain_id = ?
        """

    result = cursor.execute(
        cmd, (type_name, '*' + seq_hash + '*', domain_id)
    ).fetchall()
    assert len(result) > 0, exit('problem')
    return result[0]


def relabel(dbfile, treefile, species=False):
    """relabel a given tree file using a given database"""

    connection = db.init_db(dbfile)
    if treefile.endswith('.nex'):
        from Bio import Phylo
        # from io import StringIO
        Phylo.read(treefile, format='nexus')
        exit('nexus does not work')
        # tree_string = StringIO(str(tree_temp.format('newick')))
        # tree = ete3.Tree(tree_string)
    elif treefile.endswith('.new'):
        tree = ete3.Tree(treefile)
    elif treefile.endswith('.tree'):
        tree = ete3.Tree(treefile)
    else:
        exit('tree format not known')

    for leaf in tree:
        temp_name = leaf.name
        # print(temp_name)
        temp_name = temp_name.split('|')
        temp_hash = temp_name[1]
        type_name = temp_name[-1]
        temp_domain_id = temp_name[-2]
        result = get_relabel_map(
            connection,
            temp_domain_id,
            type_name,
            temp_hash
        )
        leaf.add_features(
            original_name=leaf.name,
            taxon_id=str(result[0]),
            domain_id=str(result[1])
        )
        if not species:
            leaf.name = leaf.taxon_id + '_' + leaf.domain_id
        else:
            leaf.name = leaf.taxon_id

    return tree.write()


def afaprepare(dbfile, domain_type_arg, location='domains'):
    """prepare for aligning a set of sequences"""
    import evoc.utils
    # get seqs from database
    seqs = evoc.utils.get_mfa(dbfile, domain_type_arg)
    # calculate md5hash
    md5hash = hashlib.new('md5', seqs.encode('utf-8')).hexdigest()

    # figure out what to call them, and where to put them
    connection = db.init_db(dbfile)
    ob_id, ob_name = evoc.utils.translate_anchor(connection, domain_type_arg)
    out_path = os.path.join(
        '.', location, ob_name
    )
    out_file = os.path.join(out_path, ob_name + '.fasta')

    try:
        os.makedirs(out_path)
    except OSError as e:
        # already exists
        pass

    # output path exists
    if os.path.exists(out_file):
        with open(out_file, 'rb') as inputfile:
            filemd5 = hashlib.md5(inputfile.read()).hexdigest()
        if filemd5 == md5hash:  # files are same
            print('file already exists, not writing')
            return out_file

    with open(out_file, 'w') as outh:
        outh.write(seqs)
        print('wrote seqs to {0}.'.format(out_file))

    return out_file


def align(input_file, method='muscle', force=False):
    """function to align a set of sequences"""

    import configparser
    config = configparser.ConfigParser()
    from pkg_resources import resource_filename
    base_config = resource_filename('evoc', 'default.conf')
    config.read(base_config)
    muscle_bin = config['muscle']['muscle_bin']

    # process input_file
    base_path, base_name = os.path.split(input_file)
    base = base_name.split('.')[0]

    input_file_time = os.path.getmtime(input_file)
    # align the sequences
    if method == 'muscle':
        for i in range(6):
            if i == 0:
                infile = os.path.join(base_path, base_name)
                outfile = os.path.join(
                    base_path, base + '.muscle.{0}'.format(i)
                )
            else:
                infile = os.path.join(
                    base_path, base + '.muscle.{0}'.format(i - 1)
                )
                outfile = os.path.join(
                    base_path, base + '.muscle.{0}'.format(i)
                )

            align_cmd = [
                muscle_bin,
                '-in',
                infile,
                '-out',
                outfile,
                '-maxiters', '100'
            ]
            if i > 0:
                align_cmd.append('-refine')
            if os.path.exists(outfile) and not force:
                outfiletime = os.path.getmtime(outfile)
                if outfiletime > input_file_time:
                    print(
                        'skipping alignment because {0} exists and is newer '
                        'than {1}'.format(
                            outfile, input_file
                        ))
                    if i == 5:
                        return outfile
            subprocess.call(align_cmd)
        return outfile


def make_tree(input_file, tree_method='fasttree', number=1, force=False, t=8):
    """make a tree using the provided method"""

    # parse config
    import configparser
    config = configparser.ConfigParser()
    from pkg_resources import resource_filename
    base_config = resource_filename('evoc', 'default.conf')
    config.read(base_config)

    base_path, base_name = os.path.split(input_file)
    in_file = base_name.split('.')
    ob_name = in_file[0]
    ali_method = in_file[1]

    # make subdirectory
    output_path = os.path.join(base_path, tree_method)
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    if tree_method == 'fasttree':
        # make a fast tree
        fasttree_bin = config['fasttree']['fasttree_bin']
        output_file = os.path.join(
            output_path, '{0}.{1}.ft.tree'.format(ob_name, ali_method)
        )
        input_time = os.path.getmtime(input_file)
        tree_cmd = [
            fasttree_bin,
            '-wag', '-gamma',
            '-out',
            output_file,
            input_file
        ]
    elif tree_method == 'phyml':
        phyml_bin = config['phyml']['phyml_bin']

        # convert to phyml
        from evoc.utils import convert_afa_to_phy

        # convert to phylip format
        new_name = os.path.join(
            output_path,
            '{0}.{1}'.format(ob_name, ali_method) + '.phy')
        convert_afa_to_phy(
            input_file,
            new_name
        )
        input_file = new_name
        output_file = os.path.join(
            output_path, '{0}.{1}.phy_phyml_tree'.format(ob_name, ali_method)
        )
        input_time = os.path.getmtime(new_name)
        tree_cmd = [
            # 'mpirun', '-np', str(7),
            # './lib/phyml/src/phyml',
            phyml_bin,
            '-i', new_name,
            '-d', 'aa',         # input type
            '-b', str(number),  # bootstraps
            '-m', 'JTT',        # model
            '-f', 'e',          # empirical frequencies, or m for model freqs
            '-v', 'e',          # ML est prop. of inv sites for discrete gamma
            '-c', '10',         # 4 categories of site variation discrete gamma
            '-a', 'e',          # float or ML esimate of Gamma(alpha) param
            '-s', 'SPR',        # SPR and NNI best search for tree topology
            # '-k',               # optimize branch lengths of bootstraps
        ]
    elif tree_method == 'raxml':
        # identify bin
        raxml_single_bin = config['RAxML']['RAxML_single_bin']
        raxml_multi_bin = config['RAxML']['RAxML_multi_bin']
        raxml_bin = raxml_single_bin
        if t > 1:
            raxml_bin = raxml_multi_bin
        # make a tree using raxml
        outname = '{0}.{1}.raxml'.format(ob_name, ali_method)
        outnameboot = '{0}.{1}.boot.raxml'.format(ob_name, ali_method)
        outnameconsensus = '{0}.{1}.consensus.raxml'.format(
            ob_name, ali_method
        )
        output_file = os.path.join(
            output_path,
            'RAxML_bipartitionsBranchLabels.{0}.{1}.consensus.raxml'.format(
                ob_name, ali_method
            )
        )
        input_time = os.path.getmtime(input_file)
        tree_cmd1 = [
            # './lib/standard-RAxML/raxmlHPC-PTHREADS-AVX2',
            raxml_bin,
            '-s', input_file,               # sequence file name
            '-n', outname,              # output file name
            '-m', 'PROTGAMMAIAUTO',     # model
            '-f', 'd',                  # method
            '-T', str(8),               # Threads
            '-#', str(number),             # run number
            '-p', str(55555),           # randomseed for initial tree
            '--auto-prot=aic',          # aic selection of best protein model
            '-w', os.path.abspath(output_path)  # absolute path to output dir
        ]
        tree_cmd2 = [
            # './lib/standard-RAxML/raxmlHPC-PTHREADS-AVX2',
            raxml_bin,
            '-s', input_file,                # sequence file name
            '-n', outnameboot,          # output file name
            '-m', 'PROTGAMMAIAUTO',     # model
            '-f', 'd',                  # method
            '-T', str(8),               # Threads
            '-b', str(12345),           # bootstrap random seed,
            '-#', str(number),             # bootstrap number
            '-p', str(55555),           # randomseed for initial tree
            # '-d',                       # random starting trees for ML
            '--auto-prot=aic',          # aic selection of best protein model
            '-w', os.path.abspath(output_path)  # absolute path to output dir
        ]
        tree_cmd3 = [
            # './lib/standard-RAxML/raxmlHPC-PTHREADS-AVX2',
            raxml_bin,
            '-n', outnameconsensus,          # output file name
            '-m', 'PROTGAMMAIAUTO',     # model
            '-f', 'b',                  # method - draw bipartitions
            '-t', os.path.join(
                output_path,
                'RAxML_bestTree.{0}.{1}.raxml'.format(ob_name, ali_method)
            ),
            '-z', os.path.join(
                output_path,
                'RAxML_bootstrap.{0}.{1}.boot.raxml'.format(
                    ob_name, ali_method
                )
            ),
            '-w', os.path.abspath(output_path)  # absolute path to output dir
        ]
    else:
        if os.path.exists(output_path):
            os.rmdir(output_path)
        exit('method "{0}"" not known'.format(tree_method))

    if os.path.exists(output_file):
        output_time = os.path.getmtime(output_file)
    else:
        print('Expected output file {0} not found'.format(output_file))
        output_time = None
    if output_time is not None and input_time < output_time and not force:
        print('{0} output is newer than input, skipping'.format(
            tree_method
        ))
        return True
    if force:
        print('Forced {0} recalculation, removing files in {1}'.format(
            tree_method, output_path
        ))
        for f in os.listdir(output_path):
            os.remove(os.path.join(output_path, f))

    if tree_method == 'raxml':
        print(tree_cmd1)
        subprocess.call(tree_cmd1)
        print(tree_cmd2)
        subprocess.call(tree_cmd2)
        print(tree_cmd3)
        subprocess.call(tree_cmd3)
    else:
        print(tree_cmd)
        subprocess.call(tree_cmd)

    return True


def build(
    dbfile,
    domain_type_arg,
    ali_method='muscle',
    tree_method='fasttree',
    number=1,
    location='domains'
):
    """extract, align, build tree using auto method given domain type info"""
    # get seqs
    base_seq_file = afaprepare(dbfile, domain_type_arg, location=location)
    base_align_file = align(base_seq_file, method=ali_method)
    return make_tree(base_align_file, tree_method=tree_method, number=number)
