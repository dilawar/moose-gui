all : check build

check :
	python -m compileall -q .

build :
	python setup.py sdist bdist

install :
	python -m pip install . --upgrade --user

test: install
	( cd /tmp && moosegui )
