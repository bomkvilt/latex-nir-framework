from __future__ import annotations
from ..includes import FTexworksConfig, PathWorks
from .classes.document_strcuture import FRootNode
from .generators.autogen.generator import AutogenGenerator

import os



class ProjectInitializer:
    
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf    = conf
        self._autogen = AutogenGenerator()

    def InitProject(self, root: FRootNode) -> None:
        self._initBuildDirectories(root)

    # protected:

    def _initBuildDirectories(self, root: FRootNode) -> None:
        # >> to prevent a number of LaTeX error 
        # section build directory must be created 
        # by-hands before LaTeX compile start
        self._createSectionBuildRoot(root)
        # >> create autogen files.
        # This method creates files with basic variables.
        # Diffrent modules can update the file with use of special instruments
        self._generateAutogens(root)

    def _createSectionBuildRoot(self, root: FRootNode) -> None:
        buildRoot = self._conf.GetBuildRoot()
        for secnode in root.children.values():
            builddir = PathWorks.JoinPath(buildRoot, secnode.rpath)
            # check if build directory already exists
            self._checkBuildDir(builddir)
            # create the directory
            print(f'creating a section build directory... "{builddir}"... ', end = '')
            os.makedirs(builddir, exist_ok = True)
            print('done')
    
    def _generateAutogens(self, root: FRootNode) -> None:
        buildRoot = self._conf.GetBuildRoot()
        for secnode in root.children.values():
            outpath = PathWorks.JoinPath(buildRoot, secnode.rpath, 'autogen.tex')
            # render template
            print(f'generating an autogen file {outpath}... ', end='')
            self._autogen.Generate(secnode, outpath)
            print('done')

    def _checkBuildDir(self, builddir: str) -> None:
        if (os.path.exists(builddir) and not os.path.isdir(builddir)):
            raise RuntimeError(f'build path {builddir} must be a directory')
