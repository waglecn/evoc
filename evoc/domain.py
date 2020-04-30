"""functions for manipulating domains"""
from evoc import db


def init_cli(subparser):
    """
    """

    import argparse

    subparsers = []

    draw_domain_parser = subparser.add_parser(
        'draw_domain',
        help='Draw a domain from a db given one or more gene_id'
    )
    draw_domain_parser.add_argument(
        'db',
        help='An evoc db (filename)',
        type=argparse.FileType('r', encoding='utf-8')
    )
    draw_domain_parser.add_argument(
        '-g', '--gene_id',
        metavar='id',
        help='one or more gene_ids for which domains are to be drawn',
        nargs='+',
        type=int,
        dest='gene_id_list'
    )
    draw_domain_parser.add_argument(
        '--wide',
        help='Draw all genes in one row',
        action='store_const',
        const='wide',
        dest='format',
        default='tall'
    )

    draw_domain_parser.add_argument(
        '-o', '--out',
        help='output to a file',
        type=argparse.FileType('w', encoding='utf-8'),
        dest='output',
        required=True
    )
    subparsers.append(draw_domain_parser)

    print_domain_parser = subparser.add_parser(
        'print_domain',
        help='Display a domain from a db given a gene_id'
    )
    print_domain_parser.add_argument(
        'db',
        help='An evoc db (filename)',
        type=argparse.FileType('r', encoding='utf-8')
    )
    print_domain_parser.add_argument(
        '-g', '--gene_id',
        metavar='id',
        help='one or more gene_ids for which domains are to be drawn',
        nargs='+',
        dest='gene_id_list'
    )
    print_domain_parser.add_argument(
        '--whole',
        help="show whole domains",
        default=False,
        action='store_true',
        dest='show_whole'
    )
    subparsers.append(print_domain_parser)

    return subparsers


class domainFormat(object):
    trackWidth = 2000
    trackHeight = 75
    label_height = 0.5 * trackHeight * 0.75
    label_y_offset = 0.33 * label_height
    track_y_spacing = 12
    track_x_spacing = 50

    corner_radius = 15.0

    xScale = 0.33

    stroke_color = '#808080'
    fill_color = '#808080'
    text_stroke = '#808080'
    text_fill = '#808080'


def d_ancestors(connection, domain_type_id):
    # print('considering domain {0}'.format(domain_type_id))
    stack = [domain_type_id]
    collected = []
    while len(stack) > 0:
        # print('stack: {0}'.format(stack))
        d = stack.pop()
        # print('  working on {0}'.format(d))
        d_rel_result = db.check_relationship(
            # rel_type 3 = is_a
            connection, subject_id=d, type_id=3
        )
        if not d_rel_result:
            d_rel_result = []
            # print('  none found')
            continue
        for r in d_rel_result:
            # print(r)
            # print('  adding {0} to stack'.format(r[1]))
            stack.append(r[1])
            type_result = db.check_type(connection, type_id=r[1])
            # print(type_result)
            collected += [t for t in type_result if t not in collected]

    # print(collected)
    return collected


def draw_domain(dbfilename, gene_id_list, outfilename, tformat):
    """function that draws a domain given a gene_id"""

    import svgwrite

    show_whole = False

    parts = {
        # NRPS domains
        29: {'label': 'AMP-binding',
             'short-label': 'A',
             'fill': '#227722',
             'stroke': '#227722',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
        4403: {'label': 'A-PCPfill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        21: {'label': 'condensation',
             'short-label': 'C',
             'fill': '#36BC36',
             'stroke': '#36BC36',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
        6563: {'label': 'E-CondFill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        6002: {'label': 'E-CtermComFill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        28: {'label': 'Epimerization',
             'short-label': 'E',
             'fill': '#A3F39D',
             'stroke': '#A3F39D',
             'text_fill': '#252525',
             'text_stroke': '#252525'},
        34: {'label': 'NRPS-COM_Cterm',
             'short-label': '',
             'fill': '#EEEEEE',
             'stroke': '#333333',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
        33: {'label': 'NRPS-COM_Nterm',
             'short-label': '',
             'fill': '#EEEEEE',
             'stroke': '#333333',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
        5042: {'label': 'NRPSCtermFill_domain',
               'short-label': '',
               'fill': '#EEEEEE',
               'stroke': '#333333',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        4954: {'label': 'NRPSNtermFill_domain',
               'short-label': '',
               'fill': '#EEEEEE',
               'stroke': '#333333',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        4400: {'label': 'Cond-Afill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        6587: {'label': 'PCP-CondFill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        6462: {'label': 'PCP-Efill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        4404: {'label': 'PCP-Xfill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        31: {'label': 'PCP',
             'short-label': 'T',
             'fill': '#0000FF',
             'stroke': '#0000FF',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
        4405: {'label': 'X-TEfill',
               'short-label': '',
               'fill': '#606060',
               'stroke': '#606060',
               'text_fill': '#FFFFFF',
               'text_stroke': '#FFFFFF'},
        26: {'label': 'X',
             'short-label': 'X',
             'fill': '#22E68B',
             'stroke': '#22E68B',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
        72: {'label': 'Thioesterase',
             'short-label': 'TE',
             'fill': '#FFA500',
             'stroke': '#FFA500',
             'text_fill': '#FFFFFF',
             'text_stroke': '#FFFFFF'},
    }

    connection = db.init_db(dbfilename)
    cur = connection.cursor()

    gene_domains = []
    for g in gene_id_list:
        # do something
        cmd = """
            SELECT domain.domain_id, domain.start, domain.end,
                type.type_id, type.name
            FROM domain
            JOIN type ON domain.type_id = type.type_id
            WHERE domain.source_gene_id = ?
        """
        where = (g,)
        if not show_whole:
            cmd += """ AND NOT type.name GLOB ? """
            where = (g, '*_whole')

        gene_domains.append([d for d in cur.execute(cmd, where).fetchall()])

    df = domainFormat()

    # domains are now loaded
    dlengths = [g[-1][2] - g[0][1] for g in gene_domains]
    max_length = max(dlengths)

    # initialize area
    if tformat == 'tall':
        df.trackWidth = 1.2 * df.xScale * max_length
        dwg_height = (len(gene_domains) * df.trackHeight) + \
            ((len(gene_domains) - 1) * df.track_y_spacing)
    elif tformat == 'wide':
        df.trackWidth = sum(dlengths) * df.xScale + \
            (len(dlengths) - 1) * df.track_x_spacing
        dwg_height = 1.0 * df.trackHeight

    dwg_width = df.trackWidth
    dwg = svgwrite.Drawing(
        filename=outfilename,
        size=('{0}px'.format(dwg_width), '{0}px'.format(dwg_height))
    )

    for g in gene_domains:
        i = gene_domains.index(g)
        xoffset = 0
        if tformat == 'wide':
            track_center_y = 0.5 * df.trackHeight
        elif tformat == 'tall':
            track_center_y = ((i + 1) * df.trackHeight) + \
                (i * df.track_y_spacing) - (0.5 * df.trackHeight)
        print('track {0} center y: {1}'.format(i, track_center_y))

        for d in g:
            # get ancestors
            print(d)
            d_anc = d_ancestors(connection, d[3])

            # translate coordinates
            if tformat == 'wide':
                xoffset = sum(
                    [dlengths[j] for j in range(0, i)]
                ) * \
                    df.xScale + \
                    (i * df.track_x_spacing)

            dwidth = (d[2] - d[1] + 1.0) * df.xScale
            x = xoffset + d[1] * df.xScale
            cx = x + (0.5 * dwidth)
            cy = track_center_y

            # add the element
            fill_color = df.fill_color
            stroke_color = df.stroke_color
            text_fill = df.text_fill
            text_stroke = df.text_stroke
            large_label = ''
            for a in d_anc:
                if 'AMP-binding' in a:
                    print(d_anc)
                    large_label = '({0})'.format(
                        d_anc[0][1].split('_')[-1].capitalize()
                    )
                if a[0] in parts:
                    fill_color = parts[a[0]]['fill']
                    stroke_color = parts[a[0]]['stroke']
                    label = parts[a[0]]['short-label'] + large_label
                    text_fill = parts[a[0]]['text_fill']
                    text_stroke = parts[a[0]]['text_stroke']
                    break

            dwg.add(
                svgwrite.shapes.Rect(
                    insert=(x, cy - (0.25 * df.trackHeight)),
                    size=(dwidth, 0.5 * df.trackHeight),
                    rx=df.corner_radius, ry=df.corner_radius,
                    fill=fill_color,
                    stroke=stroke_color
                )
            )

            dwg.add(
                dwg.text(
                    label,
                    insert=(cx, cy + df.label_y_offset),
                    text_anchor='middle',
                    style='font-size:{0}px; '.format(
                        df.label_height
                    ) + 'font-family:Helvetica,sans-serif',
                    fill=text_fill,
                    stroke=text_stroke
                )
            )
            # print(
            #     'start {0} => {1}'.format(d[1], d[1] * df.xScale),
            #     'end {0} => {1}'.format(d[2], d[2] * df.xScale),
            #     'span {0} => {1}'.format(
            #         (d[2] - d[1] + 1.0) * df.xScale, dwidth
            #     ),
            # )

    dwg.save()


def print_domain(dbfilename, gene_id_list, show_whole):
    """function that displays domain architecture given one or more gene_ids"""

    connection = db.init_db(dbfilename)
    cur = connection.cursor()

    for g in gene_id_list:

        cmd = """
            SELECT gene.gb_id, gene.start, gene.end,
                type.type_id, type.name
            FROM gene
            JOIN type ON gene.type_id = type.type_id
            WHERE gene.gene_id = ?
        """
        result = [r for r in cur.execute(cmd, (g,)).fetchall()]

        print('\ngene_id: {0}\tType: ({1}), {2}'.format(
            result[0][0], result[0][3], result[0][4]
        ))
        print('length: {0} aa\tstart: {1}\tend: {2}'.format(
            (int(result[0][2]) - int(result[0][1]) + 1) / 3,
            result[0][1], result[0][2]
        ))
        print('{0}'.format('=' * 80))
        print('{0:<>5}\t{1:>5}\t{2:>5}\t{3:>5}\t{4:>5}\t{5:^20}'.format(
            'domain', 'start', 'end', 'length', 'type_id', 'type'
        ))
        print('{0}'.format('=' * 80))

        cmd = """
            SELECT domain.domain_id, domain.start, domain.end,
                type.type_id, type.name
            FROM domain
            JOIN type ON domain.type_id = type.type_id
            WHERE domain.source_gene_id = ?
        """
        where = (g,)
        if not show_whole:
            cmd += " AND NOT type.name GLOB ? "
            where = (g, '*_whole')

        result = cur.execute(cmd, where).fetchall()
        for r in result:
            print('{0:>5}\t{1:>5}\t{2:>5}\t{3:>5}\t{4:>5}\t{5}'.format(
                r[0], r[1], r[2],
                int(r[2]) - int(r[1]) + 1,
                r[3], r[4]
            ))
