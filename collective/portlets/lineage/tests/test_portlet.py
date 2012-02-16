import unittest2 as unittest
from plone.app.testing import login
from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite
from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlets.lineage import LineageNewsPortlet, LineageEventsPortlet, LineageRecentPortlet, LineageReviewPortlet

from collective.portlets.lineage.tests.base import LineagePortletsTestCase


class TestPortlet(LineagePortletsTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, 'admin')
        
    def test_events_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlets.lineage.LineageEventsPortlet')
        self.assertEquals(portlet.addview,
                          'collective.portlets.lineage.LineageEventsPortlet')
    
    def test_news_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlets.lineage.LineageNewsPortlet')
        self.assertEquals(portlet.addview,
                          'collective.portlets.lineage.LineageNewsPortlet')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        for p in (LineageEventsPortlet, LineageNewsPortlet):
            portlet = p.Assignment()
            self.failUnless(IPortletAssignment.providedBy(portlet))
            self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_news_portlet_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlets.lineage.LineageNewsPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   LineageNewsPortlet.Assignment))

    def test_news_portlet_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.portal.REQUEST

        mapping['foo'] = LineageNewsPortlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, LineageNewsPortlet.EditForm))

    def test_events_portlet_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlets.lineage.LineageEventsPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   LineageEventsPortlet.Assignment))

    def test_events_portlet_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.portal.REQUEST

        mapping['foo'] = LineageEventsPortlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, LineageEventsPortlet.EditForm))


    def test_obtain_renderer(self):
        context = self.portal
        request = self.portal.REQUEST
        view = self.portal.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        for p in (LineageEventsPortlet, LineageNewsPortlet):
            assignment = p.Assignment()

            renderer = getMultiAdapter(
                (context, request, view, manager, assignment), IPortletRenderer)
            self.failUnless(isinstance(renderer, p.Renderer))


class TestRenderer(LineagePortletsTestCase):
    ## These don't really test anything
    
    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, 'admin')

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment
        # constructor.
        assignment = assignment or LineageEventsPortlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        # TODO: Pass any keyword arguments to the Assignment constructor.
        for p in (LineageEventsPortlet, LineageNewsPortlet):
            r = self.renderer(context=self.portal,
                              assignment=p.Assignment())
            r = r.__of__(self.portal)
            r.update()
            output = r.render()
            #print "output %s" % output
            # TODO: Test output

class LineageEventsPortletTest(LineagePortletsTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, 'admin')
        self.portal.portal_types['Child Folder'].global_allow = True
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        
    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or LineageEventsPortlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlets.lineage.LineageEventsPortlet')
        self.assertEquals(portlet.addview, 'collective.portlets.lineage.LineageEventsPortlet')

    def test_events_custom_title(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        context = self.portal.site1
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(customTitle="Frojbalc", count=5, state=('draft',), excludeSubsite=False))
        self.assertEquals("Frojbalc", r.data.customTitle)
   
    def test_events_default_title(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        context = self.portal.site1
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',), excludeSubsite=False))
        self.assertEquals("Lineage Events", r.data.customTitle)

    def test_published_events_parent_exclude_subsite(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Event', 'e1')
        self.portal.site1.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal
        
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=True))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_events()))
        
    def test_published_events_subsite_exclude_subsite(self):
        self.portal.invokeFactory('Event', 'p1e1')
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Event', 'e1')
        self.portal.site1.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal.site1
        
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=True))
        self.assertEquals(1, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=True))
        self.assertEquals(2, len(r.published_events()))
        
    def test_published_events_nested_subsite_exclude_subsite(self):

        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Child Folder', 'site1_subsite')
        
        self.portal.invokeFactory('Event', 'p1e1')
        self.portal.site1.invokeFactory('Event', 's1e1')
        self.portal.site1.site1_subsite.invokeFactory('Event', 'e1')
        self.portal.site1.site1_subsite.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.site1_subsite.e1, 'publish')
        context = self.portal.site1.site1_subsite
        
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=True))
        self.assertEquals(1, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=True))
        self.assertEquals(2, len(r.published_events()))
        
        
    #Now test if excludeSubsite=False
    
    def test_published_events_parent_include_subsite(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Event', 'e1')
        self.portal.site1.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal
        
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=False))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=False))
        self.assertEquals(1, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=False))
        self.assertEquals(2, len(r.published_events()))        

    def test_published_events_subsite_include_subsite(self):
        self.portal.invokeFactory('Event', 'p1e1')
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Event', 'e1')
        self.portal.site1.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal.site1
        
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=False))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=False))
        self.assertEquals(1, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=False))
        self.assertEquals(2, len(r.published_events()))
        
    def test_published_events_nested_subsite_include_subsite(self):

        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Child Folder', 'site1_subsite')
        
        self.portal.invokeFactory('Event', 'p1e1')
        self.portal.site1.invokeFactory('Event', 's1e1')
        self.portal.site1.site1_subsite.invokeFactory('Event', 'e1')
        self.portal.site1.site1_subsite.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.site1_subsite.e1, 'publish')
        context = self.portal.site1.site1_subsite
        
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=False))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=False))
        self.assertEquals(1, len(r.published_events()))
        r = self.renderer(context=context, assignment=LineageEventsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=False))
        self.assertEquals(2, len(r.published_events()))


class LineageNewsPortletTest(LineagePortletsTestCase):
    
    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, 'admin')
        self.portal.portal_types['Child Folder'].global_allow = True
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        
    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or LineageNewsPortlet.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
    
    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlets.lineage.LineageNewsPortlet')
        self.assertEquals(portlet.addview, 'collective.portlets.lineage.LineageNewsPortlet')
        
    def test_news_custom_title(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        context = self.portal.site1
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(customTitle="Frojbalc", count=5, state=('draft',), excludeSubsite=False))
        self.assertEquals("Frojbalc", r.data.customTitle)

    def test_news_default_title(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        context = self.portal.site1
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',), excludeSubsite=False))
        self.assertEquals("Lineage News", r.data.customTitle)

    def test_published_news_parent_exclude_subsite(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('News Item', 'e1')
        self.portal.site1.invokeFactory('News Item', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal
        
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=True))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_news_items()))
        
    def test_published_news_subsite_exclude_subsite(self):
        self.portal.invokeFactory('News Item', 'p1e1')
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('News Item', 'e1')
        self.portal.site1.invokeFactory('News Item', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal.site1
        
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=True))
        self.assertEquals(1, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=True))
        self.assertEquals(2, len(r.published_news_items()))
        
    def test_published_news_nested_subsite_exclude_subsite(self):

        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Child Folder', 'site1_subsite')
        
        self.portal.invokeFactory('News Item', 'p1e1')
        self.portal.site1.invokeFactory('News Item', 's1e1')
        self.portal.site1.site1_subsite.invokeFactory('News Item', 'e1')
        self.portal.site1.site1_subsite.invokeFactory('News Item', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.site1_subsite.e1, 'publish')
        context = self.portal.site1.site1_subsite
        
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=True))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=True))
        self.assertEquals(1, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=True))
        self.assertEquals(2, len(r.published_news_items()))
        
        
    #Now test if excludeSubsite=False
    
    def test_published_news_parent_include_subsite(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('News Item', 'e1')
        self.portal.site1.invokeFactory('News Item', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal
        
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=False))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=False))
        self.assertEquals(1, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=False))
        self.assertEquals(2, len(r.published_news_items()))        

    def test_published_news_subsite_include_subsite(self):
        self.portal.invokeFactory('News Item', 'p1e1')
        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('News Item', 'e1')
        self.portal.site1.invokeFactory('News Item', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.e1, 'publish')
        context = self.portal.site1
        
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=False))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=False))
        self.assertEquals(1, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=False))
        self.assertEquals(2, len(r.published_news_items()))
        
    def test_published_news_nested_subsite_include_subsite(self):

        self.portal.invokeFactory('Child Folder', 'site1')
        self.portal.site1.invokeFactory('Child Folder', 'site1_subsite')
        
        self.portal.invokeFactory('News Item', 'p1e1')
        self.portal.site1.invokeFactory('News Item', 's1e1')
        self.portal.site1.site1_subsite.invokeFactory('News Item', 'e1')
        self.portal.site1.site1_subsite.invokeFactory('News Item', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.site1.site1_subsite.e1, 'publish')
        context = self.portal.site1.site1_subsite
        
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('draft',),excludeSubsite=False))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', ),excludeSubsite=False))
        self.assertEquals(1, len(r.published_news_items()))
        r = self.renderer(context=context, assignment=LineageNewsPortlet.Assignment(count=5, state=('published', 'private',),excludeSubsite=False))
        self.assertEquals(2, len(r.published_news_items()))

class LineageRecentPortletTest(LineagePortletsTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, 'admin')
        self.portal.portal_types['Child Folder'].global_allow = True
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or LineageRecentPortlet.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlets.lineage.LineageRecentPortlet')
        self.assertEquals(portlet.addview, 'collective.portlets.lineage.LineageRecentPortlet')

    def test_exclude_subsite_checkbox(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        context = self.portal
        
        r = self.renderer(context=context, assignment=LineageRecentPortlet.Assignment(excludeSubsite=False))
        self.assertEquals(False, r.is_parent_site_only())
        
        r = self.renderer(context=context, assignment=LineageRecentPortlet.Assignment(excludeSubsite=True))
        self.assertEquals(True, r.is_parent_site_only())
    
    def test_subsite_content_excluded(self):
        self.portal.invokeFactory('Child Folder','site1')
        self.portal.site1.invokeFactory('News Item', 's1_n1')
        context = self.portal

        r = self.renderer(context=context, assignment=LineageRecentPortlet.Assignment(count=20, excludeSubsite=True))
        self.failIf('s1_n1' in [i.id for i in r.recent_items()])

    def test_subsite_content_included(self):
        self.portal.invokeFactory('Child Folder','site1')
        self.portal.site1.invokeFactory('News Item', 's1_n1')
        self.portal.site1.portal_workflow.doActionFor(self.portal.site1.s1_n1, 'publish')
        context = self.portal

        r = self.renderer(context=context, assignment=LineageRecentPortlet.Assignment(count=20, excludeSubsite=False))
        self.failUnless('s1_n1' in [i.id for i in r.recent_items()])


class LineageReviewPortletTest(LineagePortletsTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        login(self.portal, 'admin')
        self.portal.portal_types['Child Folder'].global_allow = True
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.portal.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or LineageReviewPortlet.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlets.lineage.LineageReviewPortlet')
        self.assertEquals(portlet.addview, 'collective.portlets.lineage.LineageReviewPortlet')

    def test_exclude_subsite_checkbox(self):
        self.portal.invokeFactory('Child Folder', 'site1')
        context = self.portal
        
        r = self.renderer(context=context, assignment=LineageReviewPortlet.Assignment(excludeSubsite=False))
        #self.assertEquals(False, r.is_parent_site_only())
        self.assertEquals(False, r.data.excludeSubsite)
        
        r = self.renderer(context=context, assignment=LineageReviewPortlet.Assignment(excludeSubsite=True))
        self.assertEquals(True, r.data.excludeSubsite)

    def test_subsite_content_excluded(self):
        self.portal.invokeFactory('Child Folder','site1')
        self.portal.site1.invokeFactory('News Item', 's1_n1')
        self.portal.invokeFactory('Document','page1')
        context = self.portal
        self.portal.site1.portal_workflow.doActionFor(self.portal.site1.s1_n1, 'submit')
        self.portal.portal_workflow.doActionFor(self.portal.page1, 'submit')
        r = self.renderer(context=context, assignment=LineageReviewPortlet.Assignment(excludeSubsite=True))

        self.failIf('s1_n1' in [i['title'] for i in r.review_items()])
        self.failUnless('page1' in [i['title'] for i in r.review_items()])

    def test_subsite_content_included(self):
        self.portal.invokeFactory('Child Folder','site1')
        self.portal.site1.invokeFactory('News Item', 's1_n1')
        self.portal.invokeFactory('Document', 'page1')
        self.portal.site1.portal_workflow.doActionFor(self.portal.site1.s1_n1, 'submit')
        self.portal.portal_workflow.doActionFor(self.portal.page1, 'submit')
        context = self.portal

        r = self.renderer(context=context, assignment=LineageReviewPortlet.Assignment(excludeSubsite=False))
        self.failUnless('page1' in [i['title'] for i in r.review_items()])
        self.failUnless('s1_n1' in [i['title'] for i in r.review_items()])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPortlet))
    suite.addTest(unittest.makeSuite(TestRenderer))
    suite.addTest(unittest.makeSuite(LineageEventsPortletTest))
    suite.addTest(unittest.makeSuite(LineageNewsPortletTest))
    suite.addTest(unittest.makeSuite(LineageRecentPortletTest))
    suite.addTest(unittest.makeSuite(LineageReviewPortletTest))
    return suite
