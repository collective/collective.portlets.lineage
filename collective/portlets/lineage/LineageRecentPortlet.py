from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.AdvancedQuery import *
from collective.portlets.lineage import LineagePortletsMessageFactory as _
from collective.portlets.lineage.LineagePortletsCommon import get_subsites

class ILineageRecentPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)
                       
    excludeSubsite = schema.Bool(title=_(u"Exclude subsites"),
                               description = _(u"If selected, search results will not include recent items added to subsites."),
                               default = False,
                               required = False)

class Assignment(base.Assignment):
    implements(ILineageRecentPortlet)

    def __init__(self, count=5, excludeSubsite=False):
        self.count = count
        self.excludeSubsite = excludeSubsite

    @property
    def title(self):
        return _(u"Lineage Recent items")

def _render_cachekey(fun, self):
    if self.anonymous:
        raise ram.DontCache()
    return render_cachekey(fun, self)

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/recent.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.navigation_root_url = portal_state.navigation_root_url()
        self.typesToShow = portal_state.friendly_types()
        self.navigation_root_path = portal_state.navigation_root_path()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return not self.anonymous and len(self._data())

    def recent_items(self):
        return self._data()

    def recently_modified_link(self):
        context = aq_inner(self.context)
        setattr(context, 'subsite_paths', self.get_subsite_paths())
        setattr(context, 'parent_only', self.is_parent_site_only())
        return '%s/recently_modified' % self.navigation_root_url

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        limit = self.data.count
        path = self.navigation_root_path
        excludeSubsite = self.data.excludeSubsite
        query = self.catalog.makeAdvancedQuery({'portal_type':self.typesToShow, 
                                           'path':path, 
                                           'sort_on':'modified',
                                           'sort_order':'reverse',
                                           'sort_limit':limit})
        if excludeSubsite:
            query &= ~ In('path', get_subsites(path,self.catalog), filter=True)
        results = self.catalog.evalAdvancedQuery(query)
        return results[:limit]
    
    def get_subsite_paths(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = self.navigation_root_path
        return get_subsites(path,catalog)
   
    def is_parent_site_only(self):
        return self.data.excludeSubsite

class AddForm(base.AddForm):
    form_fields = form.Fields(ILineageRecentPortlet)
    label = _(u"Add Recent Portlet")
    description = _(u"This portlet displays recently modified content.")

    def create(self, data):
        return Assignment(count=data.get('count', 5), excludeSubsite=data.get('excludeSubsite'))

class EditForm(base.EditForm):
    form_fields = form.Fields(ILineageRecentPortlet)
    label = _(u"Edit Recent Portlet")
    description = _(u"This portlet displays recently modified content.")
