from .texworks_config import FTexworksConfig
from .modules.module_manager  import ModuleManager, ModuleBase
from .modules.project_tree.module import ProjectTreeModule
from .modules.type2tex.module import Type2LaTeXModule
from .modules.build_scripts.module import BuildScriptsModule

import os, sys


class Texworks:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._root = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
        self._module_manager = self._createModuleManager(conf)
        
        self.AddModule('project' , ProjectTreeModule(conf))
        self.AddModule('type2tex', Type2LaTeXModule(conf))
        self.AddModule('build'   , BuildScriptsModule(conf))

    def ProcessComandLineArgs(self, argv: list[str] = None) -> None:
        # if argv is empty -- use all command line arguments except the programs's name
        if (argv == None):
            argv = sys.argv[1:]
        # pass the arguments to a module manager's command-buss
        argv = self._normalizeCLAs(argv)
        self._module_manager.ProcessArgv(argv)

    def AddModule(self, name: str, module: ModuleBase) -> None:
        self._module_manager.AddModule(name, module)

# private:

    @staticmethod
    def _createModuleManager(conf: FTexworksConfig) -> ModuleManager:
        manager = ModuleManager(conf)
        return manager

    def _normalizeCLAs(self, args: list[str]) -> list[str]:
        # drop texworks-relative paths to absolute ones
        return list(map(lambda x: x.replace('*/', self._root + '/'), args))
