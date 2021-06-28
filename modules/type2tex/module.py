from __future__ import annotations
from ..includes import FTexworksConfig, ModuleBase, ArgParserBuilder
from .utils.mml_token_extractor import MMLTokenExtractor

import os

_moduleRoot = os.path.dirname(os.path.realpath(__file__))
_mmltexRoot = os.path.join(_moduleRoot, 'mmltex')
_tokensPath = os.path.join(_moduleRoot, 'utils/mml_tokens.json')



class Type2LaTeXModule(ModuleBase):

    def __init__(self, conf: FTexworksConfig) -> None:
        super().__init__(conf)

    def Register(self, builder: ArgParserBuilder) -> None:
        initcmd = builder.addCommand('init', help = 'init module data')
        initcmd.addHandler(self._initModuleHandler)
        
        gencmd = builder.addCommand('gen' , help = 'generate equations')
        gencmd.addArgument('secname', help = 'section name pattern')
        gencmd.addHandler(self._generateEquationsHandler)


    # protected:

    def _initModuleHandler(self, _) -> None:
        # update tocken list
        self._updateTockens()
        

    @staticmethod
    def _updateTockens() -> None:
        extractor = MMLTokenExtractor(_mmltexRoot)
        extractor.SaveTokensTo(_tokensPath)
        print(f'mml tokens were saved to "{_tokensPath}"')


    def _generateEquationsHandler(self, args) -> None:
        secname = args.secname
        pass
