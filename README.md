# Evoc

## Development Setup
--------------------------
Quickstart:
```
cd evoc
make develop
```

Or, for optional Qt4:
```
cd evoc
make develop WITHQT4
```

Inside the package folder:
```
virtualenv -P python3 env
source ./env/bin/activate
pip install pip -U
pip install -e .
```

This package uses ete3, which can make use of PyQt4.
Obsolote, but included for historical reasons can use the following package:

```
wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.3/sip-4.19.3.tar.gz
tar xzvf sil-4.19.3.tar.gz
cd sip-4.19.3
python configure.py
make
make install
```

```
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_x11-4.12.tar.gz
tar -xzvf PyQt4_gpl_x11-4.12.tar.gz
python ./configure-ng.py
```

If performing the last steps in a virtualenv instead:
```
python configure.py --incdir=[name-of-virtualenv]/include/[python version]
make
make install
```

## External Requirements
--------------------------
python3 >= 3.5
```
	sudo apt-get install virtualenv python3-dev build-essential muscle fasttree \
	 python3-dev graphviz graphviz-dev libblas-dev liblapack-dev
```
ecceTERA >= 1.2.2 (https://mbb.univ-montp2.fr/MBB/download_sources/16__ecceTERA)


## References
--------------------------

Huerta-Cepas, J., Serra, F., Bork, P. (2016) ETE3: Reconstruction, Analysis, and Visualization of Phylogenomic Data. __Mol Biol Evol__ **33(6)**:1635-1638. https://doi.org/10.1093/molbev/msw046

Jacox, E., Chauve, C., Szöllősi, G.J., Ponty, Y., Scornavacca, C. (2016) ecceTERA: comprehensive gene tree-species tree reconciliation using parsimony. _Bioinformatics_ **32(13)**:2056-2058. https://doi.org/10.1093/bioinformatics/btw105

Waglechner, N., McArthur, A.G. & Wright, G.D. (2019) Phylogenetic reconciliation reveals the natural history of glycopeptide antibiotic biosynthesis and resistance. _Nat Microbiol_ **4**:1862–1871. https://doi.org/10.1038/s41564-019-0531-5
