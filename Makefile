install-doc:
	pip install -r requirements/doc.pip

doc:
	cd docs && make html

install-test:
	pip install -r requirements/test.pip

test:
	demo_esutils test demo_esutils
	flake8 django_esutils

clean:
	rm -f .coverage
	rm -r docs/_build
	find . -name '*.pyc' -delete
	find . -name '*~' -delete
