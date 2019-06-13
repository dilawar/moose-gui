PY := $(shell which python3)

all : check build

check :
	$(PY) -m compileall -q .

build :
	$(PY) setup.py sdist bdist

install : uninstall
	git clean -fxd .
	$(PY) -m pip install . --upgrade --user

test: install
	( cd /tmp && moosegui )

uninstall :
	$(PY) -m pip uninstall moosegui -y
