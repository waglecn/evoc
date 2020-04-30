"""Preparing Bacterial Genome Core Gene Alignments

Originally contributed by Andrew Pawlowski (2018)
    1 extract_proteins.py
    2 hmm_alignments.sh
    3 concat_aln.py for concatanating the alignments and adding empty sequences
        if gene wasn't present in that strain

    hp = HMMERprints(filelist)


Classes
-------

Functions
---------
"""
import os
import io
from urllib import parse
from Bio import SeqIO
from Bio import BiopythonExperimentalWarning
import subprocess
import pickle
from multiprocessing import Pool
from progress.bar import Bar
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', BiopythonExperimentalWarning)
    from Bio import SearchIO

# def parse_num_type_name(filename):
#     head, tail = os.path.split(filename)
#     num = tail[0:2]
#     ftype = tail.split('_')[1]
#     filename = '.'.join(tail.split('.')[:-1])
#     name = '_'.join(filename.split('_')[2:])
#     return num, ftype, name


# def parse_default_name(filename):
#     head, tail = os.path.split(filename)
#     filename = '.'.join(tail.split('.')[:-1])
#     return filename


# def extract_proteins(files, output_dir='.', name_handler=parse_default_name):
#     outfiles = []
#     for file in files:
#         head, tail = os.path.split(os.path.abspath(file))
#         file_time = os.path.getmtime(file)

#         # generate extracted protein file
#         file_name = name_handler(file) + '.fa'
#         out_path = os.path.join(output_dir, file_name)
#         if not os.path.exists(out_path) or \
#             (
#                 os.path.exists(out_path) and
#                 os.path.getmtime(out_path) < file_time
#         ):
#             gb_records = [r for r in SeqIO.parse(file, 'gb')]
#             fasta = ""
#             features = []
#             for i, contig in enumerate(gb_records):
#                 features = [f for f in contig.features if f.type == 'CDS']
#                 for j, feature in enumerate(features):
#                     if 'translation' in feature.qualifiers:
#                         fasta += '>{0}\n{1}\n'.format(
#                             '{0}_{1}'.format(
#                                 i, j
#                             ),
#                             feature.qualifiers['translation'][0]
#                         )
#             if len(fasta) == 0:
#                 # prodigal?
#                 cmd = ['prodigal', '-a', out_path, '-i', file]
#                 subprocess.check_output(cmd)
#                 records = [r for r in SeqIO.parse(out_path, 'fasta')]
#                 c = 0
#                 known = []
#                 for r in records:
#                     num = int(r.id.split('_')[-1])
#                     proposed_name = '{0}_{1}'.format(c, num)
#                     while proposed_name in known:
#                         c += 1
#                         proposed_name = '{0}_{1}'.format(c, num)
#                     r.id = proposed_name
#                     known.append(proposed_name)
#                     fasta += r.format('fasta').replace('*', '')

#             new_file = open(out_path, 'w')
#             new_file.write(fasta)
#             new_file.close()
#         outfiles.append(out_path)
#     return outfiles


# def hmm_alignments(query_list, hmm_list):
#     import subprocess
#     import io

#     abb_query = []
#     for q in query_list:
#         head, tail = os.path.split(os.path.abspath(q))
#         abb_query.append('.'.join(tail.split('.')[:-1]))

#     abb_hmm = []
#     for h in hmm_list:
#         head, tail = os.path.split(os.path.abspath(h))
#         abb_hmm.append('.'.join(tail.split('.')[:-1]))

#     pre_aligned = {}
#     for i, q in enumerate(query_list):
#         collected = []
#         pbar = Bar('{0} progress '.format(
#             abb_query[i].ljust(30)), max=len(hmm_list)
#         )
#         for j, hmm in enumerate(hmm_list):
#             cmd = ['hmmsearch', '--cut_tc', '--cpu', '1', hmm, q]
#             result = io.StringIO(subprocess.check_output(cmd).decode("utf_8"))
#             hmm_output = SearchIO.read(result, 'hmmer3-text')
#             if len(hmm_output.hsps) > 0:
#                 target_sequence = hmm_output.hsps[0].hit.id
#             else:
#                 target_sequence = None
#             collected.append(target_sequence)
#             pbar.next()
#         pbar.finish()

#         # load sequences once and extract target top-hit
#         seqs = SeqIO.to_dict(SeqIO.parse(q, 'fasta'))
#         collected_sequences = []
#         for s in collected:
#             if s is not None and s in seqs:
#                 collected_sequences.append(seqs[s].format('fasta'))
#             else:
#                 collected_sequences.append('')
#         pre_aligned[q] = collected_sequences
#         # # debug
#         # if q == './45_genome_WAC01376.fa':
#         #     outh = open('dump.fasta', 'w')
#         #     outh.write(str(collected_sequences))
#         #     outh.close()
#         #     from Bio import SeqIO
#         #     new

#     # next is to take the pre-aligned sequences and align them to a given hmm
#     aligned = {}
#     tempout_filename = 'tempout.fa'
#     for i, hmm in enumerate(hmm_list):
#         tempout = open(tempout_filename, 'w')
#         all_empty = True
#         aligned[abb_hmm[i]] = {}
#         for j, q in enumerate(query_list):
#             if pre_aligned[q][i] is not '':
#                 all_empty = False
#                 new = pre_aligned[q][i].replace(
#                     '>', '>{0}___{1}___'.format(abb_query[j], abb_hmm[i])
#                 )
#                 tempout.write(new)
#         tempout.close()

#         if not all_empty:
#             cmd = [
#                 'hmmalign', '--trim', '--outformat', 'afa', hmm,
#                 tempout_filename
#             ]
#             result = io.StringIO(subprocess.check_output(cmd).decode("utf-8"))
#             records = SeqIO.to_dict(SeqIO.parse(result, 'fasta'))
#         else:
#             records = {}

#         # process the aligned sequences - each query should have a hit in the
#         # aligned records, othewise add the dummy sequence
#         if len(records) > 0:
#             align_length = len(records[list(records.keys())[0]])
#         else:
#             align_length = 1

#         for q in abb_query:
#             found = False
#             for target in records:
#                 if q in target:
#                     found = records[target]
#             if not found:
#                 found = SeqRecord.SeqRecord(
#                     Seq.Seq("-" * align_length, Alphabet.IUPAC.protein),
#                     id="{0}___{1}___".format(q, hmm),
#                     description=""
#                 )
#             aligned[abb_hmm[i]][q] = found
#     os.remove(tempout_filename)
#     return aligned


# def concat_alignments(aligned, excluded_models=[]):
#     """produce concatenated alignment from aligned seq object"""
#     # get the names of the genomes and the models
#     models = list(aligned.keys())
#     genomes = list(aligned[models[0]].keys())
#     num_genomes = len(genomes)

#     # sanity check
#     for m in models:
#         assert len(aligned[m]) == num_genomes, exit('something is wrong')
#     processed_align = {}

#     processed_models = [m for m in models if m not in excluded_models]
#     for m in processed_models:
#         for g in genomes:
#             if g not in processed_align:
#                 processed_align[g] = aligned[m][g].seq
#             else:
#                 processed_align[g] += aligned[m][g].seq
#     output = ""
#     for g in processed_align:
#         new = SeqRecord.SeqRecord(processed_align[g], id=g, description='')
#         output += new.format('fasta'). replace('.', '-')

#     return output


class HMMERmodel_list:
    """A class that contains references to available HMM models

    The model list only depends on the package reference. The default list of
    models are provided with the package

    Methods
    -------
    add(filename)
        add an .hmm file to the list
    """

    _base_dir, _tail = os.path.split(__file__)
    _hmm_core_dir = os.path.join(
        _base_dir, 'bact_core_tree_building', 'core_hmm'
    )
    _default_hmm_list = []
    _list = None
    for hmm in os.listdir(_hmm_core_dir):
        if hmm.endswith('.hmm') and hmm not in _default_hmm_list:
            _default_hmm_list.append(os.path.join(_hmm_core_dir, hmm))

    def __init__(self, filelist=[]):
        self._list = []
        for hmmfile in self._default_hmm_list:
            if os.path.exists(hmmfile):
                temp = HMMERmodel(hmmfile)
            self.add(temp)
        for hmmfile in filelist:
            if os.path.exists(hmmfile):
                temp = HMMERmodel(hmmfile)
            self.add(temp)
        print('{0} models are loaded'.format(len(self._list)))

    def __str__(self):
        result = ""
        for model in self:
            result += model.model_accession + " " + model.model_filename + "\n"
        return result

    def __getitem__(self, item):
        return self._list[item]

    def __contains__(self, item):
        for i in self._list:
            if i == item:
                return True
        return False

    def __len__(self):
        return len(self._list)

    def add(self, hmmermodel):
        """Add an .hmm to the list

        Parameters
        ----------
        filename : a filename for a valid HMMER 3 HMM file
        """
        if isinstance(hmmermodel, str) and os.path.exists(hmmermodel):
            hmmermodel = HMMERmodel(hmmermodel)

        if isinstance(hmmermodel, HMMERmodel):
            if hmmermodel not in self:
                self._list.append(hmmermodel)
            else:
                print('{} already loaded'.format(hmmermodel))
            return
        print('{} is not a .hmm file or a HMMERmodel'.format(hmmermodel))
        return


class HMMERmodel:
    """This class represents an HMM model

    This class is meant to work within HMMERmodel_list
    """

    def __init__(self, hmm_file, *args, **kwargs):
        """
        Parameters
        ----------
        hmm_file : str
            a filename for a vlid HMMER 3 HMM file
        accession : str
            (optional) an accession for this model
        locus_name : str
            (optional) the locus this model represents
        """

        self.model_filename = hmm_file
        head, tail = os.path.split(self.model_filename)
        tail = tail.split('.')
        assert tail[-1] == 'hmm'
        tail = '.'.join(tail[:-1])
        parts = tail.split('_')
        self.model_num = parts[0]
        parts = parts[-1].split('-')
        self.model_accession = parts[0]
        self.model_locus_name = parts[-1]
        if 'accession' in kwargs:
            self.model_accesion = kwargs['accession']
        if 'locus_name' in kwargs:
            self.locus_name = kwargs['locus_name']

    def __str__(self):
        return "{0} {1}\n{2}\n".format(
            self.model_accession,
            self.model_locus_name,
            self.model_filename
        )

    def __eq__(self, item):
        if (
            self.model_accession == item.model_accession and
            self.model_locus_name == item.model_locus_name and
            self.model_filename == item.model_filename
        ):
            return True
        return False

class HMMERsource:
    """A class to store a reference todata that can be used to calculate
    HMMERprint with some caching for faster access

    Attributes
    ----------

    Methods
    -------
    derive_name()
        derives a standard name from the filename of the source
    """

    def __init__(
        self, source, models, force=False,
        output_location=None
    ):
        """
        Parameters
        ----------
        source : str
            a valid filename or url
        models : HMMERmodel_list
            the list of models to search against
        force: bool (default False)
            whether to force re-parsing of the source or load the cached .hmp
            (if available and source mtime older than the cached mtime)
        output_location : str
            a path for storing cached information

        """
        self.reference = source
        self.parsed_reference = self.parse_reference()

        # self.output_location = output_location
        # self.name = self.derive_name()
        # if output_location is None:
        #     self.output_location = self.original_location
        # self.print_filename = os.path.join(
        #     self.output_location,
        #     self.name + '.hmp'
        # )
        # self.nt_fasta = ""
        # self.aa_fasta = ""
        # self.BIO = None
        # self.hmmerprint = self.make_HMMERprint(self, models)

    def parse_reference(self):
        assert self.reference is not None
        parsed_url = parse.urlparse(self.reference)
        if not bool(parsed_url.scheme):
            # assume file
            parsed_url = parse.urlparse('file://{}'.format(self.reference))
        # url
        scheme = parsed_url.scheme
        path = parsed_url.path
        table = None
        dbid = None
        if parsed_url.scheme == 'sqlite3':
            # so something
            head, tail = os.path.split(path)
            head = os.path.split(head)
            path = head[0]
            table = head[1]
            dbid = tail

        assert os.path.exists(path), exit(
            'not found: {0}'.format(self.reference)
        )
        path = os.path.abspath(path)
        return (scheme, path, table, dbid)

    def get_reference(self):
        if self.parsed_reference is None:
            self.parse_reference()
        exit()

        # get the BIO from the source
        # self.original_location = os.path.split(
        #     os.path.abspath(source)
        # )[0]5
        # self.original_mtime = os.path.getmtime(self.original_filename)

        # _parts = source_filename.split('.')
        # if _parts[-1] in ['gz']:
        #     gzipped = True
        #     if _parts[-2] in ['gb', 'gbk', 'genbank']:
        #         _format = 'gb'
        # elif _parts[-1] in ['gbk', 'gb', 'genbank']:
        #     _format = 'gb'
        #     gzipped = False
        # elif _parts[-1] in ['fasta', 'fn', 'fa', 'faa']:
        #     _format = 'fasta'
        #     gzipped = False
        # else:
        #     exit('Unknown format: \'{0}\''.format(_parts[-1]))
        # # else:
        # #     _format = stype
        # #     gzipped = False


        # if (
        #     os.path.exists(self.print_filename) and (not force) and
        #     self.original_mtime < os.path.getmtime(self.print_filename)
        # ):
        #     with open(self.print_filename, 'rb') as pickle_handle:
        #         packed = pickle.load(pickle_handle)
        #         self.BIO = gzip.decompress(packed[0]).decode('utf-8', errors='ignore')
        #         self.nt_fasta = packed[1]
        #         self.aa_fasta = packed[2]
        #         self.name = packed[3]
        #         self.print_filename = packed[4]
        #         self.hmmerprint = packed[5]
        #         del packed
        # else:
        #     if gzipped:
        #         import gzip
        #         # text mode - see github.com/biopython/biopython/issues/1009
        #         _inh = gzip.open(self.original_filename, 'rt')
        #     else:
        #         _inh = open(self.original_filename, 'rU')
        #     rtemp = SeqIO.parse(_inh, format=_format)
        #     self.BIO = [
        #         r for r in rtemp
        #     ]

        #     for r in self.BIO:
        #         self.nt_fasta += r.format('fasta')
        #         for f in r.features:
        #             if f.type == 'CDS' and (
        #                 'locus_tag' in f.qualifiers or 'gene' in f.qualifiers
        #             ) and 'translation' in f.qualifiers:
        #                 available = [
        #                     f.qualifiers[k][0] for k in ['locus_tag', 'gene']
        #                     if k in f.qualifiers
        #                 ]
        #                 label = '___'.join(available)
        #                 self.aa_fasta += '>{0}\n{1}\n'.format(
        #                     label,
        #                     f.qualifiers['translation'][0]
        #                 )
        #     self.BIO = gzip.compress(bytes(self.BIO, 'utf-8'))
        #     with open(self.print_filename, 'wb') as pickle_handle:
        #         pickle.dump(
        #             (
        #                 self.BIO,
        #                 self.nt_fasta,
        #                 self.aa_fasta,
        #                 self.name,
        #                 self.print_filename,
        #                 self.hmmerprint
        #             ),
        #             pickle_handle
        #         )

    def __getitem__(self, item):
        try:
            return self.BIO[item]
        except IndexError:
            return None

    def __len__(self):
        return len(self.BIO)

    def derive_name(self):
        abspath = os.path.abspath(self.original_filename)
        prefix, base = os.path.split(abspath)
        preprefix, prefix = os.path.split(prefix)
        if base.startswith('AA'):
            name = base.split('-')[0]
        elif base.startswith('GCA_'):
            name = base.split('.')[0]
        elif prefix.startswith('AA'):
            name = prefix.split('-')[0]
        elif prefix.startswith('GCA_'):
            name = prefix.split('.')[0]
        else:
            # strip the extension from the base
            name = '.'.join(base.split('.')[:-1])
        return name


class HMMERprint:
    """A simple representation of HMMERprints"""
    def __init__(self, source, models):
        self._model_hits = self.hmm_alignments(source, models)

    def __getitem__(self, key):
        return self._model_hits.__getitem__(key)

    def hmm_alignments(self, source, models):
        head, tail = os.path.split(source.original_filename)
        temp_aa = os.path.join(head, source.name + '.fa')
        with open(temp_aa, 'w') as outh:
            outh.write(source.aa_fasta)
        seqs = SeqIO.to_dict(
            SeqIO.parse(io.StringIO(source.aa_fasta), 'fasta')
        )
        pre_aligned = {}
        for j, hmm in enumerate(models):
            cmd = [
                'hmmsearch', '--cut_tc', '--cpu', '1',
                hmm.model_filename, temp_aa
            ]
            result = io.StringIO(subprocess.check_output(cmd).decode("utf_8"))
            hmm_output = SearchIO.read(result, 'hmmer3-text')
            if len(hmm_output.hsps) > 0:
                target_sequence = hmm_output.hsps[0].hit.id
            else:
                target_sequence = None
            if target_sequence is not None and target_sequence in seqs:
                pre_aligned[hmm.model_accession] = seqs[
                    target_sequence
                ].format('fasta')
            else:
                pre_aligned[hmm.model_accession] = ''
        del seqs
        return pre_aligned


class HMMERprints():
    """A list-like object to manage HMMERprints

    SUMMARY

    Parameters
    ----------
    filelist : list of str
        a list of genomes, typically in Genbank format to be processed

    Methods
    -------
    model_alignment(models=[])
        generate concatenated alignment for each source, and each model listed.
    """

    def __init__(self, filelist, hmmlist=None, **kwargs):
        """
        Parameters:
            filelist : list of str
                A list of sources (gbk files) from which to generate a
                HMMERprint
            hmmlist : HMMERmodel_list (optional)
                If not provided, will use the default list of package-provided
                HMMs (from TIGRFAM GenProp0799) (Accessed Feb. 2018)
                [1]: http://genome-properties.jcvi.org/cgi-bin/GenomePropDefinition.cgi?prop_acc=GenProp0799 # noqa

        Returns:
            a list-like object of processed HMMERsource objects
        """
        output_location = None
        if 'output_location' in kwargs:
            output_location = kwargs['output_location']
        from progress.bar import Bar
        self.model_list = hmmlist
        if hmmlist is None:
            self.model_list = HMMERmodel_list()
        pbar = Bar('Loading sources', max=len(filelist))
        self._sources = []
        for f in filelist:
            self.add_source(
                f, self.model_list, output_location=output_location
            )
            pbar.next()
        pbar.finish()

    def __getitem__(self, item):
        return self._sources[item]

    def __len__(self):
        return len(self._sources)

    def add_source(self, f, hmmlist=None, output_location=None):
        if hmmlist is None:
            hmmlist = self.model_list
        self._sources.append(
            HMMERsource(f, hmmlist, output_location=output_location)
        )

    def model_alignment(self, models=[]):
        """generate concatenated alignment for source genomes and listed models

        A model list needs to be specified or else an empty alignment is made.
        It is also implied that there is at least one source.

        Parameters
        ----------
        models : HMMERmodel_list
            the list of models to align

        Returns:
            str concatenated fasta alignment of each genome/model

        """

        aligned = {}
        pbar = Bar('Aligned families', max=len(models))
        for m in models:
            all_empty = True
            aligned[m.model_accession] = {}
            fixers = []
            aligned_model_length = 1
            for s in self._sources:
                if s.hmmerprint[m.model_accession] is not '':
                    tmp = s.hmmerprint[m.model_accession].split('\n')
                    # ensure unique sequence ids
                    new_name = '>{0}__{1}'.format(s.name, m.model_accession)
                    tmp = new_name + '\n' + ''.join(tmp[1:]) + "\n"
                    aligned[m.model_accession][s.name] = tmp
                    all_empty = False
                else:
                    fixers.append(s.name)

            if not all_empty:
                # at least one sequence to be aligned
                tempout_filename = 'tempout.fa'
                tempout = open(tempout_filename, 'w')
                for sname in aligned[m.model_accession]:
                    tempout.write(aligned[m.model_accession][sname])
                tempout.close()
                cmd = [
                    'hmmalign', '--trim', '--outformat', 'afa',
                    m.model_filename,
                    tempout_filename
                ]
                result = io.StringIO(
                    subprocess.check_output(cmd).decode("utf-8")
                )
                records = SeqIO.to_dict(SeqIO.parse(result, 'fasta'))
                assert len(records) == len(aligned[m.model_accession])
                for sname in aligned[m.model_accession]:
                    name = "{0}__{1}".format(
                        sname, m.model_accession
                    )
                    assert name in records, exit((m.model_accession, sname))
                    aligned[m.model_accession][sname] = records[name].format(
                        'fasta'
                    )
                    aligned_model_length = len(records[name])
                os.remove(tempout_filename)
            for sname in fixers:
                name = '{0}__{1}'.format(sname, m.model_accession)
                aligned[m.model_accession][sname] = '>{0}\n{1}\n'.format(
                    name, '-' * aligned_model_length
                )
            pbar.next()
        pbar.finish()

        # sanity check
        for m in models:
            assert len(aligned[m.model_accession]) == len(self), exit(
                'something is wrong'
            )
        processed_align = {}
        for m in models:
            for s in self:
                if s.name not in processed_align:
                    processed_align[s.name] = '>{0}\n'.format(s.name) + \
                        ''.join(aligned[m.model_accession][s.name].split(
                            '\n'
                        )[1:])
                else:
                    processed_align[s.name] += \
                        ''.join(aligned[m.model_accession][s.name].split(
                            '\n'
                        )[1:])

        for s in processed_align:
            print(processed_align[s])
