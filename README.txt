Introduction
============
Portlets which can optionally include or exclude content from subsites, as provided by collective.lineages Child Folder. 

The portlets filter out subsite paths via the use of Products.AdvancedQuery, which ships with Plone 3.x

These portlets require that collective.lineages be installed in your Plone site.

Currently, the following portlets are included in this package:
 - Recent Items
 - News
 - Events
 - Search
 - Review

Usage
========
Add the following to your buildout:

    eggs = 
        ...
        collective.lineage
        collective.portlets.lineage

    zcml =
        ...
        collective.lineage
        collective.portlets.lineage

Install via zmi->setup_tools->import. Be sure to install collective.lineages first, then install this package. To add the portlets, use the manage portlets link.

TODO: include Calendar portlet

