from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'agsci', 'common', 'version.txt')).read().strip()

setup(name='agsci.common',
    version=version,
    description="",
    long_description=open("README.txt").read() + "\n" +
                     open("HISTORY.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='',
    author='Tim Simkins, College of Agricultural Sciences, Penn State University',
    author_email='trs22@psu.edu',
    url='http://agsci.psu.edu/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['agsci'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'plone.app.dexterity',
        'plone.app.lockingbehavior',
        'plone.app.theming',
        'plone.app.mosaic',
        'plone.behavior',
        'zope.schema',
        'zope.interface',
        'zope.component',
        'plone.app.relationfield',
        'requests',
        'plone.app.contenttypes',
        'collective.autopermission',
        'collective.z3cform.datagridfield',
        'collective.dexteritytextindexer',
        'Products.WebServerAuth',
        'eea.facetednavigation',
        'untangle',
        'dexterity.membrane',
        'python-ldap',
        'beautifulsoup4',
        'Jinja2',
        'premailer',
        'zLOG',
        'collective.easyform',
    ],
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      [zodbupdate]
      renames = agsci.common:zodbupdate_renames
      """,
    )
