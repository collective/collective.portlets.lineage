from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.portlets.lineage',
      version=version,
      description="A collection of collective.lineage aware portlets",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone portlets collective.lineage',
      author='Andy Leeb',
      author_email='ableeb@gmail.com',
      url='https://svn.plone.org/collective/collective.portlets.lineage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlets'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.lineage',
          'Products.AdvancedQuery',
          # -*- Extra requirements: -*-
      ],
      extras_require={'tests': ['plone.app.testing', 'collective.lineage']},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
