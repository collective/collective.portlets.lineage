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
from plone.app.layout.navigation.root import getNavigationRootObject

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.AdvancedQuery import *

from collective.portlets.lineage import LineagePortletsMessageFactory as _
from collective.portlets.lineage.LineagePortletsCommon import get_subsites

class ILineageNewsPortlet(IPortletDataProvider):

    customTitle = schema.TextLine(title = _(u"Add a title"),
                                  description = _(u"Displays a custom title for this portlet."),
                                  required = False)


    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)

    state = schema.Tuple(title=_(u"Workflow state"),
                         description=_(u"Items in which workflow state to show."),
                         default=('published', ),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )
    
    excludeSubsite = schema.Bool(title=_(u"Exclude subsites"),
                                 description = _(u"If selected, search results will not include news items added to subsites."),
                                 default = False,
                                 required = False)


class Assignment(base.Assignment):
    
    implements(ILineageNewsPortlet)

    customTitle = u"Lineage News"
    count = 5
    state = ('published')
    excludeSubsite = False

    def __init__(self, customTitle=u"Lineage News", count=5, state=('published', ), excludeSubsite=False):
        self.customTitle = customTitle
        self.count = count
        self.state = state
        self.excludeSubsite = excludeSubsite


    @property
    def title(self):
        if self.customTitle is None:
            self.customTitle = u"Lineage News"
        return self.customTitle
        
class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('templates/news.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()
        self.navigation_root_url = portal_state.navigation_root_url()
        self.navigation_root_path = portal_state.navigation_root_path()

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self._data())

    def published_news_items(self):
        return self._data()

    def all_news_link(self):
        if 'news' in getNavigationRootObject(self.context, self.portal).objectIds():
            return '%s/news' % self.navigation_root_url
        else:
            return None

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = self.navigation_root_path
        limit = self.data.count
        state = self.data.state
        excludeSubsite = self.data.excludeSubsite
        query = catalog.makeAdvancedQuery({'portal_type':'News Item', 'review_state':state, 'path':path, 'sort_on':'Date','sort_order':'reverse','sort_limit':limit})
        if excludeSubsite:
            query &= ~ In('path', get_subsites(path,catalog), filter=True)
        results = catalog.evalAdvancedQuery(query)
        return results[:limit]
        

class AddForm(base.AddForm):
    form_fields = form.Fields(ILineageNewsPortlet)
    label = _(u"Add News Portlet")
    description = _(u"This portlet displays recent News Items.")

    def create(self, data):
        return Assignment(**data)
        
class EditForm(base.EditForm):
    form_fields = form.Fields(ILineageNewsPortlet)
    label = _(u"Edit News Portlet")
    description = _(u"This portlet displays recent News Items.")
