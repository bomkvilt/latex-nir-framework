from __future__ import annotations
from ..includes import FTexworksConfig, ModuleBase, ArgParserBuilder
from ..project_tree.module import ProjectTreeModule
from .utils.mml_token_extractor import MMLTokenExtractor
from .settings import mmltexRoot, tokensPath
from .t2t_converter import T2TConverter

import os
import glob



class Type2LaTeXModule(ModuleBase):

    def __init__(self, conf: FTexworksConfig) -> None:
        super().__init__(conf)
        self._converter = T2TConverter(conf)


    def Register(self, builder: ArgParserBuilder) -> None:
        initcmd = builder.addCommand('init', help = 'init module data')
        initcmd.addHandler(self._initModuleHandler)
        
        gencmd = builder.addCommand('gen' , help = 'generate equations')
        gencmd.addArgument('secname', help = 'section name pattern')
        gencmd.addFlag('-f', onAction = True, help = 'force update')
        gencmd.addHandler(self._generateEquationsHandler)

    # protected:

    def _initModuleHandler(self, _) -> None:
        # update token list
        self._updateTokens()
        

    @staticmethod
    def _updateTokens() -> None:
        extractor = MMLTokenExtractor(mmltexRoot)
        extractor.SaveTokensTo(tokensPath)
        print(f'mml tokens were saved to "{tokensPath}"')


    def _generateEquationsHandler(self, args) -> None:
        secname = args.secname
        bForce  = args.f
        assert(secname != None)
        
        # get equation directories paths
        projectTree:ProjectTreeModule
        projectTree = self._moduleManager.GetModule(ProjectTreeModule)
        docinfo = projectTree.ScanDocument(secname)
        resdirs = docinfo.GetAllResources('equations')

        # scan found directories and and convert found equations
        for resdir in resdirs:
            for epspath in glob.iglob(f'{resdir}/*.eps'):
                self._converter.Convert(epspath, bForce)
