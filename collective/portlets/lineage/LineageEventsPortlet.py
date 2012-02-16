from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey
from plone.app.layout.navigation.root import getNavigationRootObject

from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.AdvancedQuery import *

from collective.portlets.lineage import LineagePortletsMessageFactory as _
from collective.portlets.lineage.LineagePortletsCommon  import get_subsites

class ILineageEventsPortlet(IPortletDataProvider):

    customTitle = schema.TextLine(
            title = _(u"Add a title"),
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
                               description = _(u"If selected, search results will not include events added to subsites."),
                               default = False,
                               required = False)                         

class Assignment(base.Assignment):
    
    implements(ILineageEventsPortlet)
    
    customTitle = u"Lineage Events"
    count = 5
    state = ('published')
    excludeSubsite = False
    
    def __init__(self, customTitle=u"Lineage Events", count=5, state=('published', ), excludeSubsite=False):
        self.customTitle = customTitle
        self.count = count
        self.state = state
        self.excludeSubsite = excludeSubsite

    @property
    def title(self):
        if self.customTitle is None:
            self.customTitle = u"Lineage Events"
        return self.customTitle

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('templates/events.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.navigation_root_url = portal_state.navigation_root_url()
        self.portal = portal_state.portal()
        self.navigation_root_path = portal_state.navigation_root_path()

        self.have_events_folder = 'events' in getNavigationRootObject(self.context,         
                                                                      self.portal).objectIds()


    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self._data())

    def published_events(self):
        return self._data()

    def all_events_link(self):
        if self.have_events_folder:
            return '%s/events' % self.navigation_root_url
        else:
            return '%s/events_listing' % self.navigation_root_url

    def prev_events_link(self):
        if (self.have_events_folder and
            'aggregator' in self.portal['events'].objectIds() and
            'previous' in self.portal['events']['aggregator'].objectIds()):
            return '%s/events/aggregator/previous' % self.navigation_root_url
            
        elif (self.have_events_folder and
            'previous' in self.portal['events'].objectIds()):
            return '%s/events/previous' % self.navigation_root_url
        else:
            return None

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        limit = self.data.count
        state = self.data.state
        path = self.navigation_root_path
        excludeSubsite = self.data.excludeSubsite
        query = catalog.makeAdvancedQuery({'portal_type':'Event', 'review_state':state, 'end':{'query':DateTime(),'range':'min'}, 'path':path, 'sort_on':'start','sort_limit':limit})
        if excludeSubsite:
            query &= ~ In('path', get_subsites(path,catalog), filter=True)
        results = catalog.evalAdvancedQuery(query,('start',),)
        return results[:limit]                   

class AddForm(base.AddForm):
    form_fields = form.Fields(ILineageEventsPortlet)
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")

    def create(self, data):
        return Assignment(**data)
        
class EditForm(base.EditForm):
    form_fields = form.Fields(ILineageEventsPortlet)
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
