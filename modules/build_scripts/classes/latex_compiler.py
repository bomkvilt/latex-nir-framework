from __future__  import annotations
from typing import Any, cast
from ...includes import FTexworksConfig, PathWorks
import subprocess
import copy
import time
import sys
import os


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
        pchPath, pchName = None, None
        texFile  = self.docname + '.tex'
        arglists = list[list[str]]()

        # 1. generate args to generate a PCH file
        if (self.mode == 'PCH'):
            # \todo: fix PCH file check
            pchName, pchPath = self._makePCHNameAndPath(self.docname)
            if (self.bForce or not self.IsPCHExists(pchPath)):
                args = self._makePCHBuildArgs(os.path.basename(pchName))
                args.append(os.path.basename(texFile))
                arglists.append(args)
        
        # 2. generate args to run build steps
        for i in range(self.steps):
            args = self._makeStepBuildArgs(pchName, i == self.steps - 1)
            args.append(os.path.basename(texFile))
            arglists.append(args)
        
        return arglists

    def IsPCHExists(self, pchPath):
        docroot = self.conf.GetDocumentRoot()
        return PathWorks.CheckIfFileOrNotExists(docroot, pchPath)

    def _makePCHBuildArgs(self, pchName: str) -> list[str]:
        args = self._makeCommonArgs()
        args.append('-ini')
        args.append('-jobname=' + pchName)
        args.append('&' + self.conf.latexCompiler)
        args.append('mylatexformat.ltx')
        return args

    def _makeStepBuildArgs(self, pchName: str, bLast: bool) -> list[str]:
        args = self._makeCommonArgs()
        if (self.mode == 'PCH'):
            args.append('-fmt=' + pchName)
        if (not bLast):
            args.append('--no-pdf')
        else:
            args += self.conf.latexRenderArgs
        return args

    def _makeCommonArgs(self) -> list[str]:
        args = copy.copy(self.conf.latexArgs)
        args.insert(0, self.conf.latexCompiler)
        args.append('-aux-directory='    + self.auxdir)
        args.append('-output-directory=' + self.outdir)
        return args

    def _makePCHNameAndPath(self, docname: str) -> tuple[str, str]:
        basedir = self.conf.GetLatexOutdir()
        pchName = PathWorks.JoinPath(basedir, docname + '.PCH')
        pchPath = pchName + '.fmt'
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
        
        # \todo add argument check: so, of they contains symbols like [']
        # this means that user passed the args as he is used to write to
        # a command line to make a key=value pair if value contains spaces.
        # This quotes cleans with a console and program will receive an input without 
        # the quotes. Here we have no command line args precessors so we need to pass 
        # args withot the quotes.
        try:
            self._printMessage(print, _bcolors.OKGREEN,
                f'running command {args}')
            
            t0 = time.time()            
            
            subprocess.run(args, cwd=docroot).check_returncode()
            
            self._printMessage(print, _bcolors.OKGREEN, 
                'pass\' compilation time: {:.3f} s'.format(time.time() - t0))
            
        except subprocess.CalledProcessError:

            self._printMessage(sys.exit, _bcolors.FAIL, 
                f'fatal:\n'
                f'build recipe {args} ended with non-zero code ... termination')

    @staticmethod
    def _printMessage(func, color: Any, *pattern: str) -> None:
        func(f'\n\n{color} == {"".join(pattern)}{_bcolors.ENDC}\n\n')
