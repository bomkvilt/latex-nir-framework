from __future__ import annotations
from ..includes import FTexworksConfig, ModuleBase, ArgParserBuilder
from .project_scanner import ProjectScanner, FRootNode
from .project_initializer import ProjectInitializer



class ProjectTreeModule(ModuleBase):

    def __init__(self, conf: FTexworksConfig) -> None:
        super().__init__(conf)
        # >> init submodules
        self._scanner = ProjectScanner(conf)
        self._initializer = ProjectInitializer(conf)
        # >> create an empty root node
        self._root = self._scanner.CreateRoot()

    def Register(self, builder: ArgParserBuilder) -> None:
        initcmd = builder.addCommand('init')
        initcmd.addHandler(self._onInit)

    def ScanDocument(self, secname: str = '*') -> FRootNode:
        self._scanner.ScanProject(secname, self._root)
        return self._root

    # protected: handlers

    def _onInit(self, _) -> None:
        self.ScanDocument('*')
        self._initializer.InitProject(self._root)
