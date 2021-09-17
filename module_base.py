from __future__ import annotations
from .common.arg_parser_builder import ArgParserBuilder
from .texworks_config import FTexworksConfig

# >> forward declarations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .module_manager import ModuleManager
# <<


class ModuleBase:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf          = conf
        self._moduleManager = None

    def Register(self, builder: ArgParserBuilder) -> None:
        raise NotImplementedError()

    def SetModuleManager(self, manager: ModuleManager) -> None:
        self._moduleManager = manager
