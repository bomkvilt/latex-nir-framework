from .texworks_config import FTexworksConfig
from .module_manager  import ModuleManager, ModuleBase
from .modules.project_tree.module import ProjectTreeModule
from .modules.type2tex.module import Type2LaTeXModule

import os, sys


class Texworks:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._root = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
        self._conf = conf
        self._module_manager = self._createModuleManager()

        self.AddModule('project' , ProjectTreeModule(conf))
        self.AddModule('type2tex', Type2LaTeXModule (conf))


    def ProcessComandLineArgs(self, argv: list[str] = None) -> None:
        if (argv == None):
            argv = sys.argv[1:]
        argv = self._normalizeCLAs(argv)
        self._module_manager.ProcessArgv(argv)


    def AddModule(self, name: str, module: ModuleBase) -> None:
        self._module_manager.AddModule(name, module)


# private:

    def _createModuleManager(self) -> ModuleManager:
        manager = ModuleManager(self._conf)
        return manager


    def _normalizeCLAs(self, args: list[str]) -> list[str]:
        return list(map(lambda x: x.replace('*/', self._root + '/'), args))
