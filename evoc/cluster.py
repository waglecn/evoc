"""functions for manipulating clusters"""
from evoc import db

cmap = {
    # Aromatic aa
    14043: {'label': 'DAHPS I', 'color': '#3333A0'},

    14043: {'label': 'DAHPS II', 'color': '#3333A5'},

    14046: {'label': 'ChorismateMutase_I_whole', 'color': '#3333AA'},

    14047: {'label': 'ChorismateMutase_II_whole', 'color': '#3333A9'},
    # RamoEX added to group 2
    14048: {'label': 'ChorismateMutase_II_whole', 'color': '#3333B0'},

    14080: {'label': 'pdh_whole I', 'color': '#333399'},

    # Hpg biosynthesis
    14062: {'label': 'HmaS_whole', 'color': '#333390'},

    14054: {'label': 'Hmo_whole', 'color': '#333388'},

    14076: {'label': 'HpgT_whole', 'color': '#333380'},

    # Dpg Biosynthesis
    14050: {'label': 'DpgA_whole', 'color': '#44AA44'},

    15069: {'label': 'DpgB_whole', 'color': '#429942'},

    15081: {'label': 'DpgC_whole', 'color': '#408840'},

    15087: {'label': 'DpgD_whole', 'color': '#387738'},

    # Bht biosynthesis
    13850: {'label': 'OxyD_whole', 'color': '#FFA010'},

    14120: {'label': 'Bhp_hydrolase_whole', 'color': '#FFB010'},

    15049: {'label': 'BpsD_whole', 'color': '#FFC010'},

    14135: {'label': 'beta-hydroxylase_whole', 'color': '#DDA500'},

    # Sugar biosnythesis + tailoring
    14102: {'label': 'evaA', 'color': '#FF0050'},
    14106: {'label': 'evaB', 'color': '#FF1055'},
    14108: {'label': 'evaC', 'color': '#FF2060'},
    14097: {'label': 'evaD', 'color': '#FF3065'},
    14111: {'label': 'sugar-4-Ketoreductas5', 'color': '#FF4050'},

    # NRPS domains
    14982: {'label': 'NRPS_whole', 'color': '#689DEE'},

    3942: {'label': 'AMP-binding', 'color': '#D44F44'},

    3948: {'label': 'condensation', 'color': '#4D4DCD'},

    3951: {'label': 'PCP', 'color': '#FFFF00'},

    3949: {'label': 'Epimerization', 'color': '#808080'},

    3950: {'label': 'Thioesterase', 'color': '#00C600'},

    3946: {'label': 'X', 'color': '#ADD8E6'},

    # AMTFILL

    # 4403: {'label': 'A-PCPfill',
    #        'color': '0x808080'},

    # ATEFill

    # 4400: {'label': 'Cond-Afill',
    #        'color': '0x808080'},

    # 6587: {'label': 'Cond-PCPFill',
    #        'color': '0x808080'},

    # 34: {'label': 'NRPS-COM_Cterm',
    #      'color': '0x808080'},

    # 6563: {'label': 'E-CondFill',
    #        'color': '0x808080'},

    # 6002: {'label': 'E-CtermComFill',
    #        'color': '0x808080'},

    # MT
    # MTPCP-Fill

    # 33: {'label': 'NRPS-COM_Nterm',
    #      'color': '0x808080'},

    # PCP CondFill

    # 6462: {'label': 'PCP-Efill',
    #        'color': '0x808080'},

    # PCPTEFill

    # 4404: {'label': 'PCP-Xfill',
    #        'color': '0x808080'},

    # 4397: {'label': 'XAFill',
    #        'color': '0x689DEE'},

    # 4405: {'label': 'X-TEfill',
    #        'color': '0x808080'},

    # Tailoring
    13817: {'label': 'MbtH_1_whole', 'color': '#BBBB00'},

    13822: {'label': 'Halogenase_1_whole', 'color': '#55FFFF'},

    # Acylation
    13827: {'label': 'PseudoAglyconeDeacetylase_1_whole', 'color': '#5A2616'},

    13835: {'label': 'Acyltransferase_1_whole', 'color': '#79321D'},

    13836: {'label': 'Acyltransferase_2_whole', 'color': '#9F4026'},

    # Crosslinking
    13846: {'label': 'P450_whole', 'color': '#AAFF00'},
    13847: {'label': 'OxyA_whole', 'color': '#AAFF22'},
    13849: {'label': 'OxyB_whole', 'color': '#AAFF44'},
    13848: {'label': 'OxyC_whole', 'color': '#AAFF66'},
    13851: {'label': 'OxyE_whole', 'color': '#AAFF88'},

    13872: {'label': 'GTF I', 'color': '#CC6666'},
    13873: {'label': 'GTF II', 'color': '#CC6667'},
    13874: {'label': 'GTF III', 'color': '#CC6668'},
    13875: {'label': 'GTF IV', 'color': '#CC6669'},
    13876: {'label': 'GTF V', 'color': '#CC6670'},
    13877: {'label': 'GTF VI', 'color': '#CC6671'},  # GTF II
    13878: {'label': 'GTF VII', 'color': '#CC6672'},
    13879: {'label': 'GTF VIII', 'color': '#CC6673'},
    13887: {'label': 'NAcGTF', 'color': '#CC6674'},

    13891: {'label': 'MBGTF_1_whole', 'color': '#CCAA80'},
    13892: {'label': 'MBGTF_2_whole', 'color': '#CCAA82'},
    13893: {'label': 'MBGTF_3_whole', 'color': '#CCAA84'},
    13894: {'label': 'MBGTF_4_whole', 'color': '#CCAA86'},
    13895: {'label': 'MBGTF_5_whole', 'color': '#CCAA88'},
    13896: {'label': 'MBGTF_6_whole', 'color': '#CCAA90'},
    13897: {'label': 'MBGTF_7_whole', 'color': '#CCAA92'},

    # Sulf1ation
    13901: {'label': 'Sulfotransferase_family_whole', 'color': '#FF88FF'},

    14017: {'label': 'Methyltransferase_I_whole', 'color': '#888802'},
    14018: {'label': 'Methyltransferase_II_whole', 'color': '#888804'},
    14020: {'label': 'Methyltransferase_IV_whole', 'color': '#888806'},
    14021: {'label': 'Methyltransferase_V_whole', 'color': '#888808'},
    14022: {'label': 'Methyltransferase_VI_whole', 'color': '#888810'},
    14024: {'label': 'Methyltransferase_VIII_whole', 'color': '#888812'},
    14025: {'label': 'Methyltransferase_IX_whole', 'color': '#888814'},

    14026: {'label': 'Methyltransferase X_whole', 'color': '#888816'},

    14019: {'label': 'Methyltransferase III_whole', 'color': '#888818'},

    14023: {'label': 'Methyltransferase VII whole', 'color': '#888020'},

    14029: {'label': 'O-Methyltransferase_I_whole', 'color': '#888022'},

    14030: {'label': 'O-Methyltransferase_II_whole', 'color': '#888024'},

    14031: {'label': 'O-Methyltransferase_III_whole', 'color': '#888026'},
    14032: {'label': 'OHneurosporine O-MT', 'color': '#888028'},

    # I,  II, III, IV, V, VI, VII
    14033: {'label': 'N-Methyltransferase', 'color': '#8B0000'},


    # Conserved Misc/Unknown
    # Export / Antiport
    13909: {'label': 'ABC_transporter_ATP_whole', 'color': '#555500'},

    13940: {'label': 'ABC_trans_permease', 'color': '#555501'},

    13965: {'label': 'ABC_trans_solute_binding', 'color': '#555502'},

    13982: {'label': 'cation antiporter', 'color': '#555503'},

    13980: {'label': 'cation symporter I', 'color': '#555504'},

    13981: {'label': 'cation symporter II', 'color': '#555505'},

    13997: {'label': 'AI-23 transporter I', 'color': '#555506'},

    13998: {'label': 'MFS_transporter', 'color': '#555507'},


    14120: {'label': 'AlphaBetaHydrolase_I_whole', 'color': '#FFFF00'},
    14121: {'label': 'AlphaBetaHydrolase_II_whole', 'color': '#FFFF01'},
    14122: {'label': 'AlphaBetaHydrolase_III_whole', 'color': '#FFFF02'},
    14124: {'label': 'AlphaBetaHydrolase_V_whole', 'color': '#FFFF03'},
    14127: {'label': 'AlphaBetaHydrolase_VIII_whole', 'color': '#FFFF04'},
    14128: {'label': 'AlphaBetaHydrolase_IX_whole', 'color': '#FFFF05'},
    14129: {'label': 'AlphaBetaHydrolase_X_whole', 'color': '#FFFF06'},
    14132: {'label': 'AlphaBetaHydrolase_XIII_whole', 'color': '#FFFF07'},

    14141: {'label': 'ferredoxin', 'color': '#EEEC9F'},

    # Resistance
    14157: {'label': 'VanH_I whole', 'color': '#BB00FF'},
    14158: {'label': 'VanH_II whole', 'color': '#BB00FE'},
    14159: {'label': 'VanH_III whole', 'color': '#BB00FD'},
    14161: {'label': 'VanH_V whole', 'color': '#BB00FC'},

    14162: {'label': 'VanA_whole', 'color': '#AB20EE'},

    14165: {'label': 'VanX_I whole', 'color': '#CD00FF'},

    14168: {'label': 'VanY_I_whole', 'color': '#CE00FF'},

    14175: {'label': 'PG binding I', 'color': '#8800FF'},

    14176: {'label': 'PG binding II', 'color': '#8800EE'},

    14177: {'label': 'PG binding III', 'color': '#8800DD'},

    14183: {'label': 'MurF_whole', 'color': '#4422CC'},

    14186: {'label': 'MurG_whole', 'color': '#4422BB'},

    14189: {'label': 'FemAK VanJ_whole', 'color': '#4422AA'},

    14192: {'label': 'DDcarboxypeptidase', 'color': '#4422FF'},

    14197: {'label': 'DDligase', 'color': '#4422EE'},

    # Regulation
    14203: {'label': 'StrR_whole', 'color': '#5520FA'},

    14221: {'label': 'RespReg_whole', 'color': '#5500FF'},

    14236: {'label': 'HisK_whole', 'color': '#5500EE'},
}


def init_cli(subparser):
    """
    """

    import argparse

    subparsers = []

    draw_cluster_parser = subparser.add_parser(
        'draw_cluster',
        help='Draw a cluster from a db'
    )
    draw_cluster_parser.add_argument(
        'db',
        help='An evoc db (filename)',
        type=argparse.FileType('r', encoding='utf-8')
    )
    draw_cluster_parser.add_argument(
        'cluster_id',
        help='Cluster id to draw',
    )
    draw_cluster_parser.add_argument(
        '-f', '--from',
        help='starting gene_id to begin cluster',
        required=False,
        default=None,
        dest='start'
    )
    draw_cluster_parser.add_argument(
        '-t', '--to',
        help='last gene_id to end cluster',
        required=False,
        default=None,
        dest='end'
    )
    draw_cluster_parser.add_argument(
        '-o', '--out',
        help='output to a file',
        type=argparse.FileType('w', encoding='utf-8'),
        dest='output',
    )
    draw_cluster_parser.add_argument(
        '-gb',
        help="filter by optional gb_id",
        dest='gb',
        default=None
    )
    draw_cluster_parser.add_argument(
        '--draw_domains',
        action='store_true',
        dest='draw_domains',
        default=False
    )
    subparsers.append(draw_cluster_parser)

    print_cluster_parser = subparser.add_parser(
        'print_cluster',
        help='Display a summary of a cluster'
    )
    print_cluster_parser.add_argument(
        'db',
        help='An evoc db (filename)',
        type=argparse.FileType('r', encoding='utf-8')
    )
    print_cluster_parser.add_argument(
        'cluster_id',
        help='Cluster id to display',
    )
    subparsers.append(print_cluster_parser)

    return subparsers


def family_check(connection, gene_id):

    # cur = connection.cursor()
    # get gene info
    gene_result = db.check_gene(connection, gene_id=gene_id)
    # print(gene_result, 'XXX')
    gene_item = list(gene_result[0])
    type_result = db.check_type(connection, type_id=gene_item[3])
    gene_item = gene_item + list(type_result[0])
    # print(type_result)
    domain_result = db.check_domain(connection, source_gene_id=gene_id)
    # print(domain_result)
    domains = []
    for d in domain_result:
        d_type_result = db.check_type(connection, type_id=d[2])
        domains.append({
            'domain_id': d[0],
            'type_id': d_type_result[0][0],
            'name': d_type_result[0][1],
            'start': d[3],
            'end': d[4]
        })

    return gene_item, domains


def feature_color(connection, genes, domains):
    # the type_id -> color mapping table
    # cmap = {
    #     # NRPS domains
    #     29: {'label': 'AMP-binding',
    #          'color': colors.red},
    #     4403: {'label': 'A-PCPfill',
    #            'color': colors.grey},
    #     21: {'label': 'condensation',
    #          'color': colors.blue},
    #     6563: {'label': 'E-CondFill',
    #            'color': colors.grey},
    #     6002: {'label': 'E-CtermComFill',
    #            'color': colors.grey},
    #     28: {'label': 'Epimerization',
    #          'color': colors.grey},
    #     34: {'label': 'NRPS-COM_Cterm',
    #          'color': colors.grey},
    #     33: {'label': 'NRPS-COM_Nterm',
    #          'color': colors.grey},
    #     5042: {'label': 'NRPSCtermFill_domain',
    #            'color': colors.grey},
    #     4954: {'label': 'NRPSNtermFill_domain',
    #            'color': colors.grey},
    #     4400: {'label': 'Cond-Afill',
    #            'color': colors.grey},
    #     6587: {'label': 'PCP-CondFill',
    #            'color': colors.grey},
    #     6462: {'label': 'PCP-Efill',
    #            'color': colors.grey},
    #     4404: {'label': 'PCP-Xfill',
    #            'color': colors.grey},
    #     31: {'label': 'PCP',
    #          'color': colors.yellow},
    #     4405: {'label': 'X-TEfill',
    #            'color': colors.grey},
    #     26: {'label': 'X',
    #          'color': colors.lightblue},
    #     72: {'label': 'Thioesterase',
    #          'color': colors.green},
    #     4951: {'label': 'NRPS_whole',
    #            'color': '0x689DEE'},
    #     4397: {'label': 'Mod7_whole',
    #            'color': '0x689DEE'},

    #     # Bht-BpsD related domains
    #     6805: {'label': 'BpsD_CtermFill',
    #            'color': '0xCA8000'},
    #     6724: {'label': 'BpsD_NtermFill',
    #            'color': '0xA87000'},
    #     3989: {'label': 'OxyD_whole',
    #            'color': '0xFFA500'},
    #     1810: {'label': 'Bhp_hydrolase_whole',
    #            'color': '0xDF8600'},
    #     6723: {'label': 'BpsD_whole',
    #            'color': '0xEF9700'},
    #     # Bht biosynthesis
    #     4446: {'label': 'beta-hydroxylase_whole',
    #            'color': '0xFFBF00'},

    #     # Sugar biosnythesis + tailoring
    #     4590: {'label': 'dTDP-rhammnoseEpimerase_1_whole',
    #            'color': '0xFF0000'},
    #     4498: {'label': 'Glycosyltransferase_1_whole',
    #            'color': '0xFF0000'},
    #     4593: {'label': '4KetoReductase_1_whole',
    #            'color': '0xFF0000'},
    #     4596: {'label': 'AldoKetoReductase_whole',
    #            'color': '0xFF0000'},
    #     4588: {'label': 'Aldolase_1_whole',
    #            'color': '0xFF0000'},
    #     4494: {'label': 'Mannosyltransferase_1_whole',
    #            'color': '0xFF0000'},
    #     4496: {'label': 'MannosylTransferase_2_whole',
    #            'color': '0xFF0000'},
    #     4597: {'label': 'NDPHexoseDehydratase_whole',
    #            'color': '0xFF0000'},
    #     4485: {'label': 'O-Methyltransferase_1_whole',
    #            'color': '0xFF0000'},

    #     # Hpg biosynthesis
    #     4623: {'label': 'ChorismateMutase_1_whole',
    #            'color': '0x3333AA'},
    #     4642: {'label': 'ChorismateMutase_2_whole',
    #            'color': '0x3333A0'},
    #     76: {'label': 'pdh_whole',
    #          'color': '0x333399'},
    #     75: {'label': 'HmaS_whole',
    #          'color': '0x333390'},
    #     74: {'label': 'Hmo_whole',
    #          'color': '0x333388'},
    #     3803: {'label': 'HpgT_whole',
    #            'color': '0x333380'},

    #     # Dpg Biosynthesis
    #     3807: {'label': 'DpgA_whole',
    #            'color': '0x44AA44'},
    #     3808: {'label': 'DpgB_whole',
    #            'color': '0x429942'},
    #     3809: {'label': 'DpgC_whole',
    #            'color': '0x408840'},
    #     3810: {'label': 'DpgD_whole',
    #            'color': '0x387738'},

    #     # Sulfation
    #     4559: {'label': 'Sulfotransferase_family_1_whole',
    #            'color': '0xFF88FF'},
    #     4560: {'label': 'Sulfotransferase_family_2_whole',
    #            'color': '0xFF77FF'},
    #     # 4558: {'label': 'Sulfotransferase_family_whole',
    #     #        'color': '0xFFCCFF'},

    #     # Acylation
    #     4478: {'label': 'PseudoAglyconeDeacetylase_1_whole',
    #            'color': '0x5A2616'},
    #     4506: {'label': 'Acyltransferase_1_whole',
    #            'color': '0x79321D'},
    #     4507: {'label': 'Acyltransferase_2_whole',
    #            'color': '0x9F4026'},
    #     # 4505: {'label': 'Acyltransferase_family_whole',
    #     #        'color': '0xB35836'},

    #     # Halogenation
    #     4480: {'label': 'Halogenase_1_whole',
    #            'color': '0x55FFFF'},

    #     # Scaffold methylation
    #     4483: {'label': 'N-Methyltransferase_1_whole',
    #            'color': '0x8B0000'},
    #     4484: {'label': 'N-Methyltransferase_2_whole',
    #            'color': '0x8B0000'},

    #     # Conserved Misc/Unknown
    #     4599: {'label': 'AlphaBetaHydrolase_2_whole',
    #            'color': '0xFFFF00'},
    #     4592: {'label': 'CAminotransferase_1_whole',
    #            'color': '0xEEEE00'},
    #     4479: {'label': 'MbtH_1_whole',
    #            'color': '0xBBBB00'},
    #     4486: {'label': 'Methyltransferase_1_whole',
    #            'color': '0x888800'},

    #     # Crosslinking
    #     3986: {'label': 'OxyA_whole',
    #            'color': '0xAAFF00'},
    #     3987: {'label': 'OxyB_whole',
    #            'color': '0xAAFF11'},
    #     3988: {'label': 'OxyC_whole',
    #            'color': '0xAAFF22'},
    #     3990: {'label': 'OxyE_whole',
    #            'color': '0xAAFF33'},
    #     # 3985: {'label': 'P450_whole',
    #     #       'color': '0xAAFF44'},

    #     # Export / Antiport
    #     4448: {'label': 'ABC_transporter_1_whole',
    #            'color': '0x555500'},

    #     # Regulation
    #     4515: {'label': 'StrR_1_whole',
    #            'color': '0x1000FA'},

    #     # Resistance
    #     4601: {'label': 'PeptidoGlycanBindingProtein_1_whole',
    #            'color': '0xAA00FF'},
    #     4572: {'label': 'MurF_whole',
    #            'color': '0xAC01FF'},
    #     79: {'label': 'VanA_whole',
    #          'color': '0xAE00FF'},
    #     77: {'label': 'VanH_whole',
    #          'color': '0xBB00FF'},
    #     4564: {'label': 'VanJ_whole',
    #            'color': '0xBD00FF'},
    #     4566: {'label': 'VanR_whole',
    #            'color': '0xBF00FF'},
    #     4567: {'label': 'VanS_whole',
    #            'color': '0xCB00FF'},
    #     4565: {'label': 'VanX_whole',
    #            'color': '0xCD00FF'},
    #     4562: {'label': 'VanY_1_whole',
    #            'color': '0xCE00FF'},
    #     4563: {'label': 'VanY_2_whole',
    #            'color': '0xDA00FF'},
    # }

    # gene, domains = family_check(connection, gene_id)
    # pprint.pprint(domains)

    is_a_id = db.check_type(connection, name='is_a')[0][0]
    color = '0xCFCFCF'

    checked = []
    for d in domains:
        to_check = [d['type_id']]
        d_anc = []
        while len(to_check) > 0:
            i = to_check.pop(0)
            rel_result = db.check_relationship(
                connection, subject_id=i, type_id=is_a_id
            )
            if rel_result:
                # print('found {0}'.format(rel_result[0]))
                type_result = db.check_type(
                    connection, type_id=rel_result[0][1]
                )
                for tr in type_result:
                    if type_result[0][0] not in to_check:
                        to_check.append(type_result[0][0])
                    type_item = {
                        'type_id': type_result[0][0],
                        'name': type_result[0][1]
                    }
                    if type_item not in d_anc:
                        d_anc.append(type_item)
        if (d, d_anc) not in checked:
            checked.append((d, d_anc))
    if len(checked) == 1:
        for i, ancestor in enumerate(checked[0][1]):
            print('{0} ancestor: {1}'.format((i + 1) * '  ', ancestor))
            if ancestor['type_id'] in cmap:
                print('{0} -> {1}'.format(ancestor, cmap[ancestor['type_id']]))
                color = cmap[ancestor['type_id']]['color']
    elif len(checked) > 1:
        # pprint.pprint(checked)
        # multi-domain protein
        whole_type = {'name': 'scaffold_synthesis', 'type_id': 13816}
        if whole_type in checked[0][1]:
            color = '0xFFFF00'
            for ancestor in checked[0][1]:
                if ancestor['type_id'] in cmap:
                    color = cmap[ancestor['type_id']]['color']
        else:
            for d in checked:
                for i, ancestor in enumerate(d[1]):
                    print('{0} ancestor: {1}'.format((i + 1) * '  ', ancestor))
                    if ancestor['type_id'] in cmap:
                        print('{0} -> {1}'.format(
                            ancestor, cmap[ancestor['type_id']])
                        )
                        color = cmap[ancestor['type_id']]['color']
    return color


def get_anc(connection, d_id):
    to_check = [d_id]
    d_anc = []
    while len(to_check) > 0:
        i = to_check.pop(0)
        rel_result = db.check_relationship(
            connection, subject_id=i, type_id=4
        )
        if rel_result:
            type_result = db.check_type(
                connection, type_id=rel_result[0][1]
            )
            for tr in type_result:
                if type_result[0][0] not in to_check:
                    to_check.append(type_result[0][0])
                type_item = {
                    'type_id': type_result[0][0],
                    'name': type_result[0][1]
                }
                if type_item not in d_anc:
                    d_anc.append(type_item)
    return d_anc


def draw_cluster(
    dbfilename, cluster_id, outfilename, start, end, draw_domains, gb_id
):

    from Bio.Graphics import GenomeDiagram
    from Bio.SeqFeature import SeqFeature, FeatureLocation

    from evoc.utils import decode_gene_location

    connection = db.init_db(dbfilename)

    cur = connection.cursor()
    # gene_id start, gene_id end default values if not specified
    if start is None:
        start = 0
    if end is None:
        end = 9999999999999

    cmd = """
        SELECT gene.gb_id, gene.gene_id, gene.start, gene.end, type.name,
            gene.location
            FROM cluster_gene
        JOIN gene on gene.gene_id = cluster_gene.gene_id
        JOIN type on gene.type_id = type.type_id
        WHERE cluster_id = ?
        AND gene.gene_id >= ?
            AND gene.gene_id <= ?
    """
    where = (cluster_id, start, end)
    if gb_id is not None:
        cmd += """ AND gene.gb_id = ? """
        where = (cluster_id, start, end, gb_id)
    order_clause = """
        ORDER BY gene.gb_id, gene.start ASC
    """
    cmd += order_clause

    cluster_genes = cur.execute(cmd, where).fetchall()
    assert len(cluster_genes) > 0, exit(
        'no genes found for cluster {0}'.format(cluster_id)
    )
    by_gb = {}
    for cg in cluster_genes:
        if cg[0] not in by_gb:
            by_gb[cg[0]] = []
        by_gb[cg[0]].append(cg)

    diagram = GenomeDiagram.Diagram()

    track_num = 1
    tracks = {}
    spacer = 500  # bp between fragments!
    previous_end = 0
    # add a default feature diagram
    tracks['features'] = diagram.new_track(
        track_num,
        name='feature track',
        scale=False,
        height=0.55
    )
    track_num += 1
    feature_set = tracks['features'].new_set()

    for gb in sorted(by_gb.keys()):
        cg = by_gb[gb]
        # determine coordinate offset
        coord_offset = cg[0][2]

        # if draw_domains:
        #     tracks['domains'] = diagram.new_track(
        #         2,
        #         name='domain track',
        #         height=1
        #     )
        #     domain_set = tracks['domains'].new_set()

        for gene in cg:
            # add feature
            print('gene', gene)
            g, d = family_check(connection, gene[1])
            # pprint.pprint(g)
            # pprint.pprint(d)
            location = decode_gene_location(gene[5])
            if len(location) == 3:
                strand = location[0]
            elif len(location) == 1:
                strand = location[0][0]
            else:
                exit('something funky')
            f_start = previous_end + gene[2] - coord_offset  # start
            f_end = previous_end + gene[3] - coord_offset   # end
            f = SeqFeature(FeatureLocation(f_start, f_end), strand=strand)
            print('f', str(f.location))
            # color globally by gene_id
            fcolor = feature_color(connection, g, d)
            flabel = d[0]['name']

            feature_set.add_feature(
                f,
                name=flabel,
                color=fcolor,
                label_angle=60,
                label=False,
                label_size=15,
                label_strand=+1,
                sigil='BIGARROW',
                arrowhead_length=0.2,
                arrowshaft_height=1.0
            )
            if True and len(d) > 1:
                # get domain set
                whole_anc = get_anc(connection, d[0]['type_id'])
                whole_names = [m['name'] for m in whole_anc]
                if 'NRPS' not in whole_names:
                    continue
                multi_domains = d[1:]
                for m in multi_domains:
                    m_anc = get_anc(connection, m['type_id'])
                    mcolor = '#aeaeae'
                    for ma in m_anc:
                        if ma['type_id'] in cmap:
                            mcolor = cmap[ma['type_id']]['color']
                    # figure out if we want to draw it
                    if (
                        'Fill' in m['name'] or
                        'Nterm' in m['name'] or
                        'Cterm' in m['name']
                    ):
                        continue

                    # translate domain coordinates into base coordinates
                    m_start = 3 * m['start']
                    m_end = 3 * m['end']
                    print('bt', m_start, m_end)

                    if m_end <= m_start:
                        continue

                    assert f_start - f_start <= m_start <= f_end - f_start
                    assert f_start - f_start <= m_end <= f_end - f_start
                    assert m_end > m_start

                    if strand is -1:
                        tm_start = f_end - m_end
                        tm_end = f_end - m_start
                    elif strand is 1:
                        tm_start = f_start + m_start
                        tm_end = f_start + m_end

                    if True:
                        md = SeqFeature(
                            FeatureLocation(tm_start, tm_end),
                            strand=strand
                        )
                        print('md', str(md.location), m['name'])
                        # draw domain
                        feature_set.add_feature(
                            md, name='test',
                            color=mcolor,
                            sigil='BOX',
                            label=False,
                            strand=None,
                            height=0.1
                        )
        previous_end = previous_end + cg[-1][3] - coord_offset + spacer

    # draw and write diagrams
    diagram.draw(
        format='linear',
        track_size=0.4,
        orientation='landscape',
        # pagesize=(80 * cm, 10 * cm),
        pagesize=(1600, 200),
        fragments=1,
        start=0,
        end=100000
    )
    diagram.write(
        filename=outfilename,
        output='SVG',
        dpi=600
    )


def print_cluster(dbfilename, cluster_id):
    """print a text representation of a cluster"""
    import sqlite3
    connection = db.init_db(dbfilename)
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    cmd = """
        SELECT gb.gb_id, taxon.taxon_id,
            taxon_type.name, taxon_type.description,
            cluster_type.name, cluster_type.description,
            mol_type.name, mol_type.description
        FROM cluster
            JOIN cluster_gene ON cluster.cluster_id = cluster_gene.cluster_id
            JOIN type AS cluster_type ON cluster.type_id = cluster_type.type_id
            JOIN gene ON cluster_gene.gene_id = gene.gene_id
            JOIN gb ON gene.gb_id = gb.gb_id
            JOIN taxon ON gb.taxon_id = taxon.taxon_id
            JOIN type AS taxon_type ON taxon.type_id = taxon_type.type_id
            LEFT JOIN molecule on molecule.cluster_id = cluster.cluster_id
            LEFT JOIN type AS mol_type ON molecule.type_id = mol_type.type_id
        WHERE cluster.cluster_id = ?
        GROUP BY gb.gb_id
    """
    result = cur.execute(cmd, (cluster_id,)).fetchall()
    print(result)
    assert len(result) > 0
    print('Taxon id: {0} {1}'.format(result[0][1], result[0][2]))
    print('Cluster id: {0}'.format(cluster_id))
    print('Cluster type: {0}'.format(result[0][4]))
    print('description: {0}'.format(result[0][5]))
    print('molecule: {0} {1}'.format(result[0][6], result[0][7]))
    for g in result:
        print('\n  gb_id: {0}\t\t'.format(g[0]))
        print('{0}'.format('=' * 80))
        print('{0:>4}\t{1:>6}\t{2:>5}\t{3:<30}\t({4}, {5})'.format(
            'gene_id', 'start', 'end', 'gene_type', 'type_id', 'domain_name'
        ))
        print('{0}'.format('=' * 80))
        cmd = """
            SELECT
                gene.gene_id, gene.start, gene.end, gene_type.name,
                domain_type.type_id, domain_type.name
            FROM gene
            JOIN cluster_gene ON gene.gene_id = cluster_gene.gene_id
            JOIN type AS gene_type ON gene.type_id = gene_type.type_id
            JOIN domain ON gene.gene_id = domain.source_gene_id
            JOIN type as domain_type ON domain.type_id = domain_type.type_id
            WHERE cluster_id = ?
                AND gene.gb_id = ?
                AND domain.start = 0
            ORDER BY gene.start ASC, domain_type.type_id ASC
        """
        result = cur.execute(cmd, (cluster_id, g[0])).fetchall()
        printed = []
        for r in result:
            if r[0] not in printed:
                print('{0:>4}\t{1:>6}\t{2:>5}\t{3:<30}\t({4}, {5})'.format(
                    r[0], r[1], r[2], r[3], r[4], r[5]
                ))
                printed.append(r[0])
        print('\n\n')
