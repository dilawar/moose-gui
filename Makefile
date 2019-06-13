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

lint:
	find . -type f -name *.py -print0 | xargs -0 -I file pyflakes file

.PHONY : lint uninstall test install build check
