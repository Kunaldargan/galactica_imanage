#!/bin/bash

pip3 install numpy 
pip3 install cython
sudo apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev


# nano /home/username/.bashrc
# script = "PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}$
# export LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"


pip3 install django-bootstrap-select
pip3 install django-filebrowser
pip3 install -e git+git://github.com/dteskera/django-filebrowser-suit.git#egg=django-filebrowser \
pip3 install -e git+git://github.com/dteskera/django-filebrowser-suit-skin.git#egg=django-filebrowser-suit-skin 

if true; then
	export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}$
	export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
	pip3 install -r requirements_gpu.txt
else 
	pip3 install -r requirements.txt
fi


