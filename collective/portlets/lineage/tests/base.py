import unittest2 as unittest
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig
from plone.app.testing import IntegrationTesting
from plone.testing import z2


class LineagePortlets(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.portlets.lineage
        import collective.lineage

        xmlconfig.file('configure.zcml',
                collective.portlets.lineage,
                context=configurationContext
                )

        xmlconfig.file('configure.zcml',
                collective.lineage,
                context=configurationContext
                )
        z2.installProduct(app, 'collective.lineage')

    def setUpPloneSite(self, portal):

        portal.acl_users.userFolderAddUser('admin',
                               'secret',
                               ['Manager'],
                               [])
        portal.acl_users.userFolderAddUser('user1',
                                'secret',
                                ['Member'],
                                [])

        applyProfile(portal, 'collective.portlets.lineage:default')
        applyProfile(portal, 'collective.lineage:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'collective.portlets.lineage')
        z2.uninstallProduct(app, 'collective.lineage')

COLLECTIVE_PORTLETS_LINEAGE_FIXTURE = LineagePortlets()
COLLECTIVE_PORTLETS_LINEAGE_INTEGRATION_TESTING = IntegrationTesting(
        bases=(COLLECTIVE_PORTLETS_LINEAGE_FIXTURE,),
        name="LineagePortlets:Integration"
        )


class LineagePortletsTestCase(unittest.TestCase):
    layer = COLLECTIVE_PORTLETS_LINEAGE_INTEGRATION_TESTING

