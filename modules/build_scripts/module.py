from __future__ import annotations
from ..includes import FTexworksConfig, ModuleBase, ArgParserBuilder, assert_all
from .classes.latex_compiler import LatexCompiler, TCompilerSettings



class BuildScriptsModule(ModuleBase):

    def __init__(self, conf: FTexworksConfig) -> None:
        super().__init__(conf)
        self._latexCompiler = LatexCompiler(conf)

    def Register(self, builder: ArgParserBuilder) -> None:
        # subcommand:: init
        cmd = builder.addCommand('init')
        cmd.addHandler(self._onInit)

        # subcommand:: compile
        cmd = builder.addCommand('compile')
        cmd.addArgument(
            'docname', 
            help = 'name of a document with not .tex extension', )
        cmd.addArgument(
            '--mode', 
            help     = 'build optimisation mode',
            required = False, 
            default  = 'raw',
            choices  = ['raw', 'PCH'], )
        cmd.addArgument(
            '--steps', 
            help     = 'number of LaTeX compiler steps',
            required = False, 
            default  = 2,
            choices  = [str(n) for n in range(0, 5)], )
        cmd.addFlag(
            '--bib', 
            help  = 'make biber pass',
            hasNo = False, )
        cmd.addFlag(
            '-f',
            help='force PCH compilation', )
        cmd.addHandler(self._onBuild)

        # subcommand:: clear
        cmd = builder.addCommand('clear')
        cmd.addArgument(
            'docname', 
            help = 'name of a document with not .tex extension', )
        cmd.addHandler(self._onClear)

    # protected: handlers

    def _onInit(self, args) -> None:
        # do nothing
        pass

    def _onBuild(self, args) -> None:
        settings = TCompilerSettings()
        settings.mode    = args.mode
        settings.steps   = int(args.steps)
        settings.docname = args.docname
        settings.bbiber  = args.bib
        settings.bforce  = args.f

        self._latexCompiler.CompileDocument(settings)

    def _onClear(self, args) -> None:
        # \todo write a clear script
        pass
