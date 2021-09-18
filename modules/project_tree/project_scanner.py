from __future__ import annotations
from ..includes import FTexworksConfig, PathWorks
from .classes.name_checker import NameChecker
from .classes.document_strcuture import FRootNode


class ProjectScanner:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf = conf
        self._typemap = dict[str, str](zip(
            conf.resourceTypes.values(), 
            conf.resourceTypes.keys()
        ))
        self._nameChecker = NameChecker()
    
    def CreateRoot(self) -> FRootNode:
        root = FRootNode()
        root.name  = ''
        root.apath = self._conf.GetDocumentRoot()
        root.rpath = '.'
        return root

    def ScanProject(self, secname: str, root: FRootNode) -> None:
        root.ScanChildren(secname, self._typemap, self._conf, self._nameChecker)
