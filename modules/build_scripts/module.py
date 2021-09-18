from __future__ import annotations
from ..includes import FTexworksConfig, ModuleBase, ArgParserBuilder, PathWorks
from .classes.latex_compiler import LatexCompiler



class BuildScriptsModule(ModuleBase):

    def __init__(self, conf: FTexworksConfig) -> None:
        super().__init__(conf)
        self._latexCompiler = LatexCompiler(conf)

    def Register(self, builder: ArgParserBuilder) -> None:
        # subcommand:: init
        cmd = builder.addCommand('init')
        cmd.addHandler(self._onInit)

        # subcommand:: .
        cmd = builder.addCommand('compile')
        cmd.addArgument('docname', help = 'name of a document with not .tex extension')
        cmd.addArgument('--mode' , help = 'build optimisation mode',
            required = False, 
            default = 'raw',
            choices = ['raw', 'PCH']
        )
        cmd.addArgument('--steps', help = 'number of LaTeX compiler steps',
            required = False, 
            default = 2,
            choices = [str(n) for n in range(0, 3)]
        )
        cmd.addFlag('-f', help = 'force PCH compilation')
        cmd.addHandler(self._onBuild)

        # subcommand:: clear
        cmd = builder.addCommand('clear')
        cmd.addArgument('docname', help = 'name of a document with not .tex extension')
        cmd.addHandler(self._onClear)

# protected: handlers

    def _onInit(self, args) -> None:
        # do nothing
        pass

    def _onBuild(self, args) -> None:
        assert(args.f != None)
        assert(args.mode != None)
        assert(args.steps != None)
        assert(args.docname != None)
        self._latexCompiler.CompileDocument(
            args.docname,
            args.mode,
            int(args.steps),
            args.f
        )

    def _onClear(self, args) -> None:
        # \todo write a clear script
        pass
