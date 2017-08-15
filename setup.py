"""Package setup."""
from setuptools import setup
from setuptools import find_packages

version = '1.0'

setup(
    name='wildcard.lockdown',
    version=version,
    description=(
        'Plone add-on to be able to make your site read-only except for a set '
        'of conditions that can be defined and enabled/disabled.'
    ),
    long_description=(
        open('README.rst').read() + '\n' +
        open('CHANGES.rst').read() + '\n'
    ),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Framework :: Plone :: 4.3',
        'Framework :: Plone',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
    ],
    keywords='',
    author='',
    author_email='',
    url='http://svn.plone.org/svn/collective/',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['wildcard'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFPlone',
        'plone.app.registry'
        'setuptools',
        'z3c.autoinclude',
    ],
    extras_require={
        'test': [
            'plone.app.testing'
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
