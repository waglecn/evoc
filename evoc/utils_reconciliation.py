"""utilities for reconciliation"""
import os
from evoc.utils_tree import relabel, intersect


def init_cli(subparser):
    import sys
    import argparse

    subparsers = []

    # subdivide tree sub-command
    subdivide_parser = subparser.add_parser(
        'subdivide',
        help='Compute the subdividion of species tree S into S\''
    )
    subdivide_parser.add_argument(
        'species_tree_file',
        help='an ultrametric species tree (Newick format)',
        type=argparse.FileType('r', encoding='utf-8'),
        nargs=1
    )
    subdivide_parser.add_argument(
        '-o', '--out',
        help='output to a file, default to stdout',
        type=argparse.FileType('w', encoding='utf-8'),
        nargs='?',
        dest='output',
        default=sys.stdout
    )
    subparsers.append(subdivide_parser)

    # process_recon sub-command
    process_recon_parser = subparser.add_parser(
        'recon_process',
        help='Process a reconciliation against a species tree',
    )
    process_recon_parser.add_argument(
        '-s', '--species_tree_file',
        help='a labelled species tree from ecceTERA output',
        type=argparse.FileType('r'),
        dest='stree_file',
        required=True
    )
    process_recon_parser.add_argument(
        '-r', '--reconciliation',
        help='reconciliation output in ecceTERA format',
        type=argparse.FileType('r'),
        dest='recon_file',
        required=True
    )
    process_recon_parser.add_argument(
        '-o', '--out',
        help='output to a file, default to stdout',
        type=argparse.FileType('w', encoding='utf-8'),
        nargs='?',
        dest='output',
        default=sys.stdout
    )
    subparsers.append(process_recon_parser)

    # recon_collect onto sprime sub-command
    collect_recon_parser = subparser.add_parser(
        'recon_collect',
        help='Collect one or more gtree reconciliations onto a species tree'
    )
    collect_recon_parser.add_argument(
        '-s', '--species_tree_file',
        help="a labelled species tree from ecceTERA output",
        type=argparse.FileType('r'),
        dest='stree_file',
        required=True
    )
    collect_recon_parser.add_argument(
        '-r',
        metavar='reconciliation',
        help="one or more reconciliation files from ecceTERA output",
        nargs='+',
        dest='recons',
        required=True
    )
    subparsers.append(collect_recon_parser)

    # determine_coordinates sub-command
    coordinates_parser = subparser.add_parser(
        'recon_coords',
        help='Determine the coordinates for a set of reconciliations'
    )
    coordinates_parser.add_argument(
        '-s', '--species_tree_file',
        help='a labelled species tree from ecceTERA output',
        type=argparse.FileType('r'),
        dest='stree_file',
        required=True
    )
    coordinates_parser.add_argument(
        '-r',
        metavar='reconciliation',
        help="one or more reconciliation files from ecceTERA output",
        nargs='+',
        dest='recons',
        required=True
    )
    subparsers.append(coordinates_parser)

    # draw_reconciliation sub-command
    draw_recon_parser = subparser.add_parser(
        'draw_recon',
        help='Draw one or more gene tree reconciliations on a host tree',
    )
    draw_recon_parser.add_argument(
        '-s', '--species_tree_file',
        help='a labelled species tree from ecceTERA output',
        type=argparse.FileType('r'),
        dest='stree_file',
        required=True
    )
    draw_recon_parser.add_argument(
        '-r',
        metavar='reconciliation',
        help='one or more reconciliation files from ecceTERA output',
        nargs='+',
        dest='recons',
        required=True
    )
    draw_recon_parser.add_argument(
        '-o', '--out',
        help='output to a file',
        type=argparse.FileType('w', encoding='utf-8'),
        dest='outfile',
        required=True
    )
    subparsers.append(draw_recon_parser)

    # summarize grid recon
    recon_grid_summary = subparser.add_parser(
        'grid_summary',
        help='Summarize the results of a grid reconciliation'
    )
    recon_grid_summary.add_argument(
        'recon_summary',
        help='one or more summary.csv produced by a grid reconciliation run',
        nargs='+',
    )
    recon_grid_summary.add_argument(
        '-o', '--out',
        help='output to a file',
        type=argparse.FileType('w', encoding='utf-8'),
        dest='outfile',
        default=sys.stdout
    )
    subparsers.append(recon_grid_summary)

    # do reconciliation
    do_rec_parser = subparser.add_parser(
        'rec',
        help='Perform a reconciliation'
    )
    do_rec_parser.add_argument(
        '-s', '--species_tree_file',
        help='a labelled species tree',
        type=argparse.FileType('r'),
        dest='stree_file',
        required=True
    )
    do_rec_parser.add_argument(
        '-g', '--gene_tree_file',
        help='a labelled gene tree',
        type=argparse.FileType('r'),
        dest='gtree_file',
        required=True
    )
    do_rec_parser.add_argument(
        '-o', '--output_dir',
        help='output directory',
        dest='outdir',
        required=True
    )
    do_rec_parser.add_argument(
        '--suffix',
        help='output suffix',
        dest='suffix',
    )
    subparsers.append(do_rec_parser)

    return subparsers


class TreeFormat(object):

    branch_height = 10
    node_radius = 0
    gnode_radius = 4

    # base coordinates
    units = 'px'
    width = 4800  # 1400
    height = 2700  # 600

    pad_top = 50
    pad_bottom = 50
    pad_left = 50
    pad_right = 50

    scale_width_frac = 0.05
    main_width_frac = 0.85
    dead_width_frac = 0.10

    # derived coordinates
    inner_height = height - pad_top - pad_bottom
    inner_width = width - pad_left - pad_right
    scale_width = inner_width * scale_width_frac
    main_width = inner_width * main_width_frac
    dead_width = inner_width * dead_width_frac

    binary_frac = 0.40
    unary_frac = 1.0 - binary_frac

    inner_leaf_frac = 0.5

    gtree_color_pool = [
        'darkslategrey',
        'blue',
        'orange',
        'green',
        'rgb(195, 195, 0)',
        'brown',
        'black',
        'teal'
    ]

    p_xoffset = 2
    p_yoffset = -10

    p_linewidth = 2
    p_dy = 1

    padding = 40

    branch_linecap = 'round'

    # Species tree specific
    branch_width = 20
    color = '#BDE9F0'
    label_inner = True
    # Hidden nodes are those that begin with a capital I
    # (intermediate nodes in S').
    label_inner_hidden = False
    label_leaves = True
    label_font_size = 8
    label_font_family = "Arial"
    label_offset = (0, 20)
    label_anchor = 'middle'

    dead_node_color = '#F2CBD4'
    dead_node_radius = 5

    # Relative to full positions, so a dx of 1 is a full leaf separate distance
    dead_dx = 0.2
    dead_dy = 0.3

    # Gene tree specific
    gbranch_width = 2
    gbranch_dash_array = 'none'
    gbranch_cross_dash_array = '5,3'
    gbranch_arc_height = 200  # Recommended values are between 50 and 200
    gbranch_arc_height_dead = 50  # Recommended values are between 50 and 200
    # Draw lost branches with short branches and an X marker.
    gbranch_draw_lost = True
    glabel = True
    glabel_font_size = 8
    glabel_font_family = "Courier New"  # Best to use a fixed width font here
    glabel_offset = (-5, -5)
    glabel_anchor = 'end'  # Options are start, middle and end for alignment.
    gcolors = ['#055FFA', '#FC2B0F', '#26E305']
    gmarker_colors = ['#055FFA', '#FC2B0F', '#26E305']
    gmarker_points = [(3, 0), (-3, 3), (-3, -3)]  # Flat triangle arrow

    # Leave blank to make GTF (cross lines) interact with other branches
    gbranch_cross_lines_prefix = '_cross_lines'
    # Leave blank to make GTF (cross lines) interact with other branches
    gbranch_dead_lines_prefix = '_dead_lines'

    # Cause an incoming TFD branch to enter above it's branch at the 2nd
    # highest I node
    move_tfd_nodes_up = False
    # Cause an incoming TLFD branch to enter above it's branch at the 2nd
    # highest I node
    move_tlfd_nodes_up = False

    # Cause an outgoing TTD branch to leave above it's branch at the 2nd
    #  highest I node
    move_ttd_nodes_up = True
    # Cause an outgoing TLTD branch to leave above it's branch at the 2nd
    # highest I node
    move_tltd_nodes_up = True

    # If True, will not draw and horizontal transfers between leaves.
    filter_leaf_transfers = False


def randomize_node_times(tree, root_tip_len=1000.0):
    """randomize node times, make ultrametric"""

    import random

    # make a copy of the original tree, to modify in-place
    t_root = tree.copy()
    for n in t_root.traverse(strategy='preorder'):
        if n.is_root():  # skip the root node (dist = 0)
            remaining = root_tip_len
        else:
            remaining = root_tip_len - t_root.get_distance(n.up, t_root)
            if not n.is_leaf():
                n.dist = random.uniform(0.0001, remaining)
            else:
                n.dist = remaining

    return t_root


def randomize(command, tree_file, number, outfile=None):
    import progress.bar
    import ete3

    output = []
    trees = []
    # load tree
    pbar = progress.bar.Bar(' randomizing Trees: ', max=number)
    orig_tree = ete3.Tree(tree_file, format=1)
    for i in range(0, number):
        if command == 'topologies' or command == 'both':
            name_list = [n.name for n in orig_tree]
            size = len(name_list)
            new_tree = ete3.Tree()
            new_tree.populate(size, names_library=name_list)
            trees.append(new_tree)
        else:
            trees.append(orig_tree.copy())
        pbar.next()
    pbar.finish()

    # output now contains <number> trees, either with random toplogies or
    # the same as the original

    # now make the trees ultrametric
    pbar = progress.bar.Bar(' randomizing node times: ', max=number)
    for t in trees:
        new_t = randomize_node_times(t)
        output.append(new_t)
        pbar.next()
    pbar.finish()

    if outfile is not None:
        with open(outfile, 'w') as outh:
            for t in output:
                outh.write('{0}\n'.format(t.write(),))
    return output


def do_rec(
    stree_file, gtree_file, prefix_dir,
    relabel_tree=False,
    db=None,
    suffix=None,
    cost_d=2.0,
    cost_t=3.0,
    cost_l=1.0
):
    """perform a reconciliation"""
    import ete3
    import subprocess

    import configparser
    config = configparser.ConfigParser()
    from pkg_resources import resource_filename
    base_config = resource_filename('evoc', 'default.conf')
    config.read(base_config)
    ecceTERA_bin = config['ecceTERA']['ecceTERA_bin']

    # figure out the prefix
    phead, ptail = os.path.split(gtree_file)
    if '_whole' in ptail:
        dprefix = ptail.split('_')[0]
    else:
        dprefix = '.'.join(ptail.split('.')[:-1])
    print('dprefix: {0}\n'.format(dprefix))
    if suffix is not None:
        gprefix = dprefix + suffix
    else:
        gprefix = ''
    print('gprefix: {0}\n'.format(gprefix))

    # make destination dir
    destination_dir = os.path.join(prefix_dir, gprefix, '')
    if not os.path.exists(destination_dir):
        os.mkdir(destination_dir)
        print('  created {0}\n'.format(destination_dir))
    else:
        print('  {0} already exists\n'.format(destination_dir))
    print('destination_dir: {0}'.format(destination_dir))

    # check for conflicting labels
    stree = ete3.Tree(stree_file)
    stree_labels = [l.name for l in stree]

    gtree = ete3.Tree(gtree_file)
    gtree_labels = [l.name for l in gtree]

    gl = [l.split('_')[0] for l in gtree_labels]
    found = [s for s in stree_labels if s in gl]
    if not len(found) > 0:
        exit('No compatible gene_tree labels found in species tree')

    # prune tree
    pruned_g = intersect(stree_file, gtree_file)
    pruned_file = os.path.join(
        destination_dir,
        '{0}.pruned.tree'.format(gprefix)
    )
    with open(
        pruned_file, 'w'
    ) as outh:
        outh.write(pruned_g)
        print('pruned gene file: {0}\n'.format(pruned_file))

    ec_g_file = '{0}.et.tree'.format(gprefix)
    ec_s_file = '{0}.et.stree'.format(gprefix)

    ec_cmd = [
        # './lib/ecceTERA_1.2.3/bin/ecceTERA_linux64',
        # './lib/ecceTERA/build/bin/ecceTERA',
        ecceTERA_bin,
        'species.file={0}'.format(stree_file),
        'gene.file={0}'.format(pruned_file),
        'dupli.cost={0}'.format(cost_d),
        'HGT.cost={0}'.format(cost_t),
        'loss.cost={0}'.format(cost_l),
        'output.dir={0}'.format(destination_dir),
        'output.prefix={0}.'.format(gprefix),
        'print.newick=1',
        'print.newick.gene.tree.file={0}'.format(ec_g_file),
        'print.newick.species.tree.file={0}'.format(ec_s_file),
        'resolve.trees=1',
        'verbose=1',
        # 'pareto.mod=1',
        # 'sylvx.reconciliation=true',
        'print.graph=true',
        'print.graph.file=graph.txt',
        'print.info=true',
        'print.reconciliations=1',
        'print.reconciliations.file=recons'
    ]
    print(ec_cmd)

    output = subprocess.check_output(ec_cmd, stderr=subprocess.STDOUT)
    with open(
        os.path.join(
            destination_dir, gprefix + '.et.out'
        ), 'wb'
    ) as outh:
        outh.write(output)
        print(output.decode('utf-8'))


def grid_points(d_step, t_step, l_step):
    import math
    import numpy as np
    d_step = float(d_step)
    t_step = float(t_step)
    l_step = float(l_step)

    # build a list of values
    points = []
    for d in np.arange(d_step, 1.0, d_step):
        tmax = math.fsum([1.0, -d])
        for t in np.arange(t_step, tmax - (0.01 * t_step), t_step):
            lamb = math.fsum([1.0, -t, -d])
            points.append((d, t, lamb))

    return points


def subdivide_tree(stree):
    """
    """
    import statistics
    import ete3

    # get time divisions
    ttimes = []

    # because of precision, all nodes have slightly different distance to root
    # this needs to be smoothed out with a mean?
    ltimes = [node.get_distance(stree) for node in stree]
    tree_height = statistics.mean(ltimes)

    sprime = stree.copy()  # copy avoids mangling original tree
    # time label leaf nodes
    for node in sprime:
        node.add_feature('c_time', 0.0)  # by definition
        # to distinguish from other string-valued interior node labels
        node.add_feature('unique_name', 'S' + node.name)

    # time label species_root
    sprime.add_feature('c_time', tree_height)
    sprime.add_feature('unique_name', stree.name)

    # time label non-leaf nodes
    for inode in sprime.traverse(strategy='postorder'):
        dist = inode.get_distance(sprime)  # dist to root
        if not inode.is_leaf() and not inode.is_root():
            c_dist = tree_height - dist
            inode.add_feature('c_time', c_dist)
            inode.add_feature('unique_name', inode.name)
            # inode.add_face(
            #     ete3.TextFace(inode.name, fsize=6),
            #     column=0,
            #     position='branch-top'
            # )
            ttimes.append(c_dist)

    # append leaf time (min time) and root time (max time)
    ttimes.append(0.0)
    ttimes.append(tree_height)

    # process ttimes - since added in post-order
    order_ttimes = []
    while True:
        i = max(ttimes)
        ttimes.remove(i)
        order_ttimes.append(i)
        if len(ttimes) == 0:
            break
    ttimes = order_ttimes
    sprime.add_feature('ttimes', ttimes)

    # traversal
    added = 0
    for i in sprime.traverse(strategy='postorder'):
        if not i.is_root():
            ip = i.up   # parent
            p_time = ip.c_time
            i_time = i.c_time

            # get intervals in path to parent
            in_times = [t for t in ttimes if t > i_time and t < p_time]
            in_times.sort(reverse=True)

            if len(in_times) > 0:
                # remove the current node
                temp = i.detach()
                # print('\nnode: {0}\t@ {1}'.format(i.uname, i.c_time))
                # print('parent: {0}\t@ {1}'.format(ip.uname, ip.c_time))
                # print('num. intervals: {0}'.format(len(in_times)))
                # initialize tip extension
                tip_time = p_time
                tip = ip

                # iterate new tips
                for t in in_times:
                    tip_dist = tip_time - t
                    tip.add_child(
                        name='I{0}'.format(added),
                        dist=tip_dist
                    )

                    last_added_name = 'I{0}'.format(added)
                    last_added = sprime.search_nodes(
                        name=last_added_name
                    )[0]
                    last_added.add_feature('c_time', t)
                    last_added.add_feature('uname', last_added_name)

                    # get new tip
                    tip_time = t
                    tip = last_added

                    # print('  added {0}\t@ {1} ({2})'.format(
                    #     last_added_name, t, tip_dist)
                    # )
                    added += 1

                # reattach the deleted node onto the extended path
                new_child = tip.add_child(
                    child=temp, name=temp.name, dist=(tip_time - i.c_time)
                )
                # print(' Reattached: {0}\t@ {1} ({2})'.format(
                #     i.uname,
                #     i_time,
                #     tip_time - i_time)
                # )
                # print(ip)
    # compute pseudo_root
    pseudo_root = compute_pseudo_root(sprime)
    pseudo_root.ladderize()
    if pseudo_root.children[0].name == '-1':
        pseudo_root.swap_children()
        pseudo_root.children[1].ladderize(direction=0)
    print(repr(sprime))

    # add sprime by name to pseudo_root
    pseudo_root.add_feature('s_root', sprime)
    return pseudo_root


def compute_pseudo_root(sprime):
    """
    """
    import ete3

    try:
        ttimes = sprime.ttimes
    except AttributeError:
        exit('ttimes feature not found on sprime root')

    pseudo_root = ete3.Tree(name='pseudo_root')
    pseudo_root.add_feature('c_time', None)
    pseudo_root.add_child(sprime)

    tip = pseudo_root
    for t in ttimes:
        index = ttimes.index(t)
        pseudot = tip.add_child(name='-1')
        pseudot.add_feature('c_time', t)
        pseudot.add_feature('unique_name', 'DEAD{0}'.format(index))
        pseudot.dist = t
        tip = pseudot

    return pseudo_root


def simple_grid_rec(
    stree_file, gtree_file, prefix_dir,
    d_step,
    t_step,
    l_step
):
    """perform a grid-search reconciliation"""
    points = grid_points(d_step, t_step, l_step)
    print(len(points))

    from multiprocessing import Pool

    mp = []
    for p in points:
        suffix = '-{0:.4f}_{1:.4f}_{2:.4f}'.format(
            p[0], p[1], p[2]
        )
        mp.append(
            (
                stree_file, gtree_file, prefix_dir,
                {
                    'suffix': suffix,
                    'cost_d': p[0],
                    'cost_t': p[1],
                    'cost_l': p[2]
                }
            )
        )
    with Pool(processes=7) as pool:
        pool.map(do_rec, mp)


def grid_summary(summary_list, outfile):
    """
    """
    grid = grid_points(0.02, 0.02, 0.02)
    for p in grid:
        t = '-{0:.4f}_{1:.4f}_{2:.4f}.recons_canonical_symmetric.txt'.format(
            p[0], p[1], p[2]
        )
        # print('{0:.2f}, {1:.2f}, {2:.2f}'.format(p[0], p[1], p[2]))
        for s in summary_list:
            head, tail = os.path.split(s)
            dirlist = os.listdir(head)
            hit = [f for f in dirlist if t in f]

            i = hit[0].find(t)
            label = hit[0][:i]


def process_recon(pseudo_root, recon_file_name):
    """
    """
    import ete3

    try:
        with open(recon_file_name, 'r') as inh:
            rlines = inh.readlines()
            rname = recon_file_name
    except TypeError as e:
        rlines = recon_file_name.readlines()
        rname = recon_file_name.name

    sprime = pseudo_root.s_root
    assert sprime is not None, exit('cannot grab sprime')
    print('tree S\': {0}'.format(repr(sprime)))

    nodes = {}
    gtree = None
    loss_counter = 0
    e_counter = {
        'S': 0,
        'SL': 0,
        'T': 0,
        'TL': 0,
        'TTD': 0,
        'TLTD': 0,
        'TFD': 0,
        'TLFD': 0,
        'D': 0,
        'DD': 0
    }
    rlines = [r.strip() for r in rlines]
    for line in rlines:
        line = line.strip()
        parsed_line = line.split(':')
        events = parsed_line[1].split(';')
        implied_id = parsed_line[0]

        # root event, do once
        if line in rlines[0]:
            print("    ROOT LINE:     {0}".format(line))
            # root event, not source event
            # the only way gtree transitions from initial None value
            print('    BEGINNING NEW GENE TREE on {0}'.format(implied_id))
            gtree = ete3.Tree(name=implied_id)
            gtree.add_feature('root_name', rname)
        else:
            print("    LINE:     {0}".format(line))
            # parse and remove parent event on non-root lines
            parent_event_item = events[0].split(',')
            parent_source, parent_event, parent_l, parent_r = parent_event_item
            events = events[1:]

        # <g_id>:<events>[:result]
        # infer from the length of the list whether each line culminates in
        # a binary or unary event
        if len(parsed_line) == 3:
            # binary event <g_id>:<events>:<g_l, g_r>
            # represents a split on the gene tree
            g_l, g_r = parsed_line[2].split(',')
        elif len(parsed_line) == 2:
            # unary event <g_id>:<events>:<g_id>
            # represents a single edge on the gene tree
            g_l = None
            g_r = None
        else:
            exit('weird line: {0}'.format(':'.join(line)))

        assert gtree is not None, exit('problem parsing non root line')

        # Except for the root node:
        # 1) every implied id beginning every line of a reconc must already
        #    be found in the tree
        # 2) this current tip must be a leaf!
        # update the current pointer to hold the current implied g_id leaf
        current = None
        # for c in gtree.search_nodes(name=implied_id):
        for c in gtree:
            if c.name == implied_id:
                current = c
                break
        assert current is not None, exit(
            'initial cannot find the curent s_tip {0}'.format(c.name)
        )
        # if current.up is not None:
        #     print('initial current', current.up.get_ascii(show_internal=True))
        for e in events:
            print('      event: {0}'.format(e))
            s_id, etype, auxl, auxr = e.split('@')[0].split(',')
            e_support = e.split('@')[1]
            if e_support == '':
                e_support = '1.0'
            e_counter[etype] += 1
            if etype == 'S':
                assert g_l is not None and g_r is not None, exit('S problem 1')
                # original
                nodes[s_id] = {
                    'gmap': [implied_id],
                    'auxl': {},
                    'auxr': {},
                    'event': etype
                }

                nodes[s_id]['auxl'][auxl] = {'gmap': g_l}
                nodes[s_id]['auxr'][auxr] = {'gmap': g_r}
            if etype == 'T':
                assert g_l is not None and g_r is not None, exit('T problem 1')
                assert auxl == s_id or auxr == s_id, exit('T problem 2')
                nodes[s_id] = {
                    'gmap': [implied_id],
                    'auxl': {},
                    'auxr': {},
                    'event': etype
                }
                nodes[s_id]['auxl'][auxl] = {'gmap': g_l}
                nodes[s_id]['auxr'][auxr] = {'gmap': g_r}
            if etype == 'D':
                assert g_l is not None and g_r is not None, exit('D problem 1')
                assert auxl == s_id and auxr == s_id, exit('D problem 2')
                nodes[s_id] = {
                    'gmap': [g_l, g_r],
                    'auxl': {s_id: None},
                    'auxr': {s_id: None},
                    'event': etype
                }
            if etype == 'DD':
                assert g_l is not None and g_r is not None, exit(
                    'DD problem 1'
                )
                assert auxl == '-1' and auxr == '-1' and s_id == '-1', exit(
                    'DD problem 2'
                )
                nodes[s_id] = {
                    'gmap': [g_l, g_r],
                    'auxl': {s_id: None},  # '-1'
                    'auxr': {s_id: None},  # '-1'
                    'event': etype
                }
            if etype == 'TTD':
                assert g_l is not None and g_r is not None, exit(
                    'TTD problem 1'
                )
                assert (
                    auxl == '-1' and auxr == s_id or
                    auxl == s_id and auxr == '-1'
                ), exit('TTD problem 2')
                if auxl == '-1' and auxr == s_id:
                    nodes[s_id] = {
                        'gmap': [implied_id, g_r],
                        'auxl': {auxl: None},  # '-1'
                        'auxr': {s_id: None},
                        'event': etype
                    }
                else:
                    nodes[s_id] = {
                        'gmap': [implied_id, g_l],
                        'auxl': {s_id: None},
                        'auxr': {auxr: None},  # '-1'
                        'event': etype
                    }
            if etype == 'TFD':
                assert g_l is not None and g_r is not None, exit(
                    'TFD problem 1'
                )
                assert (
                    (auxl == '-1' and not auxr == '-1' and s_id == '-1') or
                    (not auxl == '-1' and auxr == '-1' and s_id == '-1')
                ), exit('TFD problem 2')
                if auxl != '-1' and auxr == '-1':
                    nodes[s_id] = {
                        'gmap': [implied_id, g_l],
                        'auxl': {},
                        'auxr': {auxr: None},
                        'evet': etype
                    }
                    nodes[s_id]['auxl'][auxl] = {'gmap': g_l}
                else:
                    nodes[s_id] = {
                        'gmap': [implied_id, g_l],
                        'auxl': {auxl: None},
                        'auxr': {},
                        'event': etype
                    }
                    nodes[s_id]['auxr'][auxr] = {'gmap': g_r}
            if etype == 'SL':
                assert s_id != auxl and s_id != auxr, exit(
                    'SL problem 1'
                )
                nodes[s_id] = {
                    'gmap': [implied_id],
                    'auxl': {},
                    'auxr': {},
                    'event': etype
                }
                nodes[s_id]['auxl']['L' + auxl] = {
                    'gmap': 'X_' + implied_id
                }
                nodes[s_id]['auxr'][auxr] = {'gmap': implied_id}
            if etype == 'TL':
                assert s_id == auxl and s_id != auxr, exit('TL problem 1')
                nodes[s_id] = {
                    'gmap': [implied_id],
                    'auxl': {},
                    'auxr': {},
                    'event': etype
                }
                nodes[s_id]['auxl']['L' + auxl] = {'gmap': 'X' + implied_id}
                nodes[s_id]['auxr'][auxr] = {'gmap': implied_id}
            if etype == 'TLTD':
                assert auxl == s_id and auxr == '-1', exit('TLTD problem 1')
                nodes[s_id] = {
                    'gmap': [implied_id],
                    'auxl': {},
                    'auxr': {},  # '-1'
                    'event': etype
                }
                nodes[s_id]['auxl']['L' + auxl] = {'gmap': 'X' + implied_id}
                nodes[s_id]['auxr'][auxr] = {'gmap': implied_id}
            if etype == 'TLFD':
                assert s_id == '-1' and auxr != '-1', exit(
                    'TLFD problem 1'
                )
                nodes[s_id] = {
                    'gmap': [implied_id],
                    'auxl': {},  # '-1'
                    'auxr': {},
                    'event': etype
                }
                nodes[s_id]['auxl']['L' + auxl] = {'gmap': 'X' + implied_id}
                nodes[s_id]['auxr'][auxr] = {'gmap': implied_id}

            # need a check to work with et labelled leaf nodes ie '3'
            # instead of 3 - searching for 3 in sprime can yield multiple
            # hits, so need to select the one that is a leaf
            temp = None
            print('\t   (looking for {0})'.format(s_id))
            if s_id.startswith("'") and s_id.endswith("'"):
                for n in pseudo_root.search_nodes(name=s_id.strip("'")):
                    if n.is_leaf():
                        temp = n
                        break
            else:
                temp = pseudo_root.search_nodes(name=s_id)[0]
            assert temp is not None, exit('cannot find s_id {0}'.format(
                s_id
            ))

            if etype in ['S', 'T', 'D', 'DD', 'TFD']:
                # a binary result, need to add two new gtree tips
                assert (g_l is not None and g_r is not None), exit(
                    'g_l is {0}, g_r is {1}'.format(str(g_l), str(g_r))
                )
                left_tip = current.add_child(name=g_l)
                right_tip = current.add_child(name=g_r)
                print('      extended {0} -> ({1}, {2})'.format(
                    current.name, g_l, g_r
                ))

                try:
                    current.mapped_to.append((temp, etype, e_support))
                    print(
                        '  added new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                except AttributeError as e:
                    current.add_feature('mapped_to', [(temp, etype, e_support)])
                    print(
                        '      Created new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                # extra actions to take on transfer
                if etype == 'T' or etype == 'TFD':
                    # which child is the transfer tip - the one that is the
                    # same as the s_id
                    if auxl == s_id:
                        transfer_stip_name = auxr
                        transfer_tip = right_tip
                    elif auxr == s_id:
                        transfer_tip = left_tip
                        transfer_stip_name = auxl
                    else:
                        exit('cannot identify T or TFD transfer tip')
                    if (
                        transfer_stip_name.startswith("'") and
                        transfer_stip_name.endswith("'")
                    ):
                        for n in pseudo_root.search_nodes(
                            name=transfer_stip_name.strip("'")
                        ):
                            if n.is_leaf():
                                really_temp = n
                                break
                    else:
                        really_temp = pseudo_root.search_nodes(
                            name=transfer_stip_name
                        )[0]
                    if not hasattr(transfer_tip, 'mapped_to'):
                        transfer_tip.add_feature('mapped_to', [])
                    transfer_tip.mapped_to.append((really_temp, 'T0', '1.0'))
                    transfer_tip.add_child(name=transfer_tip.name)
            elif etype in ['TTD']:
                # a binary result, need to add three new gtree tips
                # one for the remainder in species lineage
                # two in the dead linage, the recipient DEAD0 node
                assert (g_l is not None and g_r is not None), exit(
                    'g_l is {0}, g_r is {1}'.format(str(g_l), str(g_r))
                )
                # assign mapping to current
                if hasattr(current, 'mapped_to'):
                    current.mapped_to.append((temp, etype, e_support))
                    print(
                        '  added new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                else:
                    current.add_feature('mapped_to', [(temp, etype, e_support)])
                    print(
                        '      Created new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                # extend child tips
                children = [
                    current.add_child(name=g_l),
                    current.add_child(name=g_r)
                ]
                print('      extended {0} -> ({1}, {2})'.format(
                    current.name, g_l, g_r
                ))

                # which tip is the dead child?
                if auxl == '-1':
                    dead_child = children[0]
                elif auxr == '-1':
                    dead_child = children[1]

                dead_temp = None
                dead_id = '-1'
                dead_temp = pseudo_root.search_nodes(name=dead_id)[0]
                assert dead_temp is not None, exit('cannot find the dead tip')

                # extend that tip
                dead_child.add_feature('mapped_to', [(dead_temp, 'DEAD0', '1.0')])
                new_current = dead_child.add_child(name=dead_child.name)
                print('      Extended reference to new tip {0}'.format(
                    dead_child.name
                ))

            elif etype == 'TLTD':
                # map current
                if hasattr(current, 'mapped_to'):
                    current.mapped_to.append((temp, etype, e_support))
                    print(
                        '   added new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                else:
                    current.add_feature('mapped_to', [(temp, etype, e_support)])
                    print(
                        '   Created new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                # add loss node
                loss_counter += 1
                loss_name = 'loss{0}'.format(loss_counter)
                loss_tip = current.add_child(name=loss_name)
                print('      added tip to {0} -> {1}'.format(
                    current.name, (loss_name, etype, '1.0')
                ))
                assert loss_tip is not None, exit(
                    'cannot find loss tip {0}'.format(loss_name)
                )

                loss_map = None
                loss_child = auxl
                if loss_child.startswith("'") and loss_child.endswith("'"):
                    loss_child = loss_child.strip("'")
                    for n in pseudo_root.search_nodes(name=loss_child):
                        if n.is_leaf():
                            loss_map = n
                            break
                else:
                    loss_map = pseudo_root.search_nodes(name=loss_child)[0]
                assert loss_map is not None, exit(
                    'cannot find loss_child {0}'.format(loss_child)
                )

                loss_node = None
                try:
                    loss_node = pseudo_root.search_nodes(
                        name=auxl.strip("'")
                    )[0]
                except Exception as e:
                    assert loss_node is not None, exit(
                        'loss-mapped node {0} not found'.format(auxl)
                    )
                # print(loss_node)
                loss_tip.add_feature('mapped_to', [(loss_map, 'LOSS', '1.0')])

                dead_child = current.add_child(name=implied_id)

                dead_temp = None
                dead_id = '-1'
                if dead_id.startswith("'") and dead_id.endswith("'"):
                    dead_id = dead_id.strip("'")
                    for n in pseudo_root.search_nodes(name=dead_id):
                        if n.is_leaf():
                            temp = n
                            break
                else:
                    dead_temp = pseudo_root.search_nodes(name=dead_id)[0]
                assert dead_temp is not None, exit('cannot find the dead tip')
                # extend that tip
                dead_child.add_feature('mapped_to', [(dead_temp, 'DEAD0', '1.0')])
                print('      Moving reference to new DEAD0 tip {0}'.format(
                    implied_id
                ))
                current = dead_child
                dead_child = current.add_child(name=implied_id)
                dead_child.add_feature('mapped_to', [(dead_temp, 'DEAD0', '1.0')])
                current = dead_child
            elif etype in ['SL', 'TL', 'TLFD']:
                # in a unary event, need to add new nodes
                if etype == 'SL' or etype == 'TL':
                    # add loss node
                    loss_counter += 1
                    loss_name = 'loss{0}'.format(loss_counter)
                    print('      added tip to {0} -> {1}'.format(
                        current.name, (loss_name, etype)
                    ))
                    loss_tip = current.add_child(name=loss_name)
                    assert loss_tip is not None, exit(
                        'cannot find loss tip {0}'.format(loss_name)
                    )

                    loss_map = None
                    loss_child_name = auxl
                    if (
                        loss_child_name.startswith("'") and
                        loss_child_name.endswith("'")
                    ):
                        loss_child_name = loss_child_name.strip("'")
                        for n in pseudo_root.search_nodes(
                            name=loss_child_name
                        ):
                            if n.is_leaf():
                                loss_map = n
                                break
                    else:
                        loss_map = pseudo_root.search_nodes(
                            name=loss_child_name
                        )[0]
                    assert loss_map is not None, exit(
                        'cannot find loss_child {0}'.format(loss_child)
                    )
                    loss_tip.add_feature('mapped_to', [(loss_map, 'LOSS', '1.0')])

                if hasattr(current, 'mapped_to'):
                    current.mapped_to.append((temp, etype, e_support))
                    print(
                        '  added new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                else:
                    current.add_feature('mapped_to', [(temp, etype, e_support)])
                    print(
                        '      Created new mapped_to feature on {0} -> '
                        '{1} @ {2}'.format(
                            current.name, (temp.name, etype), e_support
                        )
                    )
                if etype == 'TL' or etype == 'TLFD':
                    # which child is the transfer tip - the one that is not the
                    # same as the s_id
                    print(e)
                    if auxl == s_id:
                        transfer_stip_name = auxr
                        transfer_tip = current

                    transfer_tip = transfer_tip.add_child(name=current.name)
                    if (
                        transfer_stip_name.startswith("'") and
                        transfer_stip_name.endswith("'")
                    ):
                        for n in pseudo_root.search_nodes(
                            name=transfer_stip_name.strip("'")
                        ):
                            if n.is_leaf():
                                really_temp = n
                                break
                    else:
                        really_temp = pseudo_root.search_nodes(
                            name=transfer_stip_name
                        )[0]
                    if not hasattr(transfer_tip, 'mapped_to'):
                        transfer_tip.add_feature('mapped_to', [])
                    transfer_tip.mapped_to.append((really_temp, 'T0', '1.0'))
                    current = transfer_tip
                # lastly, extend the current tip - if there are a series of
                # unary events, we need to keep extending the tip, and these
                # series of unary events may end up mapping to the same species
                # node
                new_current = current.add_child(name=implied_id)
                print('      Moving reference to new tip {0}'.format(
                    implied_id)
                )
                current = new_current

    # iterate through non-loss leaves in g_tree
    for n in [g for g in gtree if not g.name.startswith('loss')]:
        s_tip = None
        for s in sprime:
            if n.name.split('_')[0] == s.name:
                # found matching sprime leaf node
                s_tip = s
                break
        assert s_tip is not None, exit(
            ' s_tip not found {0} {1}'.format(
                n.name.split('_')[0], gtree.get_ascii(show_internal=True)
            )
        )
        # map all unmapped leaves to correct tip in sprime
        try:
            n.mapped_to.append((s_tip, 'C'))
        except AttributeError as e:
            # no mapped_to element
            n.add_feature('mapped_to', [(s_tip, 'C', '1.0')])

    gtree.add_feature('e_counter', e_counter)

    print('  Events counter: ', end='')
    for e in ['S', 'SL', 'D', 'DD', 'T', 'TL', 'TTD', 'TFD', 'TLTD', 'TLFD']:
        print('  {0}: {1}'.format(e, gtree.e_counter[e]), end='')
    print('')

    return gtree


def collect_onto_sprime(pseudo_root, gtrees):
    """
    """
    sprime = pseudo_root.s_root
    assert sprime is not None, exit('cannot pull sprime')
    print('\n\n' + '=' * 80 + '\n' + '=' * 80 + '\n')
    print('sprime: ' + repr(sprime))
    print('Collecting mapped gene nodes onto tree S\'')
    print('\n' + '=' * 80 + '\n' + '=' * 80 + '\n')
    sprime.add_feature('gtrees', gtrees)
    for gtree in sprime.gtrees:
        print('    Working on gtree computed from {0}'.format(gtree.root_name))
        # print(gtree.get_ascii(show_internal=True))
        # exit()
        for g in gtree.traverse(strategy='postorder'):
            if not hasattr(g, 'mapped_to') or len(g.mapped_to) == 0:
                exit('no mapping node, or wrong length')
            print('\n      considering {0} maps to {1} step {2}'.format(
                g.name,
                g.mapped_to,
                sprime.ttimes.index(g.mapped_to[0][0].c_time))
            )

            base = g.mapped_to[0][0]
            base_event = g.mapped_to[0][1]

            if base.name == '-1':
                base = [n for n in pseudo_root if n.name == '-1'][0]
                target = base.up
                interval_list = [(target, base)]
                while target.name == '-1':
                    interval_list = [(target, base)] + interval_list
                    target = target.up
            else:
                target = base.up
                # determine the interval for this event
                target = base.up  # interval must at least include one parent
                interval_list = [(target, base)]
                while target.name.startswith('I'):
                    interval_list = [(target.up, target)] + interval_list
                    target = target.up

            print('        parent of {0} is {1}'.format(
                base.name, target.name)
            )

            if base_event == 'LOSS':
                host_node = interval_list[0][1]
            elif base_event in ['C', 'S', 'SL', 'D', 'DD', 'T0']:
                # simple cases
                host_node = base
            elif base_event in ['T', 'TL']:
                # the child of this gene is found in an incomparable branch
                # and is already placed in post-order
                # to figure out where to place origin of the transfer, we need
                # to compare the intervals of the donor and recipient linages

                # recipient lineage - one is mapped to the same location,
                # the other to the location of the outgoing transfer
                if g.children[0].mapped_to[0][0] == base:
                    # recipient = g.children[1].mapped_to[0][0]
                    try:
                        recipient = g.children[1].children[0].host_node[0]
                    except Exception:
                        print(g.up.get_ascii(show_internal=True))
                        exit()
                    donor = g.mapped_to[0][0]
                    transfer_child = g.children[1]
                else:
                    # recipient = g.children[0].mapped_to[0][0]
                    recipient = g.children[0].children[0].host_node[0]
                    donor = g.mapped_to[0][0]
                    transfer_child = g.children[0]
                assert recipient is not base

                # recipient lineage interval
                target = recipient.up
                recipient_interval = [(target, recipient)]
                while target.name.startswith('I'):
                    recipient_interval = [(target.up, target)] \
                        + recipient_interval
                    target = target.up

                # donor lineage interval
                target = donor.up
                donor_interval = [(target, donor)]
                while target.name.startswith('I'):
                    donor_interval = [(target.up, target)] + donor_interval
                    target = target.up

                # interval intersection
                interval_list = [
                    (i, j)
                    for i in donor_interval
                    for j in recipient_interval
                    if (
                        i[0].c_time == j[0].c_time and
                        i[1].c_time == j[1].c_time
                    )
                ]

                # the latest interval [-1], in the donor's [0] latest
                # boundary [1]
                try:            
                    host_node = interval_list[-1][0][1]
                except Exception:
                    print(recipient_interval)
                    print(donor_interval)
                    print(donor.name)
                    print(recipient.name, 'step', sprime.ttimes.index(recipient.c_time))
                    exit(0)

                # then set the correct host node for the t0 child
                # 1: remove incorrect parasite
                print('\t\tneed to switch location of mapped t0 node')
                t0_node = transfer_child.host_node[0]
                print('\t\ttransfer_child @ {0} step {1}'.format(
                    t0_node.name,
                    sprime.ttimes.index(t0_node.c_time)
                ))
                for p in t0_node.parasites:
                    if p == (transfer_child, 'T0'):
                        t0_node.parasites.remove(p)
                        print(
                            '\t\tremoved incorrect p {0}  from t0_node '
                            'parasite list'.format(p[0].name)
                        )
                        break
                # 2: find correct interval in
                correct_t0_node = interval_list[-1][1][1]
                print('\t\tcorrect t0_node: {0} step {1}'.format(
                    correct_t0_node.name,
                    sprime.ttimes.index(correct_t0_node.c_time)
                ))
                if not hasattr(correct_t0_node, 'parasites'):
                    correct_t0_node.add_feature('parasites', [])
                correct_t0_node.parasites.append((transfer_child, 'T0'))
                print(
                    '\t\tadded transfer_child {0} to '
                    'correct host_node {1}'.format(
                        transfer_child.name, correct_t0_node.name
                    )
                )
                # 3: set correct host_node
                transfer_child.host_node = [correct_t0_node]
                print(
                    '\t\tset correct host_node {0} '
                    'on transfer_child {1}'.format(
                        correct_t0_node.name, transfer_child.name
                    )
                )
                if base_event == 'TL':
                    # also need to switch location of loss node
                    if g.children[0].name.startswith('loss'):
                        loss_child = g.children[0]
                    elif g.children[1].name.startswith('loss'):
                        loss_child = g.children[1]
                    else:
                        exit('FUBAR')
                    loss_child.mapped_to = g.mapped_to
                    for p in loss_child.host_node[0].parasites:
                        if p[0] == loss_child:
                            loss_child.host_node[0].parasites.remove(p)
                            print('removed',  p, 'from original host node')
                    loss_child.host_node = [host_node]
                    if not hasattr(host_node, 'parasites'):
                        host_node.add_feature('parasites', [])
                    host_node.parasites.append(p)
                    print(
                        loss_child.name, 'remapped to',
                        host_node.name, g.mapped_to[0][0].name
                    )

            elif base_event == 'TLFD':
                # similar situation to T events. Recipient lineage is easy
                # because the recipient is already visited in post order

                # recipient lineage
                if g.children[0].mapped_to[0][0] == base:
                    recipient = g.children[1].mapped_to[0][0]
                else:
                    recipient = g.children[0].mapped_to[0][0]
                assert recipient is not base
                # recipient lineage interval
                target = recipient.up
                recipient_interval = [(target, recipient)]
                while target.name.startswith('I'):
                    recipient_interval = [(target.up, target)] + \
                        recipient_interval
                    target = target.up

                # donor lineage - for TLFD, is the entire dead lineage, need
                # leaf node
                base = [n for n in pseudo_root if n.name == '-1'][0]

                target = base.up
                donor_interval = [(target, base)]
                while target.up.name == '-1':
                    donor_interval = [(target.up, target)] + donor_interval
                    target = target.up
                # interval intersection
                interval_list = [
                    (i, j)
                    for i in donor_interval
                    for j in recipient_interval
                    if (
                        i[0].c_time == j[0].c_time and
                        i[1].c_time == j[1].c_time
                    )
                ]
                # the earliest interval [0], in the donor [0], lowest boundary
                # of interval [1]
                host_node = interval_list[-1][0][1]
            elif base_event == 'TLTD':
                # donor lineage - species tree
                target = base.up
                donor_interval = [(target, base)]
                while target.name.startswith('I'):
                    donor_interval = [(target.up, target)] + donor_interval
                    target = target.up

                # recipient lineage - DEAD
                base = [n for n in pseudo_root if n.name == '-1'][0]

                target = base.up
                recipient_interval = [(target, base)]
                while target.up.name == '-1':
                    recipient_interval = [(target.up, target)] \
                        + recipient_interval
                    target = target.up

                # interval intersection
                interval_list = [
                    (i, j)
                    for i in donor_interval
                    for j in recipient_interval
                    if (
                        i[0].c_time == j[0].c_time and
                        i[1].c_time == j[1].c_time
                    )
                ]
                if len(interval_list) > 0:
                    print('interval_list', interval_list)
                    # the earliest node [0] in the donor [0], low boundary[1]
                    host_node = interval_list[0][0][1]
                elif len(interval_list) == 0 and base.up.name == 'pseudo_root':
                    host_node = base
            elif base_event == 'TTD':
                # donor lineage - species tree
                target = base.up
                donor_interval = [(target, base)]
                while target.name.startswith('I'):
                    donor_interval = [(target.up, target)] + donor_interval
                    target = target.up

                # recipient lineage - DEAD
                base = [n for n in pseudo_root if n.name == '-1'][0]

                target = base.up
                recipient_interval = [(target, base)]
                while target.up.name == '-1':
                    recipient_interval = [(target.up, target)] \
                        + recipient_interval
                    target = target.up

                # interval intersection
                interval_list = [
                    (i, j)
                    for i in donor_interval
                    for j in recipient_interval
                    if (
                        i[0].c_time == j[0].c_time and
                        i[1].c_time == j[1].c_time
                    )
                ]
                if len(interval_list) > 0:
                    print('interval_list', interval_list)
                    # the earliest node [0] in the donor [0], low boundary[1]
                    host_node = interval_list[0][0][1]
                elif len(interval_list) == 0 and base.up.name == 'pseudo_root':
                    host_node = base
            elif base_event == 'DEAD0':
                # recipient lineage - whole dead lineage
                base = [n for n in pseudo_root if n.name == '-1'][0]
                # recipient interval
                target = base.up
                recipient_interval = [(target, base)]
                while target.up.name == '-1':
                    recipient_interval = [(target.up, target)] \
                        + recipient_interval
                    target = target.up

                # donor interval needs to be calculated from parent
                parent_mapping = g.up.mapped_to[0][0]
                print('        parent of {0} is {1}, maps to {2}'.format(
                    g.name, g.up.name, g.up.mapped_to[0][0].name))
                target = parent_mapping.up
                donor_interval = [(target, parent_mapping)]
                while target.name.startswith('I'):
                    donor_interval = [(target.up, target)] + donor_interval
                    target = target.up

                interval_list = [
                    (i, j)
                    for i in donor_interval
                    for j in recipient_interval
                    if (
                        i[0].c_time == j[0].c_time and
                        i[1].c_time == j[1].c_time
                    )
                ]

                # the lowest entry [-1], of the recipient [1], bottom boundary
                # of interval [1]
                if len(interval_list) > 0:
                    host_node = interval_list[0][1][1]
                elif (
                    len(interval_list) == 0 and
                    g.up.mapped_to[0][0].up.name == 'pseudo_root'
                ):
                    # this happens when a TTD happens at the root node, parent
                    # mapped will access the interval from [pseudo_root, root]
                    # resulting in an empty interval intersection
                    host_node = g.mapped_to[0][0]
            elif base_event == 'TFD':
                # donor lineage - dead lineage
                base = [n for n in pseudo_root if n.name == '-1'][0]
                target = base.up
                donor_interval = [(target, base)]
                while target.up.name == '-1':
                    donor_interval = [(target.up, target)] + donor_interval
                    target = target.up

                # recipient - the child of the current gene that does
                # not also map to the dead lineage
                if g.children[0].mapped_to[0][0].name != '-1':
                    recipient = g.children[0].mapped_to[0][0]
                else:
                    recipient = g.children[1].mapped_to[0][0]
                assert recipient is not base

                # recipient interval
                target = recipient.up
                recipient_interval = [(target, recipient)]
                while target.name.startswith('I'):
                    recipient_interval = [(target.up, target)] \
                        + recipient_interval
                    target = target.up

                # interval intersection
                interval_list = [
                    (i, j)
                    for i in donor_interval
                    for j in recipient_interval
                    if (
                        i[0].c_time == j[0].c_time and
                        i[1].c_time == j[1].c_time
                    )
                ]
                # host_node should be the lowest [-1], of the donor [0],
                # lower boundary [1]
                host_node = interval_list[-1][0][1]

            else:
                exit('  unknown event {0}'.format(base_event))

            if not hasattr(host_node, 'parasites'):
                host_node.add_feature('parasites', [])
            host_node.parasites.append((g, base_event))
            if not hasattr(g, 'host_node'):
                g.add_feature('host_node', [])
            g.host_node.append(host_node)

            print('        mapped to {0} - {1}@{2} step {3}'.format(
                host_node.up.name,
                host_node.name,
                host_node.c_time,
                sprime.ttimes.index(host_node.c_time)
            ))

        print('    Collapsed {0} onto sprime\n\n'.format(gtree.root_name))
    return pseudo_root


def determine_coordinates(pseudo_root):
    """
    """
    import statistics

    sprime = pseudo_root.s_root
    assert sprime is not None
    print(repr(sprime))

    if not hasattr(pseudo_root, 'treeFormat'):
        pseudo_root.add_feature('treeFormat', TreeFormat())

    tf = pseudo_root.treeFormat

    print("Determining basic coordinates...")
    leaves = sprime.get_leaves()
    num_leaves = len(leaves)
    max_leaf_width = tf.main_width / float(num_leaves)
    tf.max_leaf_width = max_leaf_width

    inner_leaf_width = tf.inner_leaf_frac * max_leaf_width
    tf.inner_leaf_width = inner_leaf_width

    print('  Determining host node coordinates')
    # center_coordinate for first leaf
    initial_x = tf.pad_left + tf.scale_width + (max_leaf_width / 2.0)
    initial_y = tf.pad_top + tf.inner_height

    num_ttimes = len(sprime.ttimes)
    max_ttime_interval = float(tf.inner_height) / float(num_ttimes)
    tf.max_ttime_interval = max_ttime_interval
    default_dy = tf.binary_frac * max_ttime_interval

    # main lineage
    x = initial_x
    y = initial_y
    for n in sprime.traverse(strategy='postorder'):
        # placeholder coordinates
        if n.is_leaf():
            n.add_feature('x', x)
            n.add_feature('y', y)
            x += max_leaf_width
        else:
            if len(n.children) == 1:
                n.add_feature('x', n.children[0].x)
                n.add_feature('y', n.children[0].y - max_ttime_interval)
            elif len(n.children) == 2:
                n.add_feature(
                    'x',
                    statistics.mean(
                        [n.children[0].x, n.children[1].x]
                    )
                )
                n.add_feature('y', n.children[0].y - max_ttime_interval)
    print('  Determining DEAD node coordinates')
    # dead lineage
    dead_center = tf.dead_width / 2.0
    initial_x = tf.pad_left + tf.scale_width + tf.main_width + dead_center
    initial_y = tf.pad_top + tf.inner_height

    dead_tip = [n for n in pseudo_root if n.name == '-1'][0]
    dead_tip.add_feature('x', initial_x)
    dead_tip.add_feature('y', initial_y)
    dead_parent = dead_tip.up
    while not dead_parent.is_root():
        dead_parent.add_feature('x', initial_x)
        dead_parent.add_feature(
            'y', dead_parent.children[0].y - max_ttime_interval
        )
        dead_parent = dead_parent.up

    print('  Determining scale node coordinates')
    # scale
    scale_center = tf.scale_width / 2.0
    initial_x = tf.pad_left + scale_center
    initial_y = tf.pad_bottom

    # return pseudo_root  # simple exit

    print('  Determining embedded node coordinates')
    # after the host nodes have x,y coordinates, need to work on parasites
    # need to traverse the entire tree in order to determine how many parasite
    # nodes to draw at each species node in the interval between it and its
    # parent
    stack = pseudo_root.children
    while len(stack) > 0:
        print('\n The stack: {0}'.format(stack))
        # working on next child in the stack
        n = stack[0]
        stack = stack[1:]
        print('{0}    working on {1}'.format(
            '\n' + '#' * 20, n.name
        ))

        # courtesy, parent parasites for later matching
        parent_parasites = []
        if n.up.name == 'pseudo_root':
            parent_n = None
        else:
            parent_n = n.up
            if hasattr(parent_n, 'parasites'):
                parent_parasites += [p[0] for p in parent_n.parasites]
        ordered_parent_parasites = sorted(
            parent_parasites, key=lambda gene: gene.x
        )

        # get to next lowest binary child node - either the node is a leaf
        # or it has two children
        intervals = [n]
        tracks = []
        parasites = []
        x = n
        if hasattr(x, 'parasites'):
            for p in x.parasites:
                parasites.append(p[0])
        while not x.is_leaf() and len(x.children) == 1:
            intervals = [x.children[0]] + intervals
            if hasattr(x.children[0], 'parasites'):
                for p in x.children[0].parasites:
                    parasites.append(p[0])
            x = x.children[0]

        # intervals is now a reverse ordered list of intervals from c_l(n) to n
        # parasites now contains the entire list of parasite nodes mapping
        #    along this interval
        print('    This interval: {0} -> {1}'.format(
            intervals[-1].name, intervals[0].name
        ))

        # how many tracks does this require? Count how many of this parasites
        # have zero descendants in this interval - meaning they either map
        # to the lowest non-artificial species node in this interval, or
        # they map higher without descendants (loss nodes)
        for p in parasites:
            desc = [d for d in p.get_descendants() if d in parasites]
            if len(desc) == 0:
                print('      adding tip {0}'.format(repr(p)))
                tracks.append(p)

        # now I want to deal with them by gtree
        ordered_tracks = []
        for gtree in sprime.gtrees:
            g_nodes = [t for t in tracks if t.get_tree_root() == gtree]
            if len(g_nodes) == 0:
                continue

            print(' * parts by gtree {0}'.format(gtree.root_name))
            for g in g_nodes:
                if g.is_root():
                    pofg = 'N/A'
                    pofg_map = 'N/A'
                    p_event = '-'
                else:
                    pofg = '{0} ({1})'.format(g.name, hex(g.__hash__()))
                    pofg_map = '{0} ({1})'.format(
                        g.up.mapped_to[0][0].name,
                        hex(g.up.mapped_to[0][0].__hash__())
                    )
                    p_event = g.up.mapped_to[0][1]
                print('    {0}@{1} [{4}] ({2}@{3})'.format(
                    '{0} ({1})'.format(g.name, hex(g.__hash__())),
                    '{0} ({1})'.format(
                        g.mapped_to[0][0].name,
                        hex(g.mapped_to[0][0].__hash__())
                    ),
                    pofg, pofg_map, p_event
                ))

            # define an ordering function:
            # 1) the g_tree root
            # 2) and 3) descendants and duplications of parent of n, ordered as
            #   in parent
            # 3) incoming transfers and duplications, ordered by age of
            # out-going parent

            roots = []
            print('\n    Collecting root nodes...')
            # collect root nodes - roots do not exist in the parent
            for g in g_nodes:
                if g.is_root():
                    print('     {0} is root, removing'.format(g.name))
                    roots.append(g)

            # collect non-transfered-in tips (descended from the parent)
            ordered_tips = []
            print('\n    Collecting vertical nodes...')
            if len(ordered_parent_parasites) > 0:
                # order tips based on presence (if any) in p(n)
                # print('    Parent parasites: {0}'.format(
                #     ordered_parent_parasites
                # ))
                for p in ordered_parent_parasites:
                    # match the tip to the parent
                    desc = [
                        x for x in p.get_descendants() if x in parasites
                    ]
                    desc_tips = [x for x in g_nodes if x in desc]
                    if len(desc_tips) == 1:
                        tip = desc_tips[0]
                        ordered_tips.append(tip)
                        print(
                            '     {0} has parent {1}@{2}, single tip - added '
                            'to ordered tips'.format(
                                '{0} ({1})'.format(
                                    tip.name, hex(tip.__hash__())
                                ),
                                '{0} ({1})'.format(p.name, hex(p.__hash__())),
                                '{0} ({1})'.format(
                                    p.mapped_to[0][0].name,
                                    hex(p.mapped_to[0][0].__hash__())
                                ),
                            )
                        )
                    elif len(desc_tips) > 1:
                        # single parent, multiple tips, need to order
                        # one or more duplications
                        print(
                            '     multiple nodes have parent {0} [{1}]'.format(
                                repr(p), len(desc_tips)
                            )
                        )
                        dtips = []
                        descent_stack = [d for d in desc if d in p.children]
                        while len(descent_stack) > 0:
                            d = descent_stack.pop(0)
                            for c in d.children:
                                if c in desc_tips:
                                    dtips = [c] + dtips
                                elif c in desc:
                                    descent_stack.append(c)
                        ordered_tips += dtips

            # lastly, the remainder of the tips must have transfered in
            ordered_incoming = []
            print('\n    Collecting horizontal nodes...')
            transfer_tips = []
            non_desc_tips_of_p = [
                g for g in g_nodes if g not in roots and g not in ordered_tips
            ]
            print('    non-descendant tips of the parent {0}'.format(
                non_desc_tips_of_p
            ))
            if len(non_desc_tips_of_p) > 0:
                for tip in non_desc_tips_of_p:
                    t = tip
                    while t.up in parasites:
                        t = t.up
                    # tip and top-most parent of the tip in this lineage
                    transfer_tips.append((tip, t))
                transfer_tips = sorted(
                    transfer_tips,
                    key=lambda gene: gene[1].mapped_to[0][0].c_time
                )
                ordered_incoming = transfer_tips
                for incoming in ordered_incoming:
                    print('     have incoming {0} from {1}@{2}'.format(
                        incoming[0].name,
                        incoming[1].name,
                        incoming[1].mapped_to[0][0].name
                    ))
                ordered_incoming = [o[0] for o in ordered_incoming]

            # collect transferred in tips
            ordered_tracks += roots \
                + ordered_tips \
                + ordered_incoming

        # compute available dimensions
        # X cooordinate
        print('\n  Computing dimensions')
        num_tracks = len(ordered_tracks)
        print('  Need {0} tracks'.format(num_tracks))
        if num_tracks > 0:
            max_track_width = float(inner_leaf_width) / float(num_tracks)

            initial_x = n.x - (0.5 * inner_leaf_width) + \
                (0.5 * max_track_width)
            x = initial_x
            print('  X Setting X coordinates')
            print('    center of host: {0}'.format(n.x))
            print('    max_leaf_width: {0}'.format(max_leaf_width))
            print('    inner_leaf_width: {0}'.format(inner_leaf_width))
            print('    max_track_width: {0}'.format(max_track_width))
            print('    initial_x: {0}'.format(x))
            print('    Assigning:')
            for tip in ordered_tracks:
                print('     Track {0}: {1}.x = {2:.2f}'.format(
                    ordered_tracks.index(tip),
                    repr(tip), x,
                ))
                tip.add_feature('x', x)
                x += max_track_width

            p_stack = [p for p in parasites if p not in ordered_tracks]
            loop_breaker = 0
            while len(p_stack) > 0:
                print('      unassigned parasitess: {0}'.format(
                    len(p_stack))
                )
                p = p_stack.pop(0)
                children = [c for c in p.children if c in parasites]
                if len(children) == 1 and hasattr(children[0], 'x'):
                    print('assigning x to {0}'.format(repr(p)))
                    p.add_feature('x', children[0].x)
                    loop_breaker = 0
                elif len(children) == 2 and (
                    hasattr(children[0], 'x') and
                    hasattr(children[1], 'x')
                ):
                    p.add_feature(
                        'x',
                        statistics.mean([children[0].x, children[1].x])
                    )
                    loop_breaker = 0
                else:
                    print(p.name)
                    print(p)
                    print(children)
                    p_stack.append(p)
                    loop_breaker += 1
                    if loop_breaker >= 2 * len(p_stack):
                        for n in sprime.traverse(strategy='preorder'):
                            print(
                                n.name, n.c_time, sprime.ttimes.index(n.c_time)
                            )
                        exit('looplooploop')

            # Y coordinates
            # set basic dimensions
            max_layer_height = max_ttime_interval
            unary_height = max_layer_height * tf.unary_frac
            binary_height = max_layer_height * tf.binary_frac
            print('  Y Setting Y coordinates')
            print('    {0} intervals in this edge [{1:.2f}, {2:.2f}]'.format(
                len(intervals),
                intervals[0].y, intervals[-1].y
            ))
            for tip in ordered_tracks:
                # ordered list of ancestors for each track/tip
                g_nodes = [tip]
                g = tip
                while g.up in parasites:
                    g_nodes.append(g.up)
                    g = g.up

                print('     Track {0}: {1}, {2} ancestors'.format(
                    ordered_tracks.index(tip),
                    repr(tip), len(g_nodes),
                ))

                intervals.reverse()
                for i in intervals:
                    initial_y = i.y
                    y = initial_y
                    # build local list of nodes mapping inside this interval
                    local_g = []
                    if hasattr(i, 'parasites'):
                        local_g += [
                            p[0] for p in i.parasites if p[0] in g_nodes
                        ]
                    local_g = [g for g in g_nodes if g in local_g]

                    if len(local_g) > 0:
                        print(
                            '      interval {0}, {1} nodes, y = '
                            '{2:.2f}'.format(
                                intervals.index(i), len(local_g), y
                            )
                        )
                        # first event maps to the binary part of the interval
                        if local_g[0].mapped_to[0][1] in ['C', 'S', 'SL']:
                            binary_tip = local_g.pop(0)
                            binary_tip.add_feature('y', y)
                            print('       placed {0}.y = {1:.2f}'.format(
                                repr(binary_tip), y
                            ))
                        # all remaining nodes map to unary part of interval
                        y -= binary_height
                        if len(local_g) == 0:
                            # if no nodes remain after removin tip, next i
                            continue
                        num_layers = len(local_g)
                        print(
                            '      continue placing {0} nodes in interval '
                            '[{1:.2f},  {2:.2f}]'.format(
                                num_layers,
                                y,
                                y - unary_height
                            )
                        )
                        # remaining nodes map to the unary portion of the i
                        # need to know dimensions of required nodes
                        layer_width = float(unary_height) \
                            / float(num_layers)
                        for g in local_g:
                            # y coordinate is easy
                            g.add_feature('y', y)
                            y -= layer_width
                            print('       placed {0}.y = {1:.2f}'.format(
                                repr(g), y
                            ))

        # stagger for base nodes
        stagger_tips = [
            t for t in ordered_tracks if t.mapped_to[0][1] in ['S', 'SL']
        ]
        num_st = len(stagger_tips)
        print(stagger_tips)
        if num_st > 0:
            binary_height = max_ttime_interval * tf.binary_frac
            stagger_height = float(binary_height) / float(num_st)
            y = intervals[0].y - binary_height
            for st in stagger_tips:
                st.y = y
                y += stagger_height

        # add next part of the stack
        if not intervals[-1].is_leaf():
            # for child in intervals[0].children:
            stack = stack + intervals[0].children

    return pseudo_root


def svgdraw(pseudo_root, outfile_name):
    import ete3
    import svgwrite
    from svgwrite.mixins import Transform

    # pseudo_root = determine_coordinates(pseudo_root)
    tf = pseudo_root.treeFormat
    tf.parasite_nodes = True
    tf.parasite_edges = False

    sprime = pseudo_root.s_root
    assert sprime is not None

    # create drawing
    dwg = svgwrite.Drawing(
        filename=outfile_name,
        size=(
            '{0}{1}'.format(tf.width, tf.units),
            '{0}{1}'.format(tf.height, tf.units)
        )
    )
    arrows = []
    for c in tf.gtree_color_pool:
        arrow_marker = dwg.marker(
            insert=(0, 3),
            size=(6, 6),
            orient='auto'
        )
        arrow_marker.add(
            dwg.polygon(
                points=tf.gmarker_points,
                stroke=c,
                fill=c,
                stroke_width="0.1"
            )
        )
        dwg.defs.add(arrow_marker)
        arrows.append(arrow_marker)

    ts = ete3.TreeStyle()
    ts.rotation = 90
    ts.force_topology = True
    if pseudo_root.children[1].name == '-1':
        pseudo_root.swap_children()
    # pseudo_root.render(
    #     'pseudo_root.png', units='px', h=1100, w=1600, tree_style=ts
    # )

    # add elements to drawing
    simple = True
    if simple is False:
        print('\ndrawing svg host nodes')
        for n in pseudo_root.traverse(strategy='postorder'):
            if n.is_root():
                continue
            ret = dwg.add(
                dwg.circle(
                    center=(n.x, n.y),
                    r=20,
                    fill="red",
                    stroke="red",
                    stroke_width=1
                )
            )
            print(' s {0}: {1}'.format(repr(n), ret))
    else:
        print('\ndrawing svg host nodes')
        for n in pseudo_root.traverse(strategy='postorder'):
            if n.is_root():
                for c in n.children:
                    cpoints = [
                        c.x - (0.5 * tf.inner_leaf_width),
                        c.x + (0.5 * tf.inner_leaf_width)
                    ]
                    # rect
                    dwg.add(dwg.rect(
                        insert=(
                            cpoints[0],
                            c.y - (1.25 * tf.max_ttime_interval)
                        ),
                        size=(
                            tf.inner_leaf_width,
                            0.25 * tf.max_ttime_interval
                        ),
                        fill='#B8D8FF'
                    ))
                    # sides
                    dwg.add(dwg.line(
                        (cpoints[0], c.y - (1.0 * tf.max_ttime_interval)),
                        (cpoints[0], c.y - (1.25 * tf.max_ttime_interval)),
                        stroke='#5276A3',
                        stroke_width=2
                    ))
                    dwg.add(dwg.line(
                        (cpoints[1], c.y - (1.0 * tf.max_ttime_interval)),
                        (cpoints[1], c.y - (1.25 * tf.max_ttime_interval)),
                        stroke='#5276A3',
                        stroke_width=2
                    ))
            elif n.is_leaf():
                top = n
                height = 1
                if top.name == '-1':
                    while top.up.name.startswith('-1'):
                        top = top.up
                        height += 1
                else:
                    while top.up.name.startswith('I'):
                        top = top.up
                        height += 1

                # draw fill
                left = n.x - (0.5 * tf.inner_leaf_width)
                right = left + tf.inner_leaf_width
                dwg.add(dwg.rect(
                    insert=(left, top.y - tf.max_ttime_interval),
                    size=(
                        tf.inner_leaf_width,
                        height * tf.max_ttime_interval
                    ),
                    fill='#B8D8FF'
                ))
                # drall sides
                dwg.add(dwg.line(
                    (left, n.y),
                    (left, top.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2
                ))
                dwg.add(dwg.line(
                    (right, n.y),
                    (right, top.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2
                ))
            elif len(n.children) == 2:
                top = n
                height = 1
                if top.name == '-1':
                    while top.up.name.startswith('-1'):
                        top = top.up
                        height += 1
                else:
                    while top.up.name.startswith('I'):
                        top = top.up
                        height += 1
                cpoints = []
                for c in n.children:
                    cpoints.append(c.x - (0.5 * tf.inner_leaf_width))
                    cpoints.append(c.x + (0.5 * tf.inner_leaf_width))
                cpoints.sort()
                hpoints = [
                    n.x - (0.5 * tf.inner_leaf_width),
                    n.x + (0.5 * tf.inner_leaf_width)
                ]
                # fills
                # horizontal rect
                dwg.add(dwg.rect(
                    insert=(cpoints[0], n.y - tf.max_ttime_interval),
                    size=(cpoints[3] - cpoints[0], tf.max_ttime_interval),
                    fill='#B8D8FF'
                ))
                # vertical rect
                dwg.add(dwg.rect(
                    insert=(hpoints[0], top.y - tf.max_ttime_interval),
                    size=(
                        tf.inner_leaf_width,
                        n.y - top.y
                    ),
                    fill='#B8D8FF'
                ))
                # sides
                # bottom inner
                dwg.add(dwg.line(
                    (cpoints[1], n.y),
                    (cpoints[2], n.y),
                    stroke='#5276A3',
                    stroke_width=2
                ))
                # left to mid
                dwg.add(dwg.line(
                    (cpoints[0], n.y),
                    (cpoints[0], n.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2.0
                ))
                # left mid
                dwg.add(dwg.line(
                    (cpoints[0], n.y - tf.max_ttime_interval),
                    (hpoints[0], n.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2.0
                ))
                # left to top
                dwg.add(dwg.line(
                    (hpoints[0], n.y - tf.max_ttime_interval),
                    (hpoints[0], top.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2.0
                ))
                # right to mid
                dwg.add(dwg.line(
                    (cpoints[3], n.y),
                    (cpoints[3], n.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2.0
                ))
                # right mid
                dwg.add(dwg.line(
                    (cpoints[3], n.y - tf.max_ttime_interval),
                    (hpoints[1], n.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2.0
                ))
                # right to top
                dwg.add(dwg.line(
                    (hpoints[1], n.y - tf.max_ttime_interval),
                    (hpoints[1], top.y - tf.max_ttime_interval),
                    stroke='#5276A3',
                    stroke_width=2.0
                ))
                # label
                dwg.add(dwg.text(
                    text=n.name,
                    insert=(n.x - 20, n.y + 20),
                    fill='#325683',
                    font_size='40px'
                ))
            print(' s {0}: '.format(repr(n)))

    if tf.parasite_nodes:
        print('\ndrawing svg parasite nodes')
        for n in pseudo_root.traverse(strategy='postorder'):
            label = True
            if hasattr(n, 'parasites'):
                print('  s {0} parasite nodes:'.format(n.name))
                for p in n.parasites:
                    color = tf.gtree_color_pool[
                        sprime.gtrees.index(p[0].get_tree_root())
                    ]
                    if p[0].name.startswith('loss'):
                        fill = 'none'
                    else:
                        fill = color
                    point = dwg.add(
                        dwg.circle(
                            center=(p[0].x, p[0].y),
                            r=4,
                            fill=fill,
                            stroke=color,
                            stroke_width=1.5
                        )
                    )
                    # label?
                    if label:
                        if p[0].is_leaf() or p[0].mapped_to[0][0].name == '-1':
                            angle = 30
                        else:
                            angle = 0
                        item = dwg.add(dwg.text(
                            text='{0} {1}'.format(
                                p[0].name, hex(p[0].__hash__())
                            ),
                            insert=(
                                p[0].x + tf.p_xoffset,
                                p[0].y + tf.p_yoffset
                            ),
                            fill='#4C4C4C',
                            font_size='8px',
                        ))
                        Transform.rotate(
                            item,
                            angle=angle,
                            center=(
                                p[0].x + tf.p_xoffset, p[0].y + tf.p_yoffset
                            )
                        )
                    print('    g {0}: {1}'.format(repr(p), point))
                    print('      x = {0:.2f}, y = {1:.2f}'.format(
                        p[0].x, p[0].y)
                    )

    if tf.parasite_edges:
        print('\ndrawing svg parsite edges')
        for n in pseudo_root.traverse(strategy='postorder'):
            if n.is_root():
                print('skipping root')
                continue
            if hasattr(n, 'parasites'):
                for p in n.parasites:
                    color = tf.gtree_color_pool[
                        sprime.gtrees.index(p[0].get_tree_root())
                    ]
                    if p[0].is_leaf():
                        continue
                    event = p[1]
                    print(' A \'{0}\' node {1} mapped_to {2}'.format(
                        p[1], repr(p[0]), repr(p[0].mapped_to[0][0])
                    ))
                    print(' with {0} children:'.format(len(p[0].children)))
                    children = p[0].children
                    if event in ['S', 'SL', 'D']:
                        for c in children:
                            points = [
                                (c.x, c.y),
                                (c.x, p[0].y),
                                (p[0].x, p[0].y)
                            ]
                            print('   -drawing: {0}'.format(points))
                            dwg.add(dwg.polyline(
                                points=points,
                                fill='none',
                                stroke=color,
                                stroke_width='2',
                            ))
                    elif event in ['DEAD0']:
                        assert len(children) == 1, exit('DEAD0 children error')
                        points = [
                            (p[0].x, p[0].y),
                            (children[0].x, children[0].y)
                        ]
                        print('   -drawing: {0}'.format(points))
                        dwg.add(dwg.polyline(
                            points=points,
                            fill='none',
                            stroke=color,
                            stroke_width='2',
                        ))
                    elif p[1] in ['TLFD']:
                        assert len(p[0].children) == 1, exit('TLFD children error')
                        points = [
                            (p[0].x, p[0].y),
                            (children[0].x, p[0].y),
                            (children[0].x, children[0].y),
                        ]
                        print('   -drawing: {0}'.format(points))
                        dwg.add(dwg.polyline(
                            points=points,
                            fill='none',
                            stroke=color,
                            stroke_width='2',
                        ))
                    elif p[1] in ['T']:
                        assert len(p[0].children) == 2, exit('T children error')
                        for c in children:
                            if c.mapped_to[0][0] == p[0].mapped_to[0][0]:
                                # same host
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, c.y)
                                ]
                                print('   -drawing: {0}'.format(points))
                                dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                ))
                            else:
                                # different
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, p[0].y),
                                    (c.x, c.y),
                                ]
                                print('   -drawing: {0}'.format(points))
                                dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                ))
                    elif event in ['TL']:
                        assert len(children) == 2, exit('TL children error')
                        for c in children:
                            if c.mapped_to[0][0] == p[0].mapped_to[0][0]:
                                # same host
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, c.y),
                                ]
                                dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                ))
                            else:
                                # different
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, p[0].y),
                                    (c.x, c.y)
                                ]
                                dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                ))
                    elif event in ['TTD', 'TLTD']:
                        for c in children:
                            if (p[0].mapped_to[0][0] == c.mapped_to[0][0]):
                                # vertical child
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, c.y)
                                ]
                                print('   -drawing (v): {0}  {1}'.format(
                                    points, repr(c)
                                ))
                                line = dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                ))
                            else:
                                # horizontal child
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, p[0].y),
                                    (c.x, c.y)
                                ]
                                print('   -drawing (h): {0}  {1}'.format(
                                    points, repr(c)
                                ))
                                line = dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                    stroke_dasharray="10,10"
                                ))
                                line['marker-end'] = arrows[
                                    sprime.gtrees.index(p[0].get_tree_root())
                                ].get_funciri()
                    elif event in ['TFD']:
                        for c in children:
                            if (p[0].mapped_to[0][0] == c.mapped_to[0][0]):
                                # vertical child
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, c.y)
                                ]
                                print('   -drawing (v): {0}  {1}'.format(
                                    points, repr(c)
                                ))
                                line = dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                ))
                            else:
                                # horizontal child
                                points = [
                                    (p[0].x, p[0].y),
                                    (c.x, p[0].y),
                                    (c.x, c.y),
                                ]
                                print('   -drawing (h): {0}  {1}'.format(
                                    points, repr(c)
                                ))
                                line = dwg.add(dwg.polyline(
                                    points=points,
                                    fill='none',
                                    stroke=color,
                                    stroke_width='2',
                                    stroke_dasharray="10,10"
                                ))
                                line['marker-end'] = arrows[
                                    sprime.gtrees.index(p[0].get_tree_root())
                                ].get_funciri()

                    else:
                        print(p)
    print('SAVING!')
    # save drawing
    dwg.save()
