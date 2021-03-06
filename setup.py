# -*- coding: utf-8 -*-
"""Python packaging."""
from os.path import abspath
from os.path import dirname
from os.path import join
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


def packages(project_name):
    """Return list of packages distributed by project based on its name.

    >>> packages('foo')
    ['foo']
    >>> packages('foo.bar')
    ['foo', 'foo.bar']
    >>> packages('foo.bar.baz')
    ['foo', 'foo.bar', 'foo.bar.baz']
    >>> packages('FooBar')
    ['foobar']

    Implements "Use a single name" convention described in :pep:`423`.

    """
    name = str(project_name).lower()
    if '.' in name:  # Using namespace packages.
        parts = name.split('.')
        return ['.'.join(parts[0:i]) for i in range(1, len(parts) + 1)]
    else:  # One root package or module.
        return [name]


def namespace_packages(project_name):
    """Return list of namespace packages distributed in this project, based on
    project name.

    >>> namespace_packages('foo')
    []
    >>> namespace_packages('foo.bar')
    ['foo']
    >>> namespace_packages('foo.bar.baz')
    ['foo', 'foo.bar']
    >>> namespace_packages('Foo.BaR.BAZ') == namespace_packages('foo.bar.baz')
    True

    Implements "Use a single name" convention described in :pep:`423`.

    """
    package_list = packages(project_name)
    package_list.pop()  # Ignore last element.
    # Remaining packages are supposed to be namespace packages.
    return package_list


name = 'django-esutils'
version = read_relative_file('VERSION').strip()
readme = read_relative_file('README.rst')


if __name__ == '__main__':  # ``import setup`` doesn't trigger setup().
    setup(name=name,
          version=version,
          description="""Django Esutils.""",
          long_description=readme,
          classifiers=[
              'Development Status :: 3 - Alpha',
              'Programming Language :: Python',
              'Framework :: Django',
              'License :: OSI Approved :: MIT License',
          ],
          keywords='',
          author='Novapost',
          author_email='florent.pigout@novapost.fr',
          url='https://github.com/novapost/%s' % name,
          license='MIT License',
          packages=packages(name.replace('-', '_')),
          namespace_packages=namespace_packages(name),
          include_package_data=True,
          zip_safe=False,
          install_requires=[
              'django',
              'djangorestframework',
              'elasticutils'
          ],
          dependency_links=[])
