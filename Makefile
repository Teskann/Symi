all: clean

requirements:
	pip install -r requirements.txt

build: requirements
	python setup.py bdist_wheel

install: build
	pip install dist/*.whl

clean: install
	rm -rf .eggs build dist *.egg-info