# default virtualenvironment for developement
VENV = env
export VIRTUAL_ENV := $(abspath ${VENV})
export PATH := ${VIRTUAL_ENV}/bin:${PATH}

WITHQT4 = False

ifdef ($(WITHQT4),True)
  PYQT4=PyQt4
endif

all:
	# don't do anything by default

develop: venv_install
	# all
	@echo "all done\n"

sip-4.19.3/sipgen/sip:
	wget -nc https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.3/sip-4.19.3.tar.gz
	tar xzvf sip-4.19.3.tar.gz
	cd sip-4.19.3 ; python configure.py ; $(MAKE) MAKEFLAGS= ; sudo $(MAKE) install MAKEFLAGS=

PyQt4: PyQt4_prereqs sip-4.19.3/sipgen/sip PyQt_gpl_x11-4.12/QtCore/QtCore.so 

PyQt_gpl_x11-4.12/QtCore/QtCore.so:
	wget -nc http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_x11-4.12.tar.gz
	tar -xzvf PyQt4_gpl_x11-4.12.tar.gz
	cd PyQt4_gpl_x11-4.12 ; python ./configure-ng.py ; $(MAKE) MAKEFLAGS= -j 4 ; sudo $(MAKE) install MAKEFLAGS=

virtualenv: prereqs ${VENV}/bin/activate ${PYQT4}
	# virtualenv
	. ${VENV}/bin/activate && pip install -U pip

${VENV}/bin/activate:
	# activate
	virtualenv -p python3 ${VENV}
	touch ${VENV}/bin/activate

prereqs:
	# prereqs
	sudo apt-get install virtualenv python3-dev build-essential muscle fasttree \
	 python3-dev graphviz graphviz-dev libblas-dev liblapack-dev

PyQt4_prereqs:
	sudo apt-get install qt4-default libqt4-dev libqt4-opengl-dev

venv_install: virtualenv
	@echo "\n\nVIRTUALENV\n\n"
	# venv
	. ${VENV}/bin/activate && pip install -e .

clean:
	rm -Ifr ${VENV} sip-4.19.3 PyQt4_gpl_x11-4.12 PyQt*.tar.gz sip*.tar.gz \
		evoc.egg-info
