from __future__  import annotations
from typing import Any
import argparse
import copy
import os
import shutil
import subprocess
import sys
import time

from ...includes import FTexworksConfig, PathWorks, assert_all


class _COLORS:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


class TCompilerSettings:
    def __init__(self):
        self.mode: str
        self.steps: int
        self.docname: str
        self.bbiber: bool
        self.bforce: bool

    def Check(self):
        assert_all(
            self.mode,
            self.steps,
            self.docname,
            self.bforce,
            self.bbiber,
            mode='non-none'
        )


class _TCLAGenerator:
    def __init__(
        self, conf: FTexworksConfig, settings: TCompilerSettings):
        # settings
        self.conf    = conf
        self.docname = settings.docname
        self.mode    = settings.mode
        self.steps   = settings.steps
        self.bforce  = settings.bforce
        self.bbiber  = settings.bbiber
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
            if (self.bforce or not self.IsPCHExists(pchPath)):
                args = self._makePCHBuildArgs(os.path.basename(pchName))
                args.append(os.path.basename(texFile))
                arglists.append(args)

        # 2. generate args to run build steps
        def make_build_step_args(i: int):
            args = self._makeStepBuildArgs(pchName, i == self.steps - 1)
            args.append(os.path.basename(texFile))
            arglists.append(args)

        for i in range(min(self.steps, 1)):
            make_build_step_args(i)
        
        if self.bbiber:
            args = self._MakeBiberArgs()
            args.append(self.docname)
            arglists.append(args)

        for i in range(1, self.steps):
            make_build_step_args(i)

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

    def _MakeBiberArgs(self) -> list[str]:
        args = copy.copy(self.conf.biblioArgs)
        args.insert(0, self.conf.biblioCompiler)
        args.append('-output_directory=' + self.outdir)
        return args

    def _makeCommonArgs(self) -> list[str]:
        args = copy.copy(self.conf.latexArgs)
        args.insert(0, self.conf.latexCompiler)
        args.append('-aux-directory='    + self.auxdir)
        args.append('-output-directory=' + self.outdir)
        return args

    def _makePCHNameAndPath(self, docname: str) -> tuple[str, str]:
        pchName = PathWorks.JoinPath(self.outdir, docname + '.PCH')
        pchPath = pchName + '.fmt'
        return (pchName, pchPath)


class LatexCompiler:
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf = conf

    def CompileDocument(self, settings: TCompilerSettings) -> None:
        settings.Check()

        docroot = self._conf.GetDocumentRoot()
        outroot = self._conf.GetLatexOutroot()
        pdfroot = self._conf.GetPDFRoot()

        generator = _TCLAGenerator(self._conf, settings)
        for args in generator.GenerateCLAs():
            self._runScript(args, docroot=docroot)

        self._copyPDF(outroot, pdfroot, settings.docname)

    # private:

    def _runScript(self, args: list[str], docroot: str) -> None:
        # \todo add argument check: so, of they contains symbols like [']
        # this means that user passed the args as he is used to write to
        # a command line to make a key=value pair if value contains spaces.
        # This quotes cleans with a console and program will receive an input without 
        # the quotes. Here we have no command line args precessors so we need to pass 
        # args withot the quotes.
        try:
            self._printMessage(print, _COLORS.OKGREEN,
                f'running command {args}')

            t0 = time.time()
            subprocess.run(args, cwd=docroot).check_returncode()

            self._printMessage(print, _COLORS.OKGREEN,
                'pass\' compilation time: {:.3f} s'.format(time.time() - t0))

        except subprocess.CalledProcessError:
            self._printMessage(sys.exit, _COLORS.FAIL,
                f'fatal:\n'
                f'build recipe {args} ended with non-zero code... termination'
            )

    def _copyPDF(self, src_dir: str, dst_dir: str, docname: str):
        if not os.path.exists(src_dir):
            self._printMessage(sys.exit, _COLORS.FAIL,
                f'source pdf directory not exists: "{src_dir}"'
            )

        src = PathWorks.JoinPath(src_dir, docname + '.pdf')
        dst = PathWorks.JoinPath(dst_dir, docname + '.pdf')
        if not os.path.exists(src):
            self._printMessage(sys.exit, _COLORS.FAIL,
                f'source pdf directory exists: "{src}"'
            )

        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        shutil.copyfile(src, dst)

        if os.path.exists(dst):
            self._printMessage(print, _COLORS.OKGREEN,
                f'final pdf is copied to: "{dst}"'
            )
        else:
            self._printMessage(sys.exit, _COLORS.FAIL,
                f'failed to copy pdf from "{src}" to "{dst}"'
            )

    @staticmethod
    def _printMessage(func, color: Any, *pattern: str) -> None:
        func(f'\n\n{color} == {"".join(pattern)}{_COLORS.ENDC}\n\n')
