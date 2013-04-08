from Products.CMFCore.utils import getToolByName


def install(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-collective.portlets.lineage:default')
    return "Ran all import steps."


def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-collective.portlets.lineage:uninstall')
    return "Ran all uninstall steps."
