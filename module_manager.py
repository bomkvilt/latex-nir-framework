from typing import Type
from .common.arg_parser_builder import ArgParserBuilder
from .module_base import ModuleBase
from .texworks_config import FTexworksConfig



class ModuleManager:

    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf     = conf
        self._modules  = dict[Type, ModuleBase]()
        self._commands = dict[str , ModuleBase]()
        self._argsBuilder = self._createArgparser()


    def AddModule(self, cmd: str, module: ModuleBase) -> None:
        # add module to module manager
        self._modules[type(module)] = module
        self._commands[cmd] = module

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


    # protected:

    def _createArgparser(self) -> ArgParserBuilder:
        parser  = ArgParserBuilder()
        
        # >> create a command to init modules
        initcmd = parser.addCommand('init', help='initialize all texworks modules')
        initcmd.addArgument('--moduleName', help='specific module name to initialize',
            required = False, default = '')
        initcmd.addHandler(self._initModulesHandler)
        
        return parser


    def _initModulesHandler(self, args):
        moduleName = args.moduleName
        if (moduleName != ''):
            self._initModule(moduleName)
            return
        
        for cmd in self._commands.keys():
            self._initModule(cmd)


    def _initModule(self, moduleName: str) -> None:
        self.ProcessArgv([moduleName, 'init'])
