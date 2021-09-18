from __future__  import annotations
from typing import cast
from ...includes import FTexworksConfig, PathWorks
import subprocess
import copy
import time
import sys


class _compileOrder:
    def __init__(self, conf: FTexworksConfig, 
        docname: str, 
        mode   : str, 
        steps  : int, 
        bForce : bool
    ) -> None:
        # settings
        self.conf    = conf
        self.docname = docname
        self.mode    = mode
        self.steps   = steps
        self.bForce  = bForce
        # cash data
        self.auxdir = self.conf.GetLatexAUXdir()
        self.outdir = self.conf.GetLatexOutdir()

    def GenerateCLAs(self) -> list[list[str]]:
        pchPath  = None
        texFile  = self.docname + '.tex'
        arglists = list[list[str]]()

        # 1. generate args to generate a PCH file
        if (self.mode == 'PCH'):
            pchName, pchPath = self._makePCHNameAndPath(self.docname)
            if (self.bForce or not PathWorks.CheckIfFileOrNotExists(pchPath)):
                args = self._makePCHBuildArgs(pchName)
                args.append(texFile)
                arglists.append(args)
        
        # 2. generate args to run build steps
        for i in range(self.steps):
            args = self._makeStepBuildArgs(pchPath, i == self.steps - 1)
            args.append(texFile)
            arglists.append(args)
        
        return arglists

    def _makePCHBuildArgs(self, pchName: str) -> list[str]:
        args = self._makeCommonArgs()
        args.append('-ini')
        args.append('-jobname=' + pchName)
        args.append('&' + self.conf.latexCompiler)
        args.append('mylatexformat.ltx')
        return args

    def _makeStepBuildArgs(self, pchPath: str, bLast: bool) -> list[str]:
        args = self._makeCommonArgs()
        if (self.mode == 'PCH'):
            args.append('-fmt=' + pchPath)
        if (not bLast):
            args.append('--no-pdf')
            args += self.conf.latexRenderArgs
        return args

    def _makeCommonArgs(self) -> list[str]:
        args = copy.copy(self.conf.latexArgs)
        args.insert(0, self.conf.latexCompiler)
        args.append('-aux-directory=' + self.auxdir)
        args.append('-output-directory=' + self.outdir)
        return args

    def _makePCHNameAndPath(self, docname: str) -> tuple[str, str]:
        basedir = self.conf.GetLatexOutdir()
        pchName = docname + '.PCH'
        pchPath = PathWorks.JoinPath(basedir, pchName + '.fmt')
        return (pchName, pchPath)


class _bcolors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKCYAN  = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'
    BOLD    = '\033[1m'
    UNDERLINE = '\033[4m'


class LatexCompiler:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf = conf

    def CompileDocument(self, docname: str, mode: str, steps: int, bForce: bool) -> None:
        order = _compileOrder(self._conf, docname, mode, steps, bForce)
        for args in order.GenerateCLAs():
            self._runScript(args)

# private:

    def _runScript(self, args: list[str]) -> None:
        docroot = self._conf.GetDocumentRoot()
        try:
            t0 = time.time()
            subprocess.run(args, shell = True, cwd = docroot).check_returncode()
            t1 = time.time()
            print(
                f'\n\n{_bcolors.OKGREEN}' + 
                ' == comping pass\' time: {:.3f} s'.format(t1 - t0) +
                f'{_bcolors.ENDC}\n\n'
            )
        except subprocess.CalledProcessError:
            sys.exit(
                f'\n\n{_bcolors.FAIL}'
                f' == fatal:\n'
                f'build recipe {args} ended with non-zero code ... termination'
                f'{_bcolors.ENDC}\n\n'
            )
