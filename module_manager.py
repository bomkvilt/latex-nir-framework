from typing import Type
from .common.arg_parser_builder import ArgParserBuilder
from .module_base import ModuleBase
from .texworks_config import FTexworksConfig



class ModuleManager:

    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf    = conf
        self._modules = dict[Type, ModuleBase]()
        self._argsBuilder = ArgParserBuilder()


    def AddModule(self, cmd: str, module: ModuleBase) -> None:
        # add module to module manager
        self._modules[type(module)] = module

        # presetup module
        module.SetModuleManager(self)

        # register module to command line argument parsing system
        subBuilder = self._argsBuilder.addCommand(cmd)
        module.Register(subBuilder)


    def GetModule(self, type: Type) -> ModuleBase:
        if (type in self._modules):
            return self._modules[type]
        
        raise TypeError('passed type is not already registered')


    def ProcessArgv(self, argv: list[str]) -> None:
        self._argsBuilder.parseArgs(argv)
