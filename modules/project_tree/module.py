from __future__ import annotations
from ..includes import FTexworksConfig, ModuleBase, ArgParserBuilder
from .project_scanner import ProjectScanner, FDocumentInfo
from .project_initializer import ProjectInitializer



class ProjectTreeModule(ModuleBase):

    def __init__(self, conf: FTexworksConfig) -> None:
        super().__init__(conf)

        # >> init submodules
        self._scanner     = ProjectScanner(conf)
        self._initializer = ProjectInitializer(conf)

        # >> create an empty project structure
        self._docInfo = FDocumentInfo()
        self._docInfo.MarkAsDefault()


    def Register(self, builder: ArgParserBuilder) -> None:
        initcmd = builder.addCommand('init')
        initcmd.addHandler(self._onModuleCalled)


    def ScanDocument(self, secname: str) -> FDocumentInfo:
        if (self._docInfo.IsDefault()):
            self._scanProject(secname)
        return self._docInfo


    # protected:

    def _onModuleCalled(self, _) -> None:
        # scan project structure
        self.ScanDocument('*')

        # init project files
        self._initializer.InitProject(self._docInfo)


    # protected:

    def _scanProject(self, secname: str) -> None:
        self._docInfo = self._scanner.ScanDocuments(secname)
