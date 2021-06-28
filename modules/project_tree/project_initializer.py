from __future__ import annotations
from ..includes import FTexworksConfig, JoinPath
from .project_scanner import FDocumentInfo
from .generators.autogen.generator import AutogenGenerator

import os



class ProjectInitializer:
    
    def __init__(self, conf: FTexworksConfig) -> None:
        self._conf    = conf
        self._autogen = AutogenGenerator()


    def InitProject(self, docInfo: FDocumentInfo) -> None:
        self._initBuildDirectories(docInfo)


    # protected:

    # _initBuildDirectories creates all required project files:
    #   - mirror section roots to a build directory
    #   - create section autogen files
    def _initBuildDirectories(self, docInfo: FDocumentInfo) -> None:
        # >> to prevent a number of LaTeX error 
        # section build directory must be created 
        # by-hands before LaTeX compile start
        self._mirrorSectionRoots(docInfo)

        # >> create autogen files.
        # This method creates files with basic variables.
        # Diffrent modules can update the file with use of special instruments
        self._generateAutogens(docInfo)


    def _mirrorSectionRoots(self, docInfo: FDocumentInfo) -> None:
        buildRoot = self._getBuildRoot(docInfo)

        for sectionInfo in docInfo.sectins.values():
            builddir = JoinPath([buildRoot, sectionInfo.dpath])

            # check if build directory already exists
            if (os.path.exists(builddir)):
                if (os.path.isdir(builddir)):
                    continue
                raise RuntimeError(f'build path {builddir} must be a directory')
            
            # create the directory
            print(f'creating a section build directory... "{builddir}"... ', end = '')

            os.makedirs(builddir)
            
            print('done')
    

    def _generateAutogens(self, docInfo: FDocumentInfo) -> None:
        buildRoot = self._getBuildRoot(docInfo)

        for sectionInfo in docInfo.sectins.values():
            outpath = JoinPath([buildRoot, sectionInfo.dpath, 'autogen.tex'])

            print(f'generating autogen file {outpath}... ', end='')

            self._autogen.Generate(sectionInfo, outpath)

            print('done')
        

    def _getBuildRoot(self, docInfo: FDocumentInfo) -> str:
        return JoinPath([docInfo.path, self._conf.build_dir])
