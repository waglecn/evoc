"""functions for manipulating types"""
import os
from evoc import db


def init_cli(subparser):
    """
    """

    import argparse

    subparsers = []

    print_types_parser = subparser.add_parser(
        'print_types',
        help="Print types froma a db"
    )
    print_types_parser.add_argument(
        'db',
        help='An evoc db (filename)',
        type=argparse.FileType('r', encoding='utf-8')
    )
    print_types_parser.add_argument(
        'ids',
        help='zero or more type ids from the database',
        nargs='*',
        default=None,
        type=int
    )
    print_types_parser.add_argument(
        '--excluded',
        help='type ids to exclude',
        nargs='*',
        default=None,
        type=int
    )
    print_types_parser.add_argument(
        '--graphviz',
        help='graphviz',
        action="store_true",
        default=False
    )
    print_types_parser.add_argument(
        '--unjoin',
        help='unjoin from parent',
        action="store_true",
        default=False
    )
    print_types_parser.add_argument(
        '--children',
        help='only report children of ids',
        action="store_true",
        default=False,
        dest='children'
    )
    print_types_parser.add_argument(
        '--parents',
        help='only report parents of ids',
        action="store_true",
        default=False,
        dest='parents'
    )
    subparsers.append(print_types_parser)

    load_type_thv_parser = subparser.add_parser(
        'load_type_thv',
        help='load and/or update from thv file'
    )
    load_type_thv_parser.add_argument(
        'db',
        help='An evoc db (filename)',
    )
    load_type_thv_parser.add_argument(
        'thv_filename'
    )
    load_type_thv_parser.add_argument(
        '--update_types',
        default=False,
        action='store_true'
    )
    load_type_thv_parser.add_argument(
        '--update_rels',
        default=False,
        action='store_true'
    )
    subparsers.append(load_type_thv_parser)

    return subparsers


def check_children(connection, parent_id, rel_id, level, excluded):
    """recursive function to check children of every parent term"""

    # makes sure the item actually exists
    try:
        type_item = db.check_type(connection, type_id=parent_id)[0]
    except Exception as e:
        print(str(e), parent_id)
        exit(0)

    new_links = []
    print('{0}{1}'.format('\t' * level, type_item))
    rels = db.check_relationship(
        connection, object_id=parent_id, type_id=rel_id
    )
    if rels is not False:
        for rel in rels:
            if (parent_id, rel[2]) not in new_links:
                new_links.append((parent_id, rel[2]))
            if rel[2] not in excluded:
                new_links += check_children(
                    connection, rel[2], rel_id, level + 1, excluded
                )
    return new_links


def print_types_rels(
    db_filename, ids, children, parents, graphviz, excluded_ids, unjoin
):
    """print types and relationships"""
    import sys

    connection = db.init_db(db_filename)

    rel_type = db.check_type(connection, name='is_a')
    rel_id = rel_type[0][0]

    excluded = excluded_ids
    if excluded_ids is None:
        excluded = []

    if ids == []:
        print('No ids specified, getting all types...', file=sys.stderr)
        all_types = db.check_type(connection)
    else:
        all_types = []
        for i in ids:
            all_types += db.check_type(connection, type_id=i)

    root_types = []
    other_types = []

    for t in all_types:
        if len(
            db.check_relationship(connection, subject_id=t[0], type_id=rel_id)
        ) == 0:
            root_types.append(t)
        else:
            other_types.append(t)
    print('have {0} types'.format(len(all_types)), file=sys.stderr)

    if len(root_types) == 0:
        print('no root types, using interior nodes'.format(
            len(all_types)
        ), file=sys.stderr)
        root_types = other_types

    if unjoin:
        new_roots = []
        for r in root_types:
            result = db.check_relationship(
                connection, object_id=r[0], type_id=rel_id
            )
            if result is not False:
                for res in result:
                    new_roots.append(
                        db.check_type(connection, type_id=res[2])[0]
                    )
        root_types = new_roots

    links = []
    for r in root_types:
        links += check_children(connection, r[0], rel_id, 0, excluded)
    print('have {0} links'.format(len(links)), file=sys.stderr)
    other_types = [] + [
        db.check_type(connection, type_id=l[1])[0] for l in links
    ]

    # draw graph
    if graphviz:
        from evoc.cluster import cmap
        import progress.bar
        try:
            import pygraphviz as pgv
        except ImportError as e:
            # graphviz not found
            sys.exit(str(e))

        # colors all descendants by parent
        ancestor_colors = {}
        for t_id in cmap:
            color = cmap[t_id]['color']
            ancestor_colors[t_id] = color
            new_links = check_children(connection, t_id, rel_id, 0, [])
            for n in new_links:
                ancestor_colors[n[1]] = color

        all_ids = [t[0] for t in root_types + other_types]

        pbar = progress.bar.Bar(' nodes.. ', max=len(root_types + other_types))
        G = pgv.AGraph(directed=False, strict=False)
        for t in root_types + other_types:
            c = r"#CFCFCFFF"
            if t[0] in ancestor_colors:
                c = ancestor_colors[t[0]]
                c = r'#' + c[2:] + 'F0'
            G.add_node(t[0], shape='point', id=t[1], color=c)
            pbar.next()
        pbar.finish()

        pbar = progress.bar.Bar(' edges... ', max=len(links))
        for l in links:
            if l[0] in all_ids and l[1] in all_ids:
                G.add_edge(l[1], l[0], color='#00000035')
            pbar.next()
        pbar.finish()
        G.layout(prog="neato")
        G.draw("types.png")


def load_type_thv(dbfilename, thv_filename, update_types, update_rels):
    """
    """
    connection = db.init_db(dbfilename)

    cur = connection.cursor()

    with open(thv_filename, 'r') as inh:
        data = inh.readlines()

    n_changes = []
    r_changes = []

    stack = []
    last_indent = 0
    for line in data:
        if len(line.strip()) == 0 or line.startswith('#'):
            print('skipped line: {0}'.format(line))
            continue
        rel_item = None
        item = line.rstrip().split('\t')

        # update indent
        current_indent = 0
        for i in item:
            if i == '':
                current_indent += 1
            else:
                break

        # build item from line
        item = item[current_indent:]
        if len(item) == 1:
            # single
            root_item = item[0]
            # default rel_item
            rel_item = db.check_type(connection, name='is_a')[0]
        elif len(item) == 2:
            # item with rel
            root_item = item[0]
            rel_item = item[1]
            if len(rel_item) <= 10:
                # assume it is a number
                rel_item = db.check_type(connection, type_id=int(rel_item))[0]
            # else:
            #     # assume it is an item, UGLY
            #     rel_item = eval(rel_item)
        else:
            # problem
            exit('problem with item: {0}'.format(item))
        root_item = eval(root_item)
        assert rel_item is not None, exit('rel_item is None')

        # update root item in db
        old_item = db.check_type(connection, type_id=root_item[0])[0]

        if old_item != root_item:
            cmd = """
                UPDATE type SET name = ?, description = ?
                WHERE type_id = ?
            """
            name_change = 'found name change: {0} -> {1}'.format(
                old_item, root_item
            )
            n_changes.append(root_item)
            print(name_change)

        if current_indent > last_indent:
            # do something with item
            stack.append(root_item)

        elif current_indent == last_indent:
            if len(stack) > 0:
                stack.pop()
            stack.append(root_item)
        elif current_indent < last_indent:
            while len(stack) > current_indent:
                stack.pop()
            stack.append(root_item)

        if current_indent > 0:
            parent = stack[-2]
            # check rel
            rel = db.check_relationship(
                connection,
                object_id=parent[0],
                subject_id=root_item[0]
            )
            if not rel:
                rel_change = 'found change: {0} {1} {2}'.format(
                    root_item,
                    rel_item[1],
                    parent
                )
                r_changes.append((root_item[0], rel_item[0], parent[0]))
                print(rel_change)
            else:
                print('know about: {0} {1} {2}'.format(
                    root_item,
                    rel_item[1],
                    parent
                ))
        # finish loop by updating indent level
        last_indent = current_indent

    # backup db
    if update_types or update_rels:
        print('backing up db....')
        counter = 1
        while os.path.exists('backup_type.{0}'.format(counter)):
            counter += 1
        db.backup_db(dbfilename, 'backup_type.{0}'.format(counter))

    print('\nThere are {0} pending name changes'.format(len(n_changes)))
    # update name changes
    if update_types and len(n_changes) > 0:
        for n in n_changes:
            cmd = """
                UPDATE type set name = ?, description = ?
                WHERE type_id = ?
            """
            try:
                cur.execute(cmd, (n[1], n[2], n[0]))
            except Exception as e:
                print(str(e))
                print(n)
                exit()
    print('\nThere are {0} pending rel changes'.format(len(r_changes)))

    # update rel changes
    if update_rels:
        # blow up rel_table
        cmd = """
            DELETE FROM type_relationship WHERE relationship_id = ?
        """
        cur.execute(cmd, ('*',))
        connection.commit()
        for r in r_changes:
            db.add_relationship(
                connection,
                object_id=r[2],
                subject_id=r[0],
                type_id=r[1]
            )
    connection.commit()
