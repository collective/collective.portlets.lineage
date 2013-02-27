from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.formlib import form
from zope.interface import implements
from zope import schema

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base


from Products.AdvancedQuery import *
from collective.portlets.lineage import LineagePortletsMessageFactory as _
from collective.portlets.lineage.LineagePortletsCommon import get_subsites


class ILineageReviewPortlet(IPortletDataProvider):

    excludeSubsite = schema.Bool(title=_(u"Exclude subsites"),
                                 description=_(u"If selected, results will \
                                               not include items contained \
                                               in subsites."),
                                 default=False,
                                 required=False)


class Assignment(base.Assignment):
    implements(ILineageReviewPortlet)

    def __init__(self, excludeSubsite=False):
        self.excludeSubsite = excludeSubsite

    @property
    def title(self):
        return _(u"Review list")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/review.pt')

    title = _('box_review_list', default=u"Review List")

    @property
    def anonymous(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    @property
    def available(self):
        return not self.anonymous and len(self._data())

    @property
    def nav_root(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.navigation_root_path()

    def review_items(self):
        return self._data()

    def full_review_link(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        # check if user is allowed to Review Portal Content here
        if mtool.checkPermission('Review portal content', context):
            return '%s/full_review_list' % context.absolute_url()
        else:
            return None

    @memoize
    def _data(self):
        if self.anonymous:
            return []
        context = aq_inner(self.context)
        workflow = getToolByName(context, 'portal_workflow')

        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        getMember = getToolByName(context, 'portal_membership').getMemberById
        getIcon = plone_view.getIcon
        toLocalizedTime = plone_view.toLocalizedTime

        excludeSubsite = self.data.excludeSubsite
        catalog = getToolByName(context, 'portal_catalog')

        idnormalizer = queryUtility(IIDNormalizer)
        norm = idnormalizer.normalize
        objects = workflow.getWorklistsResults()
        items = []
        # use advanced query to filter out content in subsites
        if excludeSubsite:
            query = catalog.makeAdvancedQuery({'review_state': 'pending',
                                              'path': self.nav_root})
            query &= ~In('path', get_subsites(self.nav_root, catalog),
                         filter=True)
            results = catalog.evalAdvancedQuery(query)
            for obj in results:
                items.append(dict(
                    path=obj.getURL(),
                    title=obj.pretty_title_or_id(),
                    description=obj.Description,
                    icon=getIcon(obj).html_tag(),
                    creator=obj.Creator,
                    review_state=obj.review_state,
                    review_state_class='state-%s ' % norm(obj.review_state),
                    mod_date=toLocalizedTime(obj.ModificationDate),
                ))
            return items
        for obj in objects:
            review_state = workflow.getInfoFor(obj, 'review_state')
            creator_id = obj.Creator()
            creator = getMember(creator_id)
            if creator:
                creator_name = creator.getProperty('fullname', '') or \
                    creator_id
            else:
                creator_name = creator_id

            items.append(dict(
                path=obj.absolute_url(),
                title=obj.pretty_title_or_id(),
                description=obj.Description(),
                icon=getIcon(obj).html_tag(),
                creator=obj.Creator(),
                review_state=review_state,
                review_state_class='state-%s ' % norm(review_state),
                mod_date=toLocalizedTime(obj.ModificationDate()),
            ))
        return items


class AddForm(base.AddForm):
    form_fields = form.Fields(ILineageReviewPortlet)
    label = _(u"Add Review Portlet")
    description = _(u"This portlet displays a queue of \
                    documents awaiting review.")

    def create(self, data):
        return Assignment(excludeSubsite=data.get('excludeSubsite'))


class EditForm(base.EditForm):
    form_fields = form.Fields(ILineageReviewPortlet)
    label = _(u"Edit Review Portlet")
    description = _(u"This portlet displays a queue of \
                    documents awaiting review.")
