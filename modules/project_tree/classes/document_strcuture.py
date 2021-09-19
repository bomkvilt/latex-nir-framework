from __future__ import annotations
from ...includes import PathWorks, FTexworksConfig
from .name_checker import NameChecker
import os


class _subdirScanner:
    @staticmethod
    def IsDir(base: str, name: str) -> bool:
        return os.path.isdir(os.path.join(base, name))
    
    @staticmethod
    def GetSubdirs(base: str, *rest: str) -> list[str]:
        if (len(rest) > 0):
            base = os.path.join(base, *rest)
        if (not PathWorks.CheckIfDirOrNotExists(base)):
            return []
        return [f for f in os.listdir(base) if _subdirScanner.IsDir(base, f)]


class FAbstractDocumentNode:
    def __init__(self) -> None:
        self.name  = '' # directory name
        self.apath = '' # absolute directory path
        self.rpath = '' # document_root relative path
        self.resources = dict[str, list[str]]()

    def GetResources(self, key: str) -> list[str]:
        if (not key in self.resources):
            self.resources[key] = list[str]()
        return self.resources[key]

    def ScanResources(self, typemap: dict[str, str]) -> None:
        assert(self.apath != '')
        assert(self.rpath != '')

        for subdir in _subdirScanner.GetSubdirs(self.apath):
            if (not subdir in typemap):
                continue
            subpath = PathWorks.JoinPath(self.rpath, subdir)
            self.GetResources(typemap[subdir]).append(subpath)

    def _scanSubnodes(self, subroot: str, subname: str, T: type, 
        nodes: dict[str, FAbstractDocumentNode],
        check: callable[[str], None],
        typemap: dict[str, str],
    ) -> None:
        assert(self.apath != '')
        assert(self.rpath != '')

        visited = set([node for node in nodes])
        for subdir in _subdirScanner.GetSubdirs(self.apath, subroot):
            if ((subname in visited) or (subname != '*' and subname != subdir)):
                continue
            # check subdir's name
            check(subdir)
            # create a new node
            node = T()
            node.name = subdir
            node.apath = PathWorks.JoinPath(self.apath, subroot, subdir)
            node.rpath = PathWorks.JoinPath(self.rpath, subroot, subdir)
            node.ScanResources(typemap)
            nodes[subdir] = node
            # prevent non-needded operations
            if (subname != '*'):
                break


# section's part
class FPartNode(FAbstractDocumentNode):
    def __init__(self) -> None:
        super().__init__()


# section
class FSectionNode(FAbstractDocumentNode):
    def __init__(self) -> None:
        super().__init__()
        self.children = dict[str, FPartNode]()

    def GetChildNode(self, name: str) -> FPartNode:
        if (not name in self.children):
            self.children[name] = FPartNode()
        return self.children[name]

    def GetAllResources(self, key: str) -> list[str]:
        reslist = self.GetResources(key)
        for child in self.children.values():
            reslist += child.GetResources(key)
        return reslist

    def ScanChildren(self, subname: str, typemap: dict[str, str], conf: FTexworksConfig,
        nameChecker: NameChecker
    ) -> None:
        typename = FPartNode
        checker = nameChecker.CheckSecpartName
        subroot = conf.parts_dir
        self._scanSubnodes(subroot, subname, typename, self.children, checker, typemap)


class FRootNode(FAbstractDocumentNode):
    def __init__(self) -> None:
        super().__init__()
        self.children = dict[str, FSectionNode]()

    def GetChildNode(self, name: str) -> FSectionNode:
        if (not name in self.children):
            self.children[name] = FSectionNode()
        return self.children[name]

    def GetAllResources(self, key: str, bGlobal: bool = False) -> list[str]:
        reslist = self.GetResources(key)
        for child in self.children.values():
            reslist += child.GetAllResources(key)
        if (bGlobal):
            prefix  = os.path.relpath(self.apath, self.rpath)
            reslist = [PathWorks.JoinPath(prefix, path) for path in reslist]
        return reslist

    def ScanChildren(self, subname: str, typemap: dict[str, str], conf: FTexworksConfig,
        nameChecker: NameChecker
    ) -> None:
        typename = FSectionNode
        checker = nameChecker.CheckSectionName
        subroot = conf.sections_dir
        self._scanSubnodes(subroot, subname, typename, self.children, checker, typemap)
        # scan sections' parts
        for child in self.children.values():
            child.ScanChildren('*', typemap, conf, nameChecker)
