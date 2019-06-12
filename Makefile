all : check build

check :
	python -m compileall -q .

build :
	python setup.py sdist bdist

install : uninstall
	git clean -fxd .
	python -m pip install . --upgrade --user

test: install
	( cd /tmp && moosegui )

uninstall :
	python -m pip uninstall moosegui -y
