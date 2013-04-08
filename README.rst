Introduction
============
Portlets which can optionally include or exclude content from subsites, as provided by collective.lineage Child Folder. 

The portlets filter out subsite paths via the use of Products.AdvancedQuery.

These portlets require that collective.lineage be installed in your Plone site.

Currently, the following portlets are included in this package:
 - Recent Items
 - News
 - Events
 - Search
 - Review

Included portlets have been diffed against plone.app.portlets 2.3.7,
included with Plone 4.2.4

Usage
========
Add the following to your buildout:

    eggs = 
        ...
        collective.lineage
        
        collective.portlets.lineage

Install via quickinstaller or the Add Ons control panel. 

TODO: include Calendar portlet


Changelog
=========

1.1 05-15-2012
--------------
- custom titles for News and Events portlet

1.1.1 05-31-2012
--------------
- news portlet default title is News, events portlet default title is 'Upcoming Events'

1.1 05-15-2012
--------------
- adds ability to have custom titles for News, Events portlets [ableeb]

1.1.1 05-31-2012
--------------
- changes the default names of news portlet to News, and default name of events portlet to Upcoming Events

1.1.2 06-04-2012
---------------
- fixes for changes in 1.1.1

1.1.3 06-05-2012
----------------
- correctly sorts news items in portlets by Date, descending in advanced query

1.2.0 06-19-2012
----------------
- Fix livesearch
- Update templates for 4.1.5 compatibility
- Update skins/scripts/* for 4.1.5 compatibilty
- Add missing zcml registration for custom template

1.2.1 06-19-2012
----------------
- Fix portlet class files for 4.1.5 compatibilty

1.2.2 02-25-2013
----------------
- Fix portlet class files and templates for p.a.portlets-2.3.7 compatibility

1.2.3 04-08-2013
----------------
- fix search template to not prepend Search before the custom title https://github.com/collective/collective.portlets.lineage/issues/5
- add uninstall profile https://github.com/collective/collective.portlets.lineage/issues/4
- livesearch now shows on search portlet https://github.com/collective/collective.portlets.lineage/issues/2
- pep8
- fix unit tests
- add unit test for uninstall

1.2.4 04-08-2013
----------------
- no changes
