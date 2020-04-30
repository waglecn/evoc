"""Command-line interface definiition"""

import argparse
import evoc.utils_reconciliation
import evoc.domain
import evoc.cluster
import evoc.type_rel


def cli_setup(inargs=None):
    argparser = argparse.ArgumentParser(prog='evoc')

    subparser = argparser.add_subparsers(
        title='commands',
        description='available commands',
        dest='cmd',
        metavar='<command>'
    )

    # utils_reconcilation_subparsers =
    evoc.utils_reconciliation.init_cli(
        subparser
    )
    # cluster_subparsers =
    evoc.cluster.init_cli(
        subparser
    )
    # domain_subparsers =
    evoc.domain.init_cli(
        subparser
    )
    # types_subparsers =
    evoc.type_rel.init_cli(
        subparser
    )

    if inargs is None:
        import sys
        inargs = sys.argv[1:]

    if len(inargs) == 0:
        argparser.print_help()

    args = argparser.parse_args(inargs)
    dispatch(args)


def dispatch(args):
    """command dispatcher"""

    if args.cmd == 'subdivide':
        import ete3
        print(
            evoc.utils_reconciliation.subdivide_tree(
                ete3.Tree(args.species_tree_file[0].name, format=1)
            ).get_ascii(show_internal=True),
            file=args.output
        )
    if args.cmd == 'print_cluster':
        print(args)
        evoc.cluster.print_cluster(
            args.db.name,
            args.cluster_id,
        )
    if args.cmd == 'draw_domain':
        print(args)
        evoc.domain.draw_domain(
            args.db.name,
            args.gene_id_list,
            args.output.name,
            args.format
        )
    if args.cmd == 'print_domain':
        print(args)
        evoc.domain.print_domain(
            args.db.name,
            args.gene_id_list,
            args.show_whole
        )
    if args.cmd == 'print_types':
        evoc.type_rel.print_types_rels(
            args.db.name,
            args.ids,
            args.children,
            args.parents,
            args.graphviz,
            args.excluded,
            args.unjoin
        )
    if args.cmd == 'load_type_thv':
        print(args)
        evoc.type_rel.load_type_thv(
            args.db,
            args.thv_filename,
            args.update_types,
            args.update_rels
        )
    if args.cmd == 'rec':
        evoc.utils_reconciliation.do_rec(
            args.stree_file.name,
            args.gtree_file.name,
            args.outdir,
            suffix=args.suffix
        )
    if args.cmd == 'recon_process':
        import ete3
        pseudo_root = evoc.utils_reconciliation.subdivide_tree(
            ete3.Tree(args.stree_file.name, format=1)
        )
        gtree = evoc.utils_reconciliation.process_recon(
            pseudo_root, args.recon_file.name
        )
        print(gtree, file=args.output)
    if args.cmd == 'recon_collect':
        import ete3
        pseudo_root = evoc.utils_reconciliation.subdivide_tree(
            ete3.Tree(args.stree_file.name, format=1)
        )
        gtrees = [
            evoc.utils_reconciliation.process_recon(
                pseudo_root, g
            ) for g in args.recons
        ]
        pseudo_root = evoc.utils_reconciliation.collect_onto_sprime(
            pseudo_root, gtrees
        )
    if args.cmd == 'recon_coords':
        import ete3
        pseudo_root = evoc.utils_reconciliation.subdivide_tree(
            ete3.Tree(args.stree_file.name, format=1)
        )
        gtrees = [
            evoc.utils_reconciliation.process_recon(
                pseudo_root, g
            ) for g in args.recons
        ]
        pseudo_root = evoc.utils_reconciliation.collect_onto_sprime(
            pseudo_root, gtrees
        )
        pseudo_root = evoc.utils_reconciliation.determine_coordinates(
            pseudo_root
        )
    if args.cmd == 'draw_recon':
        import ete3
        pseudo_root = evoc.utils_reconciliation.subdivide_tree(
            ete3.Tree(args.stree_file.name, format=1)
        )
        gtrees = [
            evoc.utils_reconciliation.process_recon(
                pseudo_root, g
            ) for g in args.recons
        ]
        pseudo_root = evoc.utils_reconciliation.collect_onto_sprime(
            pseudo_root, gtrees
        )
        pseudo_root = evoc.utils_reconciliation.determine_coordinates(
            pseudo_root
        )
        evoc.utils_reconciliation.svgdraw(pseudo_root, args.outfile.name)
    if args.cmd == 'grid_summary':
        evoc.utils_reconciliation.grid_summary(
            args.recon_summary, args.outfile
        )
    if args.cmd == 'draw_cluster':
        print(args)
        evoc.cluster.draw_cluster(
            args.db.name,
            args.cluster_id,
            args.output,
            args.start,
            args.end,
            args.draw_domains,
            args.gb
        )


def main(args=None):
    if args is None:
        cli_setup()
