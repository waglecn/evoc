"""
Originally contributed by Andrew Pawlowski
    1 extract_proteins.py
    2 hmm_alignments.sh
    3 concat_aln.py for concatanating the alignments and adding empty sequences
        if gene wasn't present in that strain
"""
from Bio import SeqIO, SearchIO, SeqRecord, Alphabet, Seq
import os
import subprocess
from progress.bar import Bar


def parse_num_type_name(filename):
    head, tail = os.path.split(filename)
    num = tail[0:2]
    ftype = tail.split('_')[1]
    filename = '.'.join(tail.split('.')[:-1])
    name = '_'.join(filename.split('_')[2:])
    return num, ftype, name


def parse_default_name(filename):
    head, tail = os.path.split(filename)
    filename = '.'.join(tail.split('.')[:-1])
    return filename


def extract_proteins(files, output_dir='.', name_handler=parse_default_name):
    outfiles = []
    for file in files:
        head, tail = os.path.split(os.path.abspath(file))
        file_time = os.path.getmtime(file)

        # generate extracted protein file
        file_name = name_handler(file) + '.fa'
        out_path = os.path.join(output_dir, file_name)
        if not os.path.exists(out_path) or \
            (
                os.path.exists(out_path) and
                os.path.getmtime(out_path) < file_time
        ):
            gb_records = [r for r in SeqIO.parse(file, 'gb')]
            fasta = ""
            features = []
            for i, contig in enumerate(gb_records):
                features = [f for f in contig.features if f.type == 'CDS']
                for j, feature in enumerate(features):
                    if 'translation' in feature.qualifiers:
                        fasta += '>{0}\n{1}\n'.format(
                            '{0}_{1}'.format(
                                i, j
                            ),
                            feature.qualifiers['translation'][0]
                        )
            if len(fasta) == 0:
                # prodigal?
                cmd = ['prodigal', '-a', out_path, '-i', file]
                subprocess.check_output(cmd)
                records = [r for r in SeqIO.parse(out_path, 'fasta')]
                c = 0
                known = []
                for r in records:
                    num = int(r.id.split('_')[-1])
                    proposed_name = '{0}_{1}'.format(c, num)
                    while proposed_name in known:
                        c += 1
                        proposed_name = '{0}_{1}'.format(c, num)
                    r.id = proposed_name
                    known.append(proposed_name)
                    fasta += r.format('fasta').replace('*', '')

            new_file = open(out_path, 'w')
            new_file.write(fasta)
            new_file.close()
        outfiles.append(out_path)
    return outfiles


def hmm_alignments(query_list, hmm_list):
    import subprocess
    import io

    abb_query = []
    for q in query_list:
        head, tail = os.path.split(os.path.abspath(q))
        abb_query.append('.'.join(tail.split('.')[:-1]))

    abb_hmm = []
    for h in hmm_list:
        head, tail = os.path.split(os.path.abspath(h))
        abb_hmm.append('.'.join(tail.split('.')[:-1]))

    pre_aligned = {}
    for i, q in enumerate(query_list):
        collected = []
        pbar = Bar('{0} progress '.format(
            abb_query[i].ljust(30)), max=len(hmm_list)
        )
        for j, hmm in enumerate(hmm_list):
            cmd = ['hmmsearch', '--cut_tc', '--cpu', '1', hmm, q]
            result = io.StringIO(subprocess.check_output(cmd).decode("utf_8"))
            hmm_output = SearchIO.read(result, 'hmmer3-text')
            if len(hmm_output.hsps) > 0:
                target_sequence = hmm_output.hsps[0].hit.id
            else:
                target_sequence = None
            collected.append(target_sequence)
            pbar.next()
        pbar.finish()

        # load sequences once and extract target top-hit
        seqs = SeqIO.to_dict(SeqIO.parse(q, 'fasta'))
        collected_sequences = []
        for s in collected:
            if s is not None and s in seqs:
                collected_sequences.append(seqs[s].format('fasta'))
            else:
                collected_sequences.append('')
        pre_aligned[q] = collected_sequences
        # # debug
        # if q == './45_genome_WAC01376.fa':
        #     outh = open('dump.fasta', 'w')
        #     outh.write(str(collected_sequences))
        #     outh.close()
        #     from Bio import SeqIO
        #     new = 

    # next is to take the pre-aligned sequences and align them to a given hmm
    aligned = {}
    tempout_filename = 'tempout.fa'
    for i, hmm in enumerate(hmm_list):
        tempout = open(tempout_filename, 'w')
        all_empty = True
        aligned[abb_hmm[i]] = {}
        for j, q in enumerate(query_list):
            if pre_aligned[q][i] is not '':
                all_empty = False
                new = pre_aligned[q][i].replace(
                    '>', '>{0}___{1}___'.format(abb_query[j], abb_hmm[i])
                )
                tempout.write(new)
        tempout.close()

        if not all_empty:
            cmd = [
                'hmmalign', '--trim', '--outformat', 'afa', hmm,
                tempout_filename
            ]
            result = io.StringIO(subprocess.check_output(cmd).decode("utf-8"))
            records = SeqIO.to_dict(SeqIO.parse(result, 'fasta'))
        else:
            records = {}

        # process the aligned sequences - each query should have a hit in the
        # aligned records, othewise add the dummy sequence
        if len(records) > 0:
            align_length = len(records[list(records.keys())[0]])
        else:
            align_length = 1

        for q in abb_query:
            found = False
            for target in records:
                if q in target:
                    found = records[target]
            if not found:
                found = SeqRecord.SeqRecord(
                    Seq.Seq("-" * align_length, Alphabet.IUPAC.protein),
                    id="{0}___{1}___".format(q, hmm),
                    description=""
                )
            aligned[abb_hmm[i]][q] = found
    os.remove(tempout_filename)
    return aligned


def concat_alignments(aligned, excluded_models=[]):
    """produce concatenated alignment from aligned seq object"""
    # get the names of the genomes and the models
    models = list(aligned.keys())
    genomes = list(aligned[models[0]].keys())
    num_genomes = len(genomes)

    # sanity check
    for m in models:
        assert len(aligned[m]) == num_genomes, exit('something is wrong')
    processed_align = {}

    processed_models = [m for m in models if m not in excluded_models]
    for m in processed_models:
        for g in genomes:
            if g not in processed_align:
                processed_align[g] = aligned[m][g].seq
            else:
                processed_align[g] += aligned[m][g].seq
    output = ""
    for g in processed_align:
        new = SeqRecord.SeqRecord(processed_align[g], id=g, description='')
        output += new.format('fasta'). replace('.', '-')

    return output
