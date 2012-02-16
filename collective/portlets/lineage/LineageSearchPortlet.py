from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.AdvancedQuery import *

from collective.portlets.lineage import LineagePortletsMessageFactory as _
from collective.portlets.lineage.LineagePortletsCommon import get_subsites

class ILineageSearchPortlet(IPortletDataProvider):
    """ A portlet displaying a (live) search box with the option for a custom title
    """

    enableLivesearch = schema.Bool(
            title = _(u"Enable LiveSearch"),
            description = _(u"Enables the LiveSearch feature, which shows "
                             "live results if the browser supports "
                             "JavaScript."),
            default = True,
            required = False)

    customTitle = schema.TextLine(
            title = _(u"Add a title"),
            description = _(u"Displays a custom title for the search portlet."),
            required = False)
            
    excludeSubsite = schema.Bool(
            title=_(u"Exclude subsites."),
            description = _(u"If selected, search results will not include items added to subsites."),
            default = True,
            required = False)

class Assignment(base.Assignment):
    implements(ILineageSearchPortlet)

    def __init__(self, customTitle="Search", enableLivesearch=True, excludeSubsite=False):
        self.enableLivesearch=enableLivesearch
        self.customTitle=customTitle
        self.excludeSubsite=excludeSubsite

    @property
    def title(self):
        return self.customTitle

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/search.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.navigation_root_url = portal_state.navigation_root_url()
        self.navigation_root_path = portal_state.navigation_root_path()

    def enable_livesearch(self):
        return self.data.enableLivesearch

    def search_form(self):
        return '%s/search_form' % self.navigation_root_url

    def search_action(self):
        return '%s/search_portlet_results' % self.navigation_root_url

    def search_title(self):
        return self.data.customTitle
    
    #not used
    @memoize
    def search_results(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = self.navigation_root_path
        excludeSubsite = self.data.excludeSubsite
        query = catalog.makeAdvancedQuery({'path':path})
        if excludeSubsite:
            query &= ~ In('path', get_subsites(path,catalog), filter=True)
        return catalog.evalAdvancedQuery(query)
    
    def get_subsite_paths(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = self.navigation_root_path
        return get_subsites(path,catalog)
    
    def isParentSiteOnly(self):
        if self.data.excludeSubsite:
            return "true"
        return "false"

class AddForm(base.AddForm):
    form_fields = form.Fields(ILineageSearchPortlet)
    label = _(u"Add Search Portlet")
    description = _(u"This portlet shows a search box.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(ILineageSearchPortlet)
    label = _(u"Edit Search Portlet")
    description = _(u"This portlet shows a search box.")
