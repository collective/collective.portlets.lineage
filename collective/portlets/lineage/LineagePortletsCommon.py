from collective.lineage.interfaces import IChildSite
from collective.portlets.lineage import LineagePortletsMessageFactory as _

def get_subsites(path, catalog):
    subsites = catalog(path=path, object_provides=IChildSite.__identifier__)
    subsite_paths = list()
    if subsites:
        subsite_paths = [b.getPath() for b in subsites]
        if path in subsite_paths:
            subsite_paths.remove(path)
    return subsite_paths
    

