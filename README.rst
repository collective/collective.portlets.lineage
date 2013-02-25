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


